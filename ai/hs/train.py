"""
학습 루프 (한 epoch 실행 + 전체 학습 오케스트레이션).
실제 학습 반복문을 담당한다.

- best_epoch 선정 기준: val_loss가 아니라 val Macro F1이 가장 높은 시점.
  val이 원본 클래스 비율 그대로(none 85%)라, val_loss만 보면 다수 클래스
  위주로 편향된 시점이 "best"로 뽑히는 문제가 있었음 (real_holdout_100 같은
  클래스 균형 테스트에서 성능이 떨어지는 원인). Macro F1은 클래스를 동등하게
  취급하므로 이 편향을 줄여줌.
- Early Stopping: val Macro F1이 EARLY_STOPPING_PATIENCE(config.py) epoch
  연속으로 최고치를 못 넘으면 학습을 그 시점에서 멈춘다 (설정한 epoch 수를
  다 안 돌 수 있음).
"""
import numpy as np
import torch
import torch.nn as nn

import config


def run_epoch(model, loader, device, criterion, optimizer, train_mode, collect_preds=False):
    if train_mode:
        model.train()
    else:
        model.eval()

    loss_sum, correct, total = 0.0, 0, 0
    all_preds, all_labels = [], []
    context = torch.enable_grad() if train_mode else torch.no_grad()
    with context:
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)

            if train_mode:
                optimizer.zero_grad()

            out = model(xb)
            loss = criterion(out, yb)

            if train_mode:
                loss.backward()
                optimizer.step()

            loss_sum += loss.item() * xb.size(0)
            pred = out.argmax(dim=1)
            correct += (pred == yb).sum().item()
            total += yb.size(0)

            if collect_preds:
                all_preds.extend(pred.cpu().numpy())
                all_labels.extend(yb.cpu().numpy())

    avg_loss, acc = loss_sum / total, correct / total
    if collect_preds:
        return avg_loss, acc, np.array(all_preds), np.array(all_labels)
    return avg_loss, acc


def compute_macro_f1_quiet(preds, labels, num_classes):
    """evaluate.py의 compute_confusion_and_metrics와 같은 계산식이지만,
    매 epoch마다 부르는 용도라 print 없이 숫자만 반환."""
    f1s = np.zeros(num_classes)
    for c in range(num_classes):
        tp = np.sum((preds == c) & (labels == c))
        fp = np.sum((preds == c) & (labels != c))
        fn = np.sum((preds != c) & (labels == c))
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1s[c] = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return f1s.mean()


def train_model(model, train_loader, val_loader, device, class_weights_tensor,
                 epochs=config.EPOCHS, lr=config.LR):
    """
    전체 학습 실행. 반환: (history, best_epoch, best_state_dict)
    model은 학습이 끝나면 best_state_dict가 이미 load된 상태로 반환됨.
    best_epoch은 val Macro F1이 가장 높은 시점 기준으로 선정.
    """
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=config.WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    num_classes = len(class_weights_tensor)

    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': [], 'val_macro_f1': []}
    best_val_macro_f1 = -1.0
    best_epoch = -1
    best_state_dict = None
    no_improve_count = 0  # Early Stopping: 연속 미개선 횟수 추적

    print("\n=== 9. 학습 시작 ===")
    for epoch in range(1, epochs + 1):
        train_loss, train_acc = run_epoch(model, train_loader, device, criterion, optimizer, train_mode=True)
        val_loss, val_acc, val_preds, val_labels = run_epoch(
            model, val_loader, device, criterion, optimizer, train_mode=False, collect_preds=True
        )
        val_macro_f1 = compute_macro_f1_quiet(val_preds, val_labels, num_classes)
        scheduler.step()

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['val_macro_f1'].append(val_macro_f1)

        is_best = val_macro_f1 > best_val_macro_f1
        if is_best:
            best_val_macro_f1 = val_macro_f1
            best_epoch = epoch
            best_state_dict = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            no_improve_count = 0
        else:
            no_improve_count += 1

        marker = " <- best" if is_best else ""
        print(f"[Epoch {epoch:02d}/{epochs}] "
              f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.4f} val_macro_f1={val_macro_f1:.4f}{marker}")

        if device.type == 'cuda' and epoch == 1:
            print(f"   (GPU 메모리 - 할당: {torch.cuda.memory_allocated()/1024**2:.1f}MB, "
                  f"예약: {torch.cuda.memory_reserved()/1024**2:.1f}MB)")

        if no_improve_count >= config.EARLY_STOPPING_PATIENCE:
            print(f"-> val_macro_f1이 {config.EARLY_STOPPING_PATIENCE}epoch 연속 개선 없음 "
                  f"-> {epoch} epoch에서 조기 종료 (설정한 {epochs} epoch 다 안 돌고 멈춤)")
            break

    print(f"\n-> 최적 epoch: {best_epoch} (val_macro_f1={best_val_macro_f1:.4f}, "
          f"기준: val Macro F1 최고 시점)")
    print(f"-> 이후 테스트 평가 및 모델 저장은 epoch {best_epoch} 시점 가중치로 진행")
    model.load_state_dict(best_state_dict)

    return history, best_epoch, best_state_dict
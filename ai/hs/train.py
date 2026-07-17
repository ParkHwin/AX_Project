"""
학습 루프 (한 epoch 실행 + 전체 학습 오케스트레이션).
"""
import torch
import torch.nn as nn

import config


def run_epoch(model, loader, device, criterion, optimizer, train_mode):
    if train_mode:
        model.train()
    else:
        model.eval()

    loss_sum, correct, total = 0.0, 0, 0
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
            correct += (out.argmax(dim=1) == yb).sum().item()
            total += yb.size(0)

    return loss_sum / total, correct / total


def train_model(model, train_loader, val_loader, device, class_weights_tensor,
                 epochs=config.EPOCHS, lr=config.LR):
    """
    전체 학습 실행. 반환: (history, best_epoch, best_state_dict)
    model은 학습이 끝나면 best_state_dict가 이미 load된 상태로 반환됨.
    """
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=config.WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    best_val_loss = float('inf')
    best_epoch = -1
    best_state_dict = None

    print("\n=== 9. 학습 시작 ===")
    for epoch in range(1, epochs + 1):
        train_loss, train_acc = run_epoch(model, train_loader, device, criterion, optimizer, train_mode=True)
        val_loss, val_acc = run_epoch(model, val_loader, device, criterion, optimizer, train_mode=False)
        scheduler.step()

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        is_best = val_loss < best_val_loss
        if is_best:
            best_val_loss = val_loss
            best_epoch = epoch
            best_state_dict = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

        marker = " <- best" if is_best else ""
        print(f"[Epoch {epoch:02d}/{epochs}] "
              f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}{marker}")

        if device.type == 'cuda' and epoch == 1:
            print(f"   (GPU 메모리 - 할당: {torch.cuda.memory_allocated()/1024**2:.1f}MB, "
                  f"예약: {torch.cuda.memory_reserved()/1024**2:.1f}MB)")

    print(f"\n-> Early stopping 기준 최적 epoch: {best_epoch} (val_loss={best_val_loss:.4f})")
    print(f"-> 이후 테스트 평가 및 모델 저장은 epoch {best_epoch} 시점 가중치로 진행")
    model.load_state_dict(best_state_dict)

    return history, best_epoch, best_state_dict
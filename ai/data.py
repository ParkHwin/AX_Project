import pandas as pd
import numpy as np
import cv2
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    # =========================================================
    # 1. 데이터 로드 및 정제  (수정 없음)
    # =========================================================
    print("=== 1. 데이터 로드 및 정제 ===")
    data = pd.read_pickle('LSWMD.pkl')

    def get_exact_label(label):
        if isinstance(label, (list, np.ndarray)) and len(label) > 0:
            val = label[0][0] if isinstance(label[0], (list, np.ndarray)) else label[0]
            return str(val)
        return 'unlabeled'

    data['clean_label'] = data['failureType'].apply(get_exact_label)
    labeled_data = data[data['clean_label'] != 'unlabeled'].copy()
    print(f"-> 유효 데이터 {len(labeled_data)}개 추출 완료.")

    # =========================================================
    # 2. 리사이징 및 라벨 인코딩  (수정 없음)
    # =========================================================
    print("\n=== 2. 리사이징 및 라벨 인코딩 ===")
    TARGET_SIZE = (64, 64)

    def resize_for_dl(img_array):
        img_array = np.asarray(img_array)
        if img_array.dtype not in (np.uint8, np.float32):
            img_array = img_array.astype(np.uint8)
        return cv2.resize(img_array, dsize=TARGET_SIZE, interpolation=cv2.INTER_NEAREST)

    labeled_data['waferMap_resized'] = labeled_data['waferMap'].apply(resize_for_dl)

    le = LabelEncoder()
    labeled_data['encoded_label'] = le.fit_transform(labeled_data['clean_label'])
    label_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
    print(f"-> 라벨 매핑 정보: {label_mapping}")

    # =========================================================
    # 3. Train/Test 먼저 분할 (증강 전 분할 -> 누수 방지)  (수정 없음)
    # =========================================================
    print("\n=== 3. Train/Test 분할 (증강 이전) ===")
    y_raw = labeled_data['encoded_label'].values

    train_idx, test_idx = train_test_split(
        np.arange(len(labeled_data)),
        test_size=0.2, random_state=42, stratify=y_raw
    )

    train_df = labeled_data.iloc[train_idx].reset_index(drop=True)
    test_df = labeled_data.iloc[test_idx].reset_index(drop=True)
    print(f"-> train {len(train_df)}개 / test {len(test_df)}개 (분할 시점, 증강 전)")

    # =========================================================
    # 4. 불균형 해소 (train_df에만 적용)  (수정 없음)
    # =========================================================
    print("\n=== 4. 클래스 불균형 해소 (train 데이터에만 적용) ===")
    NORMAL_TARGET = 10000 # 정상 클래스는 1만장으로 제한
    DEFECT_TARGET = 5000 # 결함 종류별로 5천장
    MAX_AUGMENT_RATIO = 5

    def apply_advanced_augmentation(img_array):
        img = img_array.copy()
        if np.random.rand() > 0.5:
            img = np.fliplr(img)
        if np.random.rand() > 0.5:
            img = np.flipud(img)
        k = np.random.randint(0, 4)
        if k > 0:
            img = np.rot90(img, k=k)
        if np.random.rand() > 0.5:
            rows, cols = img.shape
            tx = np.random.randint(-cols // 10, cols // 10)
            ty = np.random.randint(-rows // 10, rows // 10)
            M = np.float32([[1, 0, tx], [0, 1, ty]])
            img = cv2.warpAffine(
                np.ascontiguousarray(img, dtype=np.uint8), M, (cols, rows),
                flags=cv2.INTER_NEAREST, borderValue=0
            )
        return img

    def balance_defect_class(df, target_count, max_augment_ratio=None):
        if df is None or len(df) == 0:
            return pd.DataFrame(columns=train_df.columns)

        current_count = len(df)

        if current_count >= target_count:
            return df.sample(n=target_count, random_state=42)

        effective_target = target_count
        if max_augment_ratio is not None:
            capped_target = current_count * (1 + max_augment_ratio)
            if capped_target < target_count:
                effective_target = capped_target

        needed = effective_target - current_count
        if needed <= 0:
            return df

        samples = df.sample(n=needed, replace=True, random_state=42).copy()
        samples['waferMap_resized'] = samples['waferMap_resized'].apply(apply_advanced_augmentation)
        return pd.concat([df, samples], ignore_index=True)

    labels_of_interest = ['none', 'Center', 'Donut', 'Edge-Ring', 'Edge-Loc',
                           'Loc', 'Random', 'Scratch', 'Near-full']

    balanced_parts = []
    for lbl in labels_of_interest:
        subset = train_df[train_df['clean_label'] == lbl].copy()
        target = NORMAL_TARGET if lbl == 'none' else DEFECT_TARGET

        if lbl == 'none' and len(subset) > NORMAL_TARGET:
            balanced_parts.append(subset.sample(n=NORMAL_TARGET, random_state=42))
        elif lbl == 'Near-full':
            result = balance_defect_class(subset, target, max_augment_ratio=MAX_AUGMENT_RATIO)
            print(f"   -> Near-full: 원본 {len(subset)}개 -> 최종 {len(result)}개 "
                  f"(비율 상한 {MAX_AUGMENT_RATIO}배 적용)")
            balanced_parts.append(result)
        else:
            balanced_parts.append(balance_defect_class(subset, target))

    final_train_df = pd.concat(balanced_parts, ignore_index=True)
    final_train_df = final_train_df.sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"-> 최종 train {len(final_train_df)}개 (분포: {final_train_df['clean_label'].value_counts().to_dict()})")
    print(f"-> test는 증강 없이 원본 그대로 {len(test_df)}개 유지")

    # =========================================================
    # 5. 텐서 변환  (수정 없음, 단 train을 다시 train/val로 나눔은 아래 6번에서)
    # =========================================================
    print("\n=== 5. 텐서 변환 ===")
    X_train_full = np.stack(final_train_df['waferMap_resized'].values)
    X_train_full = np.expand_dims(X_train_full, axis=-1)
    y_train_full = final_train_df['encoded_label'].values

    X_test = np.stack(test_df['waferMap_resized'].values)
    X_test = np.expand_dims(X_test, axis=-1)
    y_test = test_df['encoded_label'].values

    print(f"X_train_full: {X_train_full.shape}, y_train_full: {y_train_full.shape}")
    print(f"X_test      : {X_test.shape}, y_test      : {y_test.shape}")

    NUM_CLASSES = len(label_mapping)
    reverse_label_mapping = {v: k for k, v in label_mapping.items()}

    # =========================================================
    # 6. Train -> Train/Val 분리 (test는 최종 holdout으로만 사용)
    # =========================================================
    print("\n=== 6. Train -> Train/Val 분리 ===")
    # 지금까지 test set을 매 epoch 검증에 써왔는데, 이러면 test가 사실상 검증용으로
    # 소모돼 최종 성능 지표로서의 신뢰도가 떨어짐. final_train_df를 다시 나눠
    # 진짜 검증셋을 만들고, test는 학습 종료 후 딱 한 번만 사용.
    tr_idx, val_idx = train_test_split(
        np.arange(len(y_train_full)),
        test_size=0.1, random_state=42, stratify=y_train_full
    )
    X_train, y_train = X_train_full[tr_idx], y_train_full[tr_idx]
    X_val, y_val = X_train_full[val_idx], y_train_full[val_idx]
    print(f"-> train {len(y_train)}개 / val {len(y_val)}개 (train 내부 분리, test는 미접촉 유지)")

    # =========================================================
    # 7. Dataset / DataLoader
    # =========================================================
    class WaferDataset(Dataset):
        def __init__(self, X, y):
            self.X = torch.tensor(X, dtype=torch.float32).permute(0, 3, 1, 2) / 255.0
            self.y = torch.tensor(y, dtype=torch.long)

        def __len__(self):
            return len(self.y)

        def __getitem__(self, idx):
            return self.X[idx], self.y[idx]

    BATCH_SIZE = 64
    NUM_WORKERS = 0  # Windows spawn 이슈 회피

    train_dataset = WaferDataset(X_train, y_train)
    val_dataset = WaferDataset(X_val, y_val)
    test_dataset = WaferDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)

    # =========================================================
    # 8. Class Weight 계산 (none -> Loc/Edge-Loc/Scratch 오분류 완화 목적)
    # =========================================================
    print("\n=== 7. Class Weight 계산 ===")
    # 실제 confusion matrix 분석 결과: none의 절대 규모(다수 클래스) 때문에
    # 소수 클래스(Loc, Edge-Loc, Scratch)의 Precision이 크게 훼손됨.
    # 역빈도 가중치를 줘서 손실 함수가 소수 클래스 오분류에 더 민감하게 반응하도록 함.
    class_counts = np.bincount(y_train, minlength=NUM_CLASSES)
    class_weights = 1.0 / np.sqrt(class_counts + 1e-6)  # sqrt로 완화 (선형 역빈도는 과교정 위험)
    class_weights = class_weights / class_weights.sum() * NUM_CLASSES  # 평균 1 근처로 정규화
    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32)

    print(f"{'클래스':<12}{'학습 샘플 수':<14}{'가중치':<10}")
    for c in range(NUM_CLASSES):
        print(f"{reverse_label_mapping[c]:<12}{class_counts[c]:<14}{class_weights[c]:<10.4f}")

    # =========================================================
    # 9. ResNet9 (fast.ai 스타일, from scratch, 1채널 64x64 대응)
    # =========================================================
    def conv_block(in_ch, out_ch, pool=False):
        layers = [
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        ]
        if pool:
            layers.append(nn.MaxPool2d(2))
        return nn.Sequential(*layers)

    class ResidualBlock(nn.Module):
        def __init__(self, channels):
            super().__init__()
            self.conv1 = conv_block(channels, channels)
            self.conv2 = conv_block(channels, channels)

        def forward(self, x):
            out = self.conv1(x)
            out = self.conv2(out)
            return out + x

    class ResNet9(nn.Module):
        def __init__(self, num_classes):
            super().__init__()
            self.stem = conv_block(1, 64)
            self.layer1 = conv_block(64, 128, pool=True)
            self.res1 = ResidualBlock(128)

            self.layer2 = conv_block(128, 256, pool=True)
            self.layer3 = conv_block(256, 512, pool=True)
            self.res2 = ResidualBlock(512)

            self.pool = nn.AdaptiveAvgPool2d(1)
            self.fc = nn.Linear(512, num_classes)

        def forward(self, x):
            x = self.stem(x)
            x = self.layer1(x)
            x = self.res1(x)
            x = self.layer2(x)
            x = self.layer3(x)
            x = self.res2(x)
            x = self.pool(x)
            x = torch.flatten(x, 1)
            return self.fc(x)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n=== 8. 학습 디바이스: {device} ===")

    model = ResNet9(NUM_CLASSES).to(device)
    class_weights_tensor = class_weights_tensor.to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"-> 모델 파라미터 수: {total_params:,}")

    # =========================================================
    # 10. 학습 루프 (train + val, 매 epoch 기록)
    # =========================================================
    EPOCHS = 20
    LR = 1e-3

    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    def run_epoch(loader, train_mode):
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

    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    print("\n=== 9. 학습 시작 ===")
    for epoch in range(1, EPOCHS + 1):
        train_loss, train_acc = run_epoch(train_loader, train_mode=True)
        val_loss, val_acc = run_epoch(val_loader, train_mode=False)
        scheduler.step()

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        print(f"[Epoch {epoch:02d}/{EPOCHS}] "
              f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}")

        if device.type == 'cuda' and epoch == 1:
            print(f"   (GPU 메모리 - 할당: {torch.cuda.memory_allocated()/1024**2:.1f}MB, "
                  f"예약: {torch.cuda.memory_reserved()/1024**2:.1f}MB)")

    # =========================================================
    # 11. 학습/검증 곡선 그래프
    # =========================================================
    print("\n=== 10. 학습/검증 곡선 저장 ===")
    epochs_range = range(1, EPOCHS + 1)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(epochs_range, history['train_loss'], label='Train Loss', marker='o')
    axes[0].plot(epochs_range, history['val_loss'], label='Val Loss', marker='s')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Train vs Val Loss')
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot(epochs_range, history['train_acc'], label='Train Acc', marker='o')
    axes[1].plot(epochs_range, history['val_acc'], label='Val Acc', marker='s')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title('Train vs Val Accuracy')
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('training_curves.png', dpi=100)
    plt.close()
    print("-> training_curves.png 저장 완료")

    # =========================================================
    # 12. 최종 테스트 평가 (학습 끝난 후 딱 한 번만 접촉하는 진짜 holdout)
    # =========================================================
    print("\n=== 11. 최종 테스트 평가 (test set, 최초 접촉) ===")
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for xb, yb in test_loader:
            xb = xb.to(device)
            out = model(xb)
            pred = out.argmax(dim=1).cpu().numpy()
            all_preds.extend(pred)
            all_labels.extend(yb.numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    conf_matrix = np.zeros((NUM_CLASSES, NUM_CLASSES), dtype=int)
    for t, p in zip(all_labels, all_preds):
        conf_matrix[t, p] += 1

    print("Confusion Matrix (행: 실제, 열: 예측)")
    print(conf_matrix)

    per_class_precision = np.zeros(NUM_CLASSES)
    per_class_recall = np.zeros(NUM_CLASSES)
    per_class_f1 = np.zeros(NUM_CLASSES)

    print(f"\n{'클래스':<12}{'Precision':<12}{'Recall':<12}{'F1':<12}")
    for c in range(NUM_CLASSES):
        tp = conf_matrix[c, c]
        fp = conf_matrix[:, c].sum() - tp
        fn = conf_matrix[c, :].sum() - tp
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        per_class_precision[c] = precision
        per_class_recall[c] = recall
        per_class_f1[c] = f1

        print(f"{reverse_label_mapping[c]:<12}{precision:<12.4f}{recall:<12.4f}{f1:<12.4f}")

    overall_acc = (all_preds == all_labels).mean()
    macro_f1 = per_class_f1.mean()
    print(f"\n전체 정확도(micro): {overall_acc:.4f}")
    print(f"Macro F1 (클래스별 단순 평균, 다수 클래스 가중치 없음): {macro_f1:.4f}")

    # =========================================================
    # 13. 컨퓨전 매트릭스 히트맵 + 클래스별 지표 바 차트
    # =========================================================
    print("\n=== 12. 평가 그래프 저장 ===")
    class_names = [reverse_label_mapping[c] for c in range(NUM_CLASSES)]

    # 정규화된 confusion matrix (행 기준 비율) - 클래스별 규모 차이가 커서 원본 숫자만 보면
    # none의 절대값에 다른 클래스가 묻혀 보이지 않음
    conf_matrix_norm = conf_matrix.astype(float) / conf_matrix.sum(axis=1, keepdims=True)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    im = axes[0].imshow(conf_matrix_norm, cmap='Blues', vmin=0, vmax=1)
    axes[0].set_xticks(range(NUM_CLASSES))
    axes[0].set_yticks(range(NUM_CLASSES))
    axes[0].set_xticklabels(class_names, rotation=45, ha='right')
    axes[0].set_yticklabels(class_names)
    axes[0].set_xlabel('예측 라벨')
    axes[0].set_ylabel('실제 라벨')
    axes[0].set_title('Confusion Matrix (행 기준 정규화)')
    for i in range(NUM_CLASSES):
        for j in range(NUM_CLASSES):
            val = conf_matrix_norm[i, j]
            color = 'white' if val > 0.5 else 'black'
            axes[0].text(j, i, f"{val:.2f}", ha='center', va='center', color=color, fontsize=8)
    fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)

    x_pos = np.arange(NUM_CLASSES)
    width = 0.25
    axes[1].bar(x_pos - width, per_class_precision, width, label='Precision')
    axes[1].bar(x_pos, per_class_recall, width, label='Recall')
    axes[1].bar(x_pos + width, per_class_f1, width, label='F1')
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(class_names, rotation=45, ha='right')
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title('클래스별 Precision / Recall / F1')
    axes[1].legend()
    axes[1].grid(alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('test_evaluation.png', dpi=100)
    plt.close()
    print("-> test_evaluation.png 저장 완료")

    torch.save(model.state_dict(), 'resnet9_wafer.pth')
    print("-> 모델 저장 완료: resnet9_wafer.pth")


if __name__ == '__main__':
    main()
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
import warnings
import random

# Windows 기준 한글 폰트 설정 (맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 폰트에 한글 glyph가 없을 때 뜨는 경고를 메시지 내용 기준으로 확실히 차단
# (module= 필터는 하위 모듈에서 발생 시 안 걸릴 수 있어 message 정규식으로 대체)
warnings.filterwarnings('ignore', message='Glyph .* missing from font')


def main():
    # ---- 시드 고정: 매번 같은 결과가 재현되도록 (모델 초기화, 증강, 배치 셔플 등) ----
    SEED = 42
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.benchmark = True  # 속도 우선: cudnn이 레이어 크기에 맞는 최적 알고리즘을
                                            # 자동 탐색하도록 허용 (완벽한 재현성은 약간 희생)

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
    TARGET_SIZE = (64, 64)  # 32 실험 결과 Macro F1 0.8522->0.7967로 뚜렷한 하락 확인, 64로 확정

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
        test_size=0.2, random_state=SEED, stratify=y_raw
    )

    train_df = labeled_data.iloc[train_idx].reset_index(drop=True)
    test_df = labeled_data.iloc[test_idx].reset_index(drop=True)
    print(f"-> train {len(train_df)}개 / test {len(test_df)}개 (분할 시점, 증강 전)")

    # =========================================================
    # 4. 불균형 해소 (train_df에만 적용)  (수정 없음)
    # =========================================================
    print("\n=== 4. 클래스 불균형 해소 (train 데이터에만 적용) ===")
    NORMAL_TARGET = 10000
    DEFECT_TARGET = 5000
    MAX_AUGMENT_RATIO = 5

    def compute_density(img):
        # waferMap 값: 0=웨이퍼 밖, 1=정상 다이, 2=불량 다이
        # 밀도 = 불량 다이 수 / (정상+불량 다이 수), 웨이퍼 밖은 분모에서 제외
        # (12-2 섹션의 오분류 vs 정분류 밀도 비교 분석에서 사용)
        valid = img[img > 0]
        if len(valid) == 0:
            return 0.0
        return (valid == 2).sum() / len(valid)

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
            return df.sample(n=target_count, random_state=SEED)

        effective_target = target_count
        if max_augment_ratio is not None:
            capped_target = current_count * (1 + max_augment_ratio)
            if capped_target < target_count:
                effective_target = capped_target

        needed = effective_target - current_count
        if needed <= 0:
            return df

        samples = df.sample(n=needed, replace=True, random_state=SEED).copy()
        samples['waferMap_resized'] = samples['waferMap_resized'].apply(apply_advanced_augmentation)
        return pd.concat([df, samples], ignore_index=True)

    labels_of_interest = ['none', 'Center', 'Donut', 'Edge-Ring', 'Edge-Loc',
                           'Loc', 'Random', 'Scratch', 'Near-full']

    balanced_parts = []
    for lbl in labels_of_interest:
        subset = train_df[train_df['clean_label'] == lbl].copy()
        target = NORMAL_TARGET if lbl == 'none' else DEFECT_TARGET

        if lbl == 'none' and len(subset) > NORMAL_TARGET:
            balanced_parts.append(subset.sample(n=NORMAL_TARGET, random_state=SEED))
        elif lbl == 'Near-full':
            result = balance_defect_class(subset, target, max_augment_ratio=MAX_AUGMENT_RATIO)
            print(f"   -> Near-full: 원본 {len(subset)}개 -> 최종 {len(result)}개 "
                  f"(비율 상한 {MAX_AUGMENT_RATIO}배 적용)")
            balanced_parts.append(result)
        else:
            balanced_parts.append(balance_defect_class(subset, target))

    final_train_df = pd.concat(balanced_parts, ignore_index=True)
    final_train_df = final_train_df.sample(frac=1, random_state=SEED).reset_index(drop=True)
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
    tr_idx, val_idx = train_test_split(
        np.arange(len(y_train_full)),
        test_size=0.1, random_state=SEED, stratify=y_train_full
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
    # 8. Class Weight 계산 (재설계: confusion matrix 실측 기반)
    # =========================================================
    print("\n=== 7. Class Weight 계산 (confusion 패턴 기반 재설계) ===")
    class_weights = np.ones(NUM_CLASSES, dtype=np.float64)

    none_idx = label_mapping['none']
    near_full_idx = label_mapping['Near-full']

    class_weights[none_idx] = 2.3    # 실험 결과 최적값 (1.8→2.3 개선, 2.8은 오히려 하락 확인됨)
    class_weights[near_full_idx] = 1.5  # 절대 샘플 수 희소성 보완

    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32)

    print(f"{'클래스':<12}{'가중치':<10}{'비고'}")
    for c in range(NUM_CLASSES):
        note = ""
        if c == none_idx:
            note = "<- 상향 (오분류 민감도 증가)"
        elif c == near_full_idx:
            note = "<- 상향 (절대 샘플 희소)"
        print(f"{reverse_label_mapping[c]:<12}{class_weights[c]:<10.4f}{note}")

    # =========================================================
    # 9. ResNet9 (fast.ai 스타일, from scratch, 1채널 64x64 대응)
    # =========================================================
    def conv_block(in_ch, out_ch, pool=False, dropout_p=0.0):
        layers = [
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        ]
        if pool:
            layers.append(nn.MaxPool2d(2))
        if dropout_p > 0:
            layers.append(nn.Dropout2d(dropout_p))
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

            self.layer2 = conv_block(128, 256, pool=True, dropout_p=0.2)
            self.res_mid = ResidualBlock(256)  # 추가: 128/512에만 있던 residual block을
                                                # 국소 패턴(Loc/Scratch/Edge-Loc) 관련 중간
                                                # 채널 단계(256)에도 배치해보는 실험
            self.layer3 = conv_block(256, 512, pool=True, dropout_p=0.2)
            self.res2 = ResidualBlock(512)

            self.pool = nn.AdaptiveAvgPool2d(1)
            self.dropout = nn.Dropout(0.4)
            self.fc = nn.Linear(512, num_classes)

        def forward(self, x):
            x = self.stem(x)
            x = self.layer1(x)
            x = self.res1(x)
            x = self.layer2(x)
            x = self.res_mid(x)
            x = self.layer3(x)
            x = self.res2(x)
            x = self.pool(x)
            x = torch.flatten(x, 1)
            x = self.dropout(x)
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
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
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

    best_val_loss = float('inf')
    best_epoch = -1
    best_state_dict = None

    print("\n=== 9. 학습 시작 ===")
    for epoch in range(1, EPOCHS + 1):
        train_loss, train_acc = run_epoch(train_loader, train_mode=True)
        val_loss, val_acc = run_epoch(val_loader, train_mode=False)
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
        print(f"[Epoch {epoch:02d}/{EPOCHS}] "
              f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}{marker}")

        if device.type == 'cuda' and epoch == 1:
            print(f"   (GPU 메모리 - 할당: {torch.cuda.memory_allocated()/1024**2:.1f}MB, "
                  f"예약: {torch.cuda.memory_reserved()/1024**2:.1f}MB)")

    print(f"\n-> Early stopping 기준 최적 epoch: {best_epoch} (val_loss={best_val_loss:.4f})")
    print(f"-> 이후 테스트 평가 및 모델 저장은 epoch {best_epoch} 시점 가중치로 진행")
    model.load_state_dict(best_state_dict)

    # =========================================================
    # 11. 학습/검증 곡선 그래프
    # =========================================================
    print("\n=== 10. 학습/검증 곡선 저장 ===")
    epochs_range = range(1, EPOCHS + 1)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(epochs_range, history['train_loss'], label='Train Loss', marker='o')
    axes[0].plot(epochs_range, history['val_loss'], label='Val Loss', marker='s')
    axes[0].axvline(x=best_epoch, color='green', linestyle='--', alpha=0.7,
                     label=f'Best Epoch ({best_epoch})')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Train vs Val Loss')
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot(epochs_range, history['train_acc'], label='Train Acc', marker='o')
    axes[1].plot(epochs_range, history['val_acc'], label='Val Acc', marker='s')
    axes[1].axvline(x=best_epoch, color='green', linestyle='--', alpha=0.7,
                     label=f'Best Epoch ({best_epoch})')
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
    # 12-1. none -> Loc/Scratch/Edge-Loc 오분류 샘플 시각화
    # =========================================================
    print("\n=== 11-1. none 오분류 샘플 확인 ===")
    target_confusions = ['Loc', 'Scratch', 'Edge-Loc']
    none_true_mask = (all_labels == none_idx)

    fig, axes = plt.subplots(len(target_confusions), 6, figsize=(18, 9))
    for row, target_name in enumerate(target_confusions):
        target_class_idx = label_mapping[target_name]
        mis_mask = none_true_mask & (all_preds == target_class_idx)
        mis_indices = np.where(mis_mask)[0]
        print(f"-> none을 {target_name}(으)로 오분류: {len(mis_indices)}건")

        n_show = min(6, len(mis_indices))
        for col in range(6):
            ax = axes[row, col]
            if col < n_show:
                idx = mis_indices[col]
                img = test_df.iloc[idx]['waferMap_resized']
                ax.imshow(img, cmap='inferno')
                ax.set_title(f"실제:none\n예측:{target_name}", fontsize=9)
            ax.axis('off')

    plt.suptitle('none이 오분류된 실제 웨이퍼 이미지 (각 행: 오분류 대상 클래스)', fontsize=13)
    plt.tight_layout()
    plt.savefig('none_misclassified_samples.png', dpi=100)
    plt.close()
    print("-> none_misclassified_samples.png 저장 완료")

    # =========================================================
    # 12-2. none 오분류 vs 정분류 샘플의 불량 다이 밀도 비교
    # =========================================================
    # waferMap 값: 0=웨이퍼 밖, 1=정상 다이, 2=불량 다이.
    # 밀도 = 불량 다이 수 / (정상+불량 다이 수) -> 웨이퍼 밖 영역은 분모에서 제외해야
    # 웨이퍼 크기 차이에 영향을 안 받음.
    # 목적: "none으로 오분류되는 샘플이 실제로 더 지저분한(밀도 높은) 웨이퍼인지"를
    # 정량적으로 확인 -> 라벨링 경계 사례 가설을 숫자로 검증.
    print("\n=== 12-2. none 오분류 vs 정분류 밀도 비교 ===")

    misclassified_idx = np.where(none_true_mask & np.isin(all_preds, [label_mapping[t] for t in target_confusions]))[0]
    correct_idx = np.where(none_true_mask & (all_preds == none_idx))[0]

    mis_density = np.array([compute_density(test_df.iloc[i]['waferMap_resized']) for i in misclassified_idx])
    correct_density = np.array([compute_density(test_df.iloc[i]['waferMap_resized']) for i in correct_idx])

    print(f"-> 오분류된 none 샘플 ({len(mis_density)}개): 평균 밀도 {mis_density.mean():.4f}, 중앙값 {np.median(mis_density):.4f}")
    print(f"-> 정분류된 none 샘플 ({len(correct_density)}개): 평균 밀도 {correct_density.mean():.4f}, 중앙값 {np.median(correct_density):.4f}")
    print(f"-> 배율: 오분류 그룹이 정분류 그룹보다 평균 밀도 {mis_density.mean() / (correct_density.mean() + 1e-9):.2f}배")

    try:
        from scipy import stats
        stat, pvalue = stats.mannwhitneyu(mis_density, correct_density, alternative='greater')
        print(f"-> Mann-Whitney U 검정 (오분류 밀도 > 정분류 밀도): p-value={pvalue:.6f}")
        print("   (p < 0.05면 두 그룹 밀도 차이가 통계적으로 유의미 -> 라벨 경계 사례 가설 뒷받침)")
    except ImportError:
        print("-> scipy 미설치로 통계 검정은 생략, 평균/중앙값 비교로만 판단")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot([correct_density, mis_density], tick_labels=['정분류 (none)', '오분류 (none->Loc/Scratch/Edge-Loc)'])
    ax.set_ylabel('불량 다이 밀도')
    ax.set_title('none 샘플 밀도 비교: 정분류 vs 오분류')
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('none_density_comparison.png', dpi=100)
    plt.close()
    print("-> none_density_comparison.png 저장 완료")

    # =========================================================
    # 13. 컨퓨전 매트릭스 히트맵 + 클래스별 지표 바 차트
    # =========================================================
    print("\n=== 12. 평가 그래프 저장 ===")
    class_names = [reverse_label_mapping[c] for c in range(NUM_CLASSES)]

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
    print(f"-> 모델 저장 완료: resnet9_wafer.pth (epoch {best_epoch} 기준, early stopping 적용됨)")


if __name__ == '__main__':
    main()
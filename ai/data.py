import pandas as pd
import numpy as np
import cv2
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

print("=== 1. 데이터 로드 및 정제 ===")
# 1.1 데이터 로드
data = pd.read_pickle('LSWMD.pkl')

# 1.2 미라벨링 데이터 제거 및 문자열 정제
def get_exact_label(label):
    if isinstance(label, (list, np.ndarray)) and len(label) > 0:
        val = label[0][0] if isinstance(label[0], (list, np.ndarray)) else label[0]
        return str(val)
    return 'unlabeled'

data['clean_label'] = data['failureType'].apply(get_exact_label)
labeled_data = data[data['clean_label'] != 'unlabeled'].copy()
print(f"-> 유효 데이터 {len(labeled_data)}개 추출 완료.")

print("\n=== 2. 리사이징 및 라벨 인코딩 ===")
TARGET_SIZE = (64, 64)

def resize_for_dl(img_array):
    img_array = np.asarray(img_array)
    # cv2.resize는 float64/객체 배열을 지원하지 않으므로 안전한 dtype으로 변환
    if img_array.dtype not in (np.uint8, np.float32):
        img_array = img_array.astype(np.uint8)
    return cv2.resize(img_array, dsize=TARGET_SIZE, interpolation=cv2.INTER_NEAREST)

labeled_data['waferMap_resized'] = labeled_data['waferMap'].apply(resize_for_dl)

le = LabelEncoder()
labeled_data['encoded_label'] = le.fit_transform(labeled_data['clean_label'])
label_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(f"-> 라벨 매핑 정보: {label_mapping}")

print("\n=== 3. 데이터 증강을 위한 라벨별 분리 ===")
data_none = labeled_data[labeled_data['clean_label'] == 'none'].copy()
data_center = labeled_data[labeled_data['clean_label'] == 'Center'].copy()
data_donut = labeled_data[labeled_data['clean_label'] == 'Donut'].copy()
data_edge_ring = labeled_data[labeled_data['clean_label'] == 'Edge-Ring'].copy()
data_edge_loc = labeled_data[labeled_data['clean_label'] == 'Edge-Loc'].copy()
data_loc = labeled_data[labeled_data['clean_label'] == 'Loc'].copy()
data_random = labeled_data[labeled_data['clean_label'] == 'Random'].copy()
data_scratch = labeled_data[labeled_data['clean_label'] == 'Scratch'].copy()
data_near_full = labeled_data[labeled_data['clean_label'] == 'Near-full'].copy()

print("\n=== 4. 불균형 해소 (증강 및 축소) ===")
NORMAL_TARGET = 10000
DEFECT_TARGET = 5000


def apply_advanced_augmentation(img_array):
    """
    강화된 웨이퍼 맵 데이터 증강 함수
    """
    img = img_array.copy()

    # 1. 반전 (상하/좌우 각각 50% 확률로 독립적 적용)
    if np.random.rand() > 0.5:
        img = np.fliplr(img)  # 좌우 반전
    if np.random.rand() > 0.5:
        img = np.flipud(img)  # 상하 반전

    # 2. 90도 단위 회전 (0, 90, 180, 270도 중 랜덤)
    k = np.random.randint(0, 4)
    if k > 0:
        img = np.rot90(img, k=k)

    # 3. 미세 이동 (Shift) - 50% 확률로 가로세로 최대 10% 이동
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


def balance_defect_class(df, target_count):
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=labeled_data.columns)

    current_count = len(df)

    # 목표치 이상이면 잘라냄 (Undersampling)
    if current_count >= target_count:
        return df.sample(n=target_count, random_state=42)

    # 부족하면 빈 공간만큼 무작위 추출하여 증강 (Augmentation)
    needed = target_count - current_count
    samples = df.sample(n=needed, replace=True, random_state=42).copy()
    samples['waferMap_resized'] = samples['waferMap_resized'].apply(apply_advanced_augmentation)

    # 원본 + 증강 데이터를 합쳐서 target_count개로 맞춤
    return pd.concat([df, samples], ignore_index=True)


print("-> 증강 및 샘플링 진행 중... (시간이 조금 소요될 수 있습니다)")
balanced_none = data_none.sample(n=NORMAL_TARGET, random_state=42) if len(data_none) > NORMAL_TARGET else data_none
balanced_center = balance_defect_class(data_center, DEFECT_TARGET)
balanced_donut = balance_defect_class(data_donut, DEFECT_TARGET)
balanced_edge_ring = balance_defect_class(data_edge_ring, DEFECT_TARGET)
balanced_edge_loc = balance_defect_class(data_edge_loc, DEFECT_TARGET)
balanced_loc = balance_defect_class(data_loc, DEFECT_TARGET)
balanced_random = balance_defect_class(data_random, DEFECT_TARGET)
balanced_scratch = balance_defect_class(data_scratch, DEFECT_TARGET)
balanced_near_full = balance_defect_class(data_near_full, DEFECT_TARGET)

# 통합 및 순서 섞기
final_df = pd.concat([
    balanced_none, balanced_center, balanced_donut, balanced_edge_ring,
    balanced_edge_loc, balanced_loc, balanced_random, balanced_scratch, balanced_near_full
], ignore_index=True)
final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)
print(f"-> 최종 데이터 {len(final_df)}개 (클래스별 분포: {final_df['clean_label'].value_counts().to_dict()})")

print("\n=== 5. 텐서 변환 및 Train/Test 분할 ===")
# 차원 추가 (N, 64, 64, 1)
X_all = np.stack(final_df['waferMap_resized'].values)
X_all = np.expand_dims(X_all, axis=-1)

y_all = final_df['encoded_label'].values

# 학습/검증 데이터 8:2 분할
X_train, X_test, y_train, y_test = train_test_split(
    X_all, y_all, test_size=0.2, random_state=42, stratify=y_all
)

print("-" * 40)
print("[최종 딥러닝 학습 준비 완료!]")
print(f"X_train (학습용 데이터): {X_train.shape}")
print(f"y_train (학습용 정답): {y_train.shape}")
print(f"X_test  (검증용 데이터): {X_test.shape}")
print(f"y_test  (검증용 정답): {y_test.shape}")
print("-" * 40)


import matplotlib
matplotlib.use('Agg')  # 스크립트 실행 환경용 (파일로 저장)
import matplotlib.pyplot as plt

print("=== 🎨 라벨별 대표 웨이퍼 이미지 및 크기 확인 ===")

def format_bytes(n_bytes):
    """바이트 값을 'B / KB / MB' 형태의 문자열로 함께 표시"""
    kb = n_bytes / 1024
    mb = n_bytes / (1024 ** 2)
    return f"{n_bytes:,}B / {kb:,.2f}KB / {mb:,.4f}MB"

reverse_label_mapping = {v: k for k, v in label_mapping.items()}

plt.figure(figsize=(12, 12))

unique_classes = np.unique(y_train)

print(f"{'라벨':<12} {'원본 크기':<12} {'원본 용량 (B / KB / MB)':<32} {'리사이즈 후':<14} {'리사이즈 후 용량 (B / KB / MB)'}")
print("-" * 110)

total_original_bytes = 0
total_resized_bytes = 0

for i, class_num in enumerate(unique_classes):
    indices = np.where(y_train == class_num)[0]
    sample_idx = indices[0]

    label_name = reverse_label_mapping[class_num]

    # 리사이즈 후 텐서 크기 및 용량 (모델에 실제로 들어가는 크기)
    img_tensor = X_train[sample_idx]
    resized_shape = img_tensor.shape
    resized_bytes = img_tensor.nbytes
    img_2d = img_tensor.squeeze()

    # 같은 라벨을 가진 원본(리사이즈 전) 웨이퍼맵 크기 및 용량
    original_img = final_df[final_df['clean_label'] == label_name]['waferMap'].iloc[0]
    original_shape = original_img.shape
    original_bytes = original_img.nbytes

    total_original_bytes += original_bytes
    total_resized_bytes += resized_bytes

    print(
        f"{label_name:<12} {str(original_shape):<12} {format_bytes(original_bytes):<32} "
        f"{str(resized_shape):<14} {format_bytes(resized_bytes)}"
    )

    plt.subplot(3, 3, i + 1)
    plt.imshow(img_2d, cmap='inferno')
    plt.title(f"[{label_name}]", fontsize=13, fontweight='bold')

    # 이미지 위에 크기 + 용량(B/KB/MB) 정보 오버레이
    plt.text(
        0.5, -0.08,
        f"{original_shape[0]}x{original_shape[1]} ({original_bytes}B/{original_bytes/1024:.2f}KB) -> "
        f"{resized_shape[0]}x{resized_shape[1]}x{resized_shape[2]} ({resized_bytes}B/{resized_bytes/1024:.2f}KB)",
        transform=plt.gca().transAxes,
        ha='center', va='top', fontsize=8, color='black'
    )
    plt.axis('off')

print("-" * 110)
print(f"대표 이미지 9장 합계 -> 원본: {format_bytes(total_original_bytes)}, 리사이즈 후: {format_bytes(total_resized_bytes)}")

# 데이터셋 전체 용량 (실제 학습에 쓰이는 X_train, X_test 전체)
print(f"\nX_train 전체 용량: {format_bytes(X_train.nbytes)}")
print(f"X_test  전체 용량: {format_bytes(X_test.nbytes)}")

plt.tight_layout()
plt.savefig('wafer_samples.png', dpi=100)
print("-> wafer_samples.png 로 저장 완료")
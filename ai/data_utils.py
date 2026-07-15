"""
pkl 로드, 라벨 정제, 리사이즈, 클래스 불균형 해소(증강 포함) 관련 함수들.
"""
import numpy as np
import pandas as pd
import cv2

import config


def get_exact_label(label):
    if isinstance(label, (list, np.ndarray)) and len(label) > 0:
        val = label[0][0] if isinstance(label[0], (list, np.ndarray)) else label[0]
        return str(val)
    return 'unlabeled'


def load_labeled_data(pkl_path=config.PKL_PATH):
    """LSWMD.pkl 로드 -> unlabeled 제외한 라벨 있는 데이터만 반환"""
    print("=== 1. 데이터 로드 및 정제 ===")
    data = pd.read_pickle(pkl_path)
    data['clean_label'] = data['failureType'].apply(get_exact_label)
    labeled_data = data[data['clean_label'] != 'unlabeled'].copy()
    print(f"-> 유효 데이터 {len(labeled_data)}개 추출 완료.")
    return labeled_data


def load_external_test_folder(folder):
    """
    real_upload_test_samples, synth_wafer_images_v2처럼
    folder/<class_name>/*.png (팔레트 모드, 인덱스 0/1/2) + folder/index.csv 구조를 읽는다.
    반환 컬럼: waferMap, clean_label (load_labeled_data와 동일한 스키마로 맞춤)
    """
    import os
    from PIL import Image

    index_df = pd.read_csv(os.path.join(folder, 'index.csv'))
    wafer_maps = []
    for fname in index_df['filename']:
        img = Image.open(os.path.join(folder, fname))
        wafer_maps.append(np.array(img))  # mode='P' -> 인덱스(0/1/2) 배열 그대로
    return pd.DataFrame({'waferMap': wafer_maps, 'clean_label': index_df['label'].values})


def resize_for_dl(img_array, target_size=config.TARGET_SIZE):
    img_array = np.asarray(img_array)
    if img_array.dtype not in (np.uint8, np.float32):
        img_array = img_array.astype(np.uint8)
    return cv2.resize(img_array, dsize=target_size, interpolation=cv2.INTER_NEAREST)


def compute_density(img):
    """waferMap 값: 0=웨이퍼 밖, 1=정상 다이, 2=불량 다이.
    밀도 = 불량 다이 수 / (정상+불량 다이 수), 웨이퍼 밖은 분모에서 제외."""
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


def balance_defect_class(df, target_count, template_columns, max_augment_ratio=None,
                          seed=config.SEED):
    """
    df를 target_count까지 오버샘플링(+증강)한다.
    template_columns: df가 비어있을 때 반환할 빈 DataFrame의 컬럼 (train_df.columns 넘기면 됨)
    """
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=template_columns)

    current_count = len(df)

    if current_count >= target_count:
        return df.sample(n=target_count, random_state=seed)

    effective_target = target_count
    if max_augment_ratio is not None:
        capped_target = current_count * (1 + max_augment_ratio)
        if capped_target < target_count:
            effective_target = capped_target

    needed = effective_target - current_count
    if needed <= 0:
        return df

    samples = df.sample(n=needed, replace=True, random_state=seed).copy()
    samples['waferMap_resized'] = samples['waferMap_resized'].apply(apply_advanced_augmentation)
    return pd.concat([df, samples], ignore_index=True)


def build_balanced_train_set(train_df, seed=config.SEED):
    """
    labels_of_interest 순서대로 클래스별 목표 개수(NORMAL_TARGET/DEFECT_TARGET)에 맞춰
    언더/오버샘플링한 최종 학습셋을 만든다.
    """
    balanced_parts = []
    for lbl in config.LABELS_OF_INTEREST:
        subset = train_df[train_df['clean_label'] == lbl].copy()
        target = config.NORMAL_TARGET if lbl == 'none' else config.DEFECT_TARGET

        if lbl == 'none' and len(subset) > config.NORMAL_TARGET:
            balanced_parts.append(subset.sample(n=config.NORMAL_TARGET, random_state=seed))
        elif lbl == 'Near-full':
            result = balance_defect_class(
                subset, target, train_df.columns,
                max_augment_ratio=config.MAX_AUGMENT_RATIO, seed=seed
            )
            print(f"   -> Near-full: 원본 {len(subset)}개 -> 최종 {len(result)}개 "
                  f"(비율 상한 {config.MAX_AUGMENT_RATIO}배 적용)")
            balanced_parts.append(result)
        else:
            balanced_parts.append(balance_defect_class(subset, target, train_df.columns, seed=seed))

    final_train_df = pd.concat(balanced_parts, ignore_index=True)
    final_train_df = final_train_df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return final_train_df
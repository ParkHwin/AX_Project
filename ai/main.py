"""
진입점. 각 단계를 모듈에서 불러와서 순서대로 실행만 함 - 로직 자체는 여기 없음.
input/output만 확인하고 싶으면 이 파일만 보면 전체 흐름이 한눈에 들어옴.
"""
import random
import warnings
import json
import gc

import numpy as np
import torch
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

import config
from data_utils import load_labeled_data, resize_for_dl, build_balanced_train_set
from dataset import WaferDataset
from model import ResNet9
from train import train_model
from evaluate import save_training_curves, run_test_inference, compute_confusion_and_metrics
# evaluate.py를 import하는 순간 한글 폰트 설정 + Glyph 경고 억제가 이미 적용됨
# (예전엔 여기 main.py에도 따로 있었는데, test_only.py 등 다른 진입점에서 빠지는
#  문제가 있어서 evaluate.py 쪽으로 옮기고 여기 중복은 제거함)


def set_seed(seed=config.SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def main():
    set_seed()

    # 1. 데이터 로드 및 정제
    labeled_data = load_labeled_data()

    # 2. 리사이징 및 라벨 인코딩
    print("\n=== 2. 리사이징 및 라벨 인코딩 ===")
    labeled_data['waferMap_resized'] = labeled_data['waferMap'].apply(resize_for_dl)
    labeled_data = labeled_data.drop(columns=['waferMap'])  # 원본(가변 크기) 배열은 이제 불필요 -> 메모리 절약
    gc.collect()
    le = LabelEncoder()
    labeled_data['encoded_label'] = le.fit_transform(labeled_data['clean_label'])
    label_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
    print(f"-> 라벨 매핑 정보: {label_mapping}")

    # 3. Train/Test 분할 (증강 전)
    print("\n=== 3. Train/Test 분할 (증강 이전) ===")
    y_raw = labeled_data['encoded_label'].values
    train_idx, test_idx = train_test_split(
        np.arange(len(labeled_data)),
        test_size=0.2, random_state=config.SEED, stratify=y_raw
    )
    train_df = labeled_data.iloc[train_idx].reset_index(drop=True)
    test_df = labeled_data.iloc[test_idx].reset_index(drop=True)
    print(f"-> train {len(train_df)}개 / test {len(test_df)}개 (분할 시점, 증강 전)")

    # 4. 클래스 불균형 해소 (train에만 적용)
    print("\n=== 4. 클래스 불균형 해소 (train 데이터에만 적용) ===")
    final_train_df = build_balanced_train_set(train_df)
    print(f"-> 최종 train {len(final_train_df)}개 "
          f"(분포: {final_train_df['clean_label'].value_counts().to_dict()})")
    print(f"-> test는 증강 없이 원본 그대로 {len(test_df)}개 유지")

    # 5. 텐서 변환
    print("\n=== 5. 텐서 변환 ===")
    X_train_full = np.expand_dims(np.stack(final_train_df['waferMap_resized'].values), axis=-1)
    y_train_full = final_train_df['encoded_label'].values
    X_test = np.expand_dims(np.stack(test_df['waferMap_resized'].values), axis=-1)
    y_test = test_df['encoded_label'].values
    print(f"X_train_full: {X_train_full.shape}, y_train_full: {y_train_full.shape}")
    print(f"X_test      : {X_test.shape}, y_test      : {y_test.shape}")

    # 텐서로 다 옮겼으니 원본 DataFrame들(수만 행, 이미지 배열 포함)은 더 이상 불필요 -> 즉시 해제
    del labeled_data, train_df, test_df, final_train_df
    gc.collect()

    num_classes = len(label_mapping)
    reverse_label_mapping = {v: k for k, v in label_mapping.items()}

    # 6. Train -> Train/Val 분리
    print("\n=== 6. Train -> Train/Val 분리 ===")
    tr_idx, val_idx = train_test_split(
        np.arange(len(y_train_full)),
        test_size=0.1, random_state=config.SEED, stratify=y_train_full
    )
    X_train, y_train = X_train_full[tr_idx], y_train_full[tr_idx]
    X_val, y_val = X_train_full[val_idx], y_train_full[val_idx]
    print(f"-> train {len(y_train)}개 / val {len(y_val)}개 (train 내부 분리, test는 미접촉 유지)")

    # 7. Dataset / DataLoader
    train_loader = torch.utils.data.DataLoader(
        WaferDataset(X_train, y_train), batch_size=config.BATCH_SIZE,
        shuffle=True, num_workers=config.NUM_WORKERS)
    val_loader = torch.utils.data.DataLoader(
        WaferDataset(X_val, y_val), batch_size=config.BATCH_SIZE,
        shuffle=False, num_workers=config.NUM_WORKERS)
    test_loader = torch.utils.data.DataLoader(
        WaferDataset(X_test, y_test), batch_size=config.BATCH_SIZE,
        shuffle=False, num_workers=config.NUM_WORKERS)

    # torch tensor로 이미 복사됐으니, 중복으로 남아있는 numpy 원본들 해제
    del X_train_full, y_train_full, X_train, X_val, X_test
    gc.collect()

    # 8. Class Weight 계산
    print("\n=== 7. Class Weight 계산 (confusion 패턴 기반 재설계) ===")
    class_weights = np.ones(num_classes, dtype=np.float64)
    none_idx = label_mapping['none']
    near_full_idx = label_mapping['Near-full']
    class_weights[none_idx] = config.NONE_CLASS_WEIGHT
    class_weights[near_full_idx] = config.NEAR_FULL_CLASS_WEIGHT
    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32)

    print(f"{'클래스':<12}{'가중치':<10}{'비고'}")
    for c in range(num_classes):
        note = ""
        if c == none_idx:
            note = "<- 상향 (오분류 민감도 증가)"
        elif c == near_full_idx:
            note = "<- 상향 (절대 샘플 희소)"
        print(f"{reverse_label_mapping[c]:<12}{class_weights[c]:<10.4f}{note}")

    # 9. 모델 준비
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n=== 8. 학습 디바이스: {device} ===")
    model = ResNet9(num_classes).to(device)
    class_weights_tensor = class_weights_tensor.to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"-> 모델 파라미터 수: {total_params:,}")

    # 10. 학습
    history, best_epoch, _ = train_model(model, train_loader, val_loader, device, class_weights_tensor)
    save_training_curves(history, best_epoch, config.EPOCHS)

    # 11. 최종 테스트 평가 (콘솔 지표 출력만, 이미지 저장은 training_curves.png만 남기기로 함)
    all_preds, all_labels = run_test_inference(model, test_loader, device)
    compute_confusion_and_metrics(all_preds, all_labels, num_classes, reverse_label_mapping)

    # 모델 저장
    torch.save(model.state_dict(), config.MODEL_SAVE_PATH)
    with open('label_mapping.json', 'w', encoding='utf-8') as f:
        json.dump({k: int(v) for k, v in label_mapping.items()}, f, ensure_ascii=False, indent=2)
    print(f"-> label_mapping.json 저장 완료 (평가 전용 스크립트가 이 파일로 클래스 순서 확인)")
    print(f"-> 모델 저장 완료: {config.MODEL_SAVE_PATH} (epoch {best_epoch} 기준, early stopping 적용됨)")


if __name__ == '__main__':
    main()
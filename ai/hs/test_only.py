"""
평가 전용 진입점. main.py처럼 학습을 처음부터 다시 돌리지 않고,
이미 저장된 resnet9_wafer.pth + label_mapping.json으로 지정한 테스트 폴더만 평가한다.

사용법:
    python test_only.py --test_folder real_upload_test_samples
    python test_only.py --test_folder synth_wafer_images_v2

모델을 다시 학습하지 않고 저장된 모델로 외부 테스트 폴더만 평가
"""
import argparse
import json

import numpy as np
import torch

import config
from data_utils import load_external_test_folder, resize_for_dl
from dataset import WaferDataset
from model import ResNet9
from evaluate import run_test_inference, compute_confusion_and_metrics


def main():
    parser = argparse.ArgumentParser(description="학습 없이 지정 폴더로 평가만 실행")
    parser.add_argument("--test_folder", required=True,
                         help="class_name/*.png + index.csv 구조의 테스트 폴더 (예: real_upload_test_samples)")
    parser.add_argument("--weights", default=config.MODEL_SAVE_PATH)
    parser.add_argument("--label_mapping", default="label_mapping.json")
    args = parser.parse_args()

    with open(args.label_mapping, 'r', encoding='utf-8') as f:
        label_mapping = json.load(f)
    reverse_label_mapping = {v: k for k, v in label_mapping.items()}
    num_classes = len(label_mapping)
    none_idx = label_mapping['none']
    print(f"-> label_mapping 로드: {label_mapping}")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if device.type == 'cpu':
        print("!" * 60)
        print("[경고] GPU 못 찾음 -> CPU로 평가 (평가는 학습보다 가벼워서 크게 안 느릴 것)")
        print("!" * 60)
    else:
        print(f"-> 디바이스: {device} ({torch.cuda.get_device_name(0)})")

    model = ResNet9(num_classes).to(device)
    model.load_state_dict(torch.load(args.weights, map_location=device))
    print(f"-> 가중치 로드 완료: {args.weights} (학습 안 함, 평가만 진행)")

    # 테스트 폴더 로드 + 학습 때와 동일한 전처리
    test_df = load_external_test_folder(args.test_folder)

    known_labels = set(label_mapping.keys())
    unknown_mask = ~test_df['clean_label'].isin(known_labels)
    if unknown_mask.any():
        print(f"   [경고] label_mapping에 없는 클래스 "
              f"{test_df.loc[unknown_mask, 'clean_label'].unique().tolist()} 제외")
        test_df = test_df[~unknown_mask].copy()

    if len(test_df) == 0:
        raise ValueError(
            f"[{args.test_folder}] 라벨 필터링 후 남은 이미지가 0개입니다. "
            f"index.csv의 label 값이 label_mapping.json의 클래스명과 정확히 일치하는지 확인하세요 "
            f"(대소문자/철자 포함)."
        )

    test_df['waferMap_resized'] = test_df['waferMap'].apply(resize_for_dl)
    test_df['encoded_label'] = test_df['clean_label'].map(label_mapping)
    test_df = test_df.drop(columns=['waferMap']).reset_index(drop=True)
    print(f"-> 테스트셋({args.test_folder}) {len(test_df)}개 로드 완료")

    X_test = np.expand_dims(np.stack(test_df['waferMap_resized'].values), axis=-1)
    y_test = test_df['encoded_label'].values

    test_loader = torch.utils.data.DataLoader(
        WaferDataset(X_test, y_test), batch_size=config.BATCH_SIZE,
        shuffle=False, num_workers=config.NUM_WORKERS)

    all_preds, all_labels = run_test_inference(model, test_loader, device)
    compute_confusion_and_metrics(all_preds, all_labels, num_classes, reverse_label_mapping)


if __name__ == "__main__":
    main()
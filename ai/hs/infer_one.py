"""
이미지 한 장 추론 스크립트.

이전 버전(infer_single.py)은 텐서 변환을 직접 다시 짜다가 test_only.py와
결과가 달라지는 버그가 있었음 (원인 특정 전 폐기). 이번 버전은 그 문제를
원천 차단하기 위해, test_only.py/evaluate.py가 이미 검증한 것과 100% 동일한
경로(resize_for_dl -> WaferDataset -> DataLoader)를 그대로 재사용한다.
직접 텐서를 새로 만들지 않는다.

사용법:
    python infer_one.py --image real_holdout_100/Center/123741_lot8227_w4.png
    python infer_one.py --folder wafer_images/unlabeled   (그 안에서 랜덤으로 하나)

이미지 한장 넣으면 모델이 어떤 클래스인지 예측
"""
import argparse
import json
import os
import random

import numpy as np
import torch
from PIL import Image

import config
from model import ResNet9
from data_utils import resize_for_dl, validate_wafer_array
from dataset import WaferDataset


def load_wafer_image(path):
    img = Image.open(path)
    arr = np.array(img)
    validate_wafer_array(arr, source=path)  # 차원 + 0/1/2 값 검증 (data_utils.py와 공용)
    return arr


def main():
    parser = argparse.ArgumentParser(description="이미지 한 장 추론 (test_only.py와 동일 경로 재사용)")
    parser.add_argument("--image", help="이미지 파일 경로")
    parser.add_argument("--folder", help="이 폴더 안에서 랜덤으로 하나 골라 추론")
    parser.add_argument("--weights", default=config.MODEL_SAVE_PATH)
    parser.add_argument("--label_mapping", default="label_mapping.json")
    parser.add_argument("--preview_out", default="unlabeled_preview.png")
    parser.add_argument("--scale", type=int, default=8)
    args = parser.parse_args()

    if not args.image and not args.folder:
        parser.error("--image 또는 --folder 중 하나는 반드시 지정해야 합니다.")

    if args.image:
        image_path = args.image
    else:
        candidates = [f for f in os.listdir(args.folder) if f.lower().endswith(('.png', '.bmp'))]
        if not candidates:
            raise FileNotFoundError(f"{args.folder}에 png/bmp 이미지가 없습니다.")
        chosen = random.choice(candidates)
        image_path = os.path.join(args.folder, chosen)
        print(f"-> {args.folder}에서 랜덤으로 골라짐: {chosen}")

    with open(args.label_mapping, 'r', encoding='utf-8') as f:
        label_mapping = json.load(f)
    reverse_label_mapping = {v: k for k, v in label_mapping.items()}
    num_classes = len(label_mapping)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if device.type == 'cpu':
        print("[경고] GPU 못 찾음 -> CPU로 추론")

    model = ResNet9(num_classes).to(device)
    model.load_state_dict(torch.load(args.weights, map_location=device))
    model.eval()
    print(f"-> 가중치 로드 완료: {args.weights}")

    raw_arr = load_wafer_image(image_path)
    print(f"-> 원본 이미지: {image_path} (크기 {raw_arr.shape}, 값 종류: {np.unique(raw_arr)})")

    # --- 여기서부터 test_only.py와 완전히 동일한 경로 ---
    resized = resize_for_dl(raw_arr)                          # (64,64)
    X = np.expand_dims(np.stack([resized]), axis=-1)          # (1,64,64,1) - test_only.py와 동일 shape
    y_dummy = np.array([0])                                   # 라벨 없어서 더미값 (평가에 안 씀)

    single_dataset = WaferDataset(X, y_dummy)                 # WaferDataset이 정규화/permute 전부 처리
    x_tensor = single_dataset.X.to(device)                    # (1,1,64,64), 이미 /2.0 정규화됨

    with torch.no_grad():
        logits = model(x_tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

    pred_id = int(np.argmax(probs))
    pred_name = reverse_label_mapping[pred_id]
    confidence = float(probs[pred_id])

    print(f"\n=== 추론 결과 ===")
    print(f"예측 클래스: {pred_name} (confidence={confidence:.4f})")
    print(f"\n클래스별 확률:")
    for idx in np.argsort(-probs):
        marker = " <- 예측" if idx == pred_id else ""
        print(f"   {reverse_label_mapping[idx]:<12}{probs[idx]:.4f}{marker}")

    img = Image.open(image_path)
    if img.mode == 'P':
        big = img.resize((img.width * args.scale, img.height * args.scale), Image.NEAREST)
    else:
        palette_img = Image.fromarray(raw_arr, mode='P')
        palette_img.putpalette([240, 239, 237, 98, 148, 207, 200, 50, 43] + [0] * (256 * 3 - 9))
        big = palette_img.resize((raw_arr.shape[1] * args.scale, raw_arr.shape[0] * args.scale), Image.NEAREST)
    big.save(args.preview_out)
    print(f"\n-> 확대 미리보기 저장 완료: {args.preview_out}")


if __name__ == "__main__":
    main()
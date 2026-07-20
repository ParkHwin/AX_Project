"""
wafer_images.zip(index.csv 포함)에서 클래스당 100개씩 뽑아 진짜 held-out test로 만들고,
그 인덱스를 LSWMD.pkl에서 제외해서 "학습에 절대 안 쓰인 진짜 테스트셋"을 만든다.

핵심 가정: wafer_images/index.csv의 'index' 컬럼이 원본 LSWMD.pkl의 행 위치(row position)와
동일하다. LSWMD.pkl은 보통 기본 순번(RangeIndex)을 유지한 채 배포되는 파일이라 이 가정이
맞을 가능성이 높지만, 100% 확신은 못 하므로 아래 '검증 단계'를 반드시 먼저 통과해야 함.

사용법:
    python prepare_real_holdout.py
    -> 1) 검증: LSWMD.pkl의 특정 행과 wafer_images의 해당 이미지가 실제로 같은지 확인
    -> 2) 검증 통과 시: real_holdout_100/<class>/*.png + index.csv 생성
    ->                  excluded_pkl_indices.json 생성 (main.py가 이 파일 보고 학습에서 제외)
"""
import os
import json
import random

import numpy as np
import pandas as pd
from PIL import Image

WAFER_IMAGES_DIR = 'wafer_images'          # index.csv + 클래스별 폴더가 있는 곳
PKL_PATH = 'LSWMD.pkl'
OUT_DIR = 'real_holdout_100'
N_PER_CLASS = 100
SEED = 42

random.seed(SEED)


def get_exact_label(label):
    if isinstance(label, (list, np.ndarray)) and len(label) > 0:
        val = label[0][0] if isinstance(label[0], (list, np.ndarray)) else label[0]
        return str(val)
    return 'unlabeled'


def verify_index_correspondence(wafer_index_df, pkl_data, n_check=10):
    """
    wafer_images의 index 컬럼이 LSWMD.pkl의 실제 행 위치와 일치하는지 표본 검사.
    shape과 failureType(라벨)이 둘 다 일치해야 통과로 간주.
    """
    print(f"\n=== 검증: index 대응 관계 확인 (표본 {n_check}개) ===")
    labeled_rows = wafer_index_df[wafer_index_df['failureType'] != 'unlabeled'].sample(
        n=min(n_check, len(wafer_index_df)), random_state=SEED
    )

    all_match = True
    for _, row in labeled_rows.iterrows():
        pkl_idx = row['index']
        png_path = os.path.join(WAFER_IMAGES_DIR, row['path'])

        if pkl_idx >= len(pkl_data):
            print(f"   [실패] index {pkl_idx}가 pkl 전체 행 수({len(pkl_data)})를 벗어남")
            all_match = False
            continue

        pkl_row = pkl_data.iloc[pkl_idx]
        pkl_label = get_exact_label(pkl_row['failureType'])
        pkl_shape = np.asarray(pkl_row['waferMap']).shape

        png_arr = np.array(Image.open(png_path))
        png_shape = png_arr.shape

        label_match = (pkl_label == row['failureType'])
        shape_match = (pkl_shape == png_shape)

        status = "OK" if (label_match and shape_match) else "MISMATCH"
        if status == "MISMATCH":
            all_match = False
        print(f"   [{status}] index={pkl_idx}: pkl라벨={pkl_label}({pkl_shape}) "
              f"vs png라벨={row['failureType']}({png_shape})")

    return all_match


def main():
    print("=== 1. wafer_images/index.csv 로드 ===")
    wafer_index_df = pd.read_csv(os.path.join(WAFER_IMAGES_DIR, 'index.csv'))
    print(f"-> 전체 {len(wafer_index_df)}행")

    print("\n=== 2. LSWMD.pkl 로드 (검증용) ===")
    pkl_data = pd.read_pickle(PKL_PATH)
    print(f"-> 전체 {len(pkl_data)}행")

    ok = verify_index_correspondence(wafer_index_df, pkl_data)
    if not ok:
        print("\n[중단] 검증 실패 -> index가 LSWMD.pkl 행 위치와 안 맞습니다.")
        print("       이 방법은 못 씁니다. 다른 방식(예: waferMap 배열 직접 비교)이 필요합니다.")
        return
    print("\n-> 검증 통과: wafer_images의 index가 LSWMD.pkl 행 위치와 일치함 확인")

    print(f"\n=== 3. 클래스당 {N_PER_CLASS}개씩 추출 ===")
    labeled_df = wafer_index_df[wafer_index_df['failureType'] != 'unlabeled'].copy()
    chosen_rows = []
    for cls, group in labeled_df.groupby('failureType'):
        n = min(N_PER_CLASS, len(group))
        chosen = group.sample(n=n, random_state=SEED)
        chosen_rows.append(chosen)
        print(f"   {cls}: {n}개 (보유 {len(group)}개 중)")
    chosen_df = pd.concat(chosen_rows, ignore_index=True)
    print(f"-> 총 {len(chosen_df)}개 선정")

    print(f"\n=== 4. 이미지 복사 + index.csv 생성 ({OUT_DIR}) ===")
    rows = []
    for _, row in chosen_df.iterrows():
        cls = row['failureType']
        src = os.path.join(WAFER_IMAGES_DIR, row['path'])
        dst_dir = os.path.join(OUT_DIR, cls)
        os.makedirs(dst_dir, exist_ok=True)
        fname = os.path.basename(row['path'])
        dst = os.path.join(dst_dir, fname)
        Image.open(src).save(dst)  # 팔레트 모드 그대로 저장
        rows.append({'filename': f'{cls}/{fname}', 'label': cls})

    with open(os.path.join(OUT_DIR, 'index.csv'), 'w', newline='') as f:
        import csv
        w = csv.DictWriter(f, fieldnames=['filename', 'label'])
        w.writeheader()
        w.writerows(rows)
    print(f"-> {len(rows)}개 이미지 복사 완료")

    print("\n=== 5. 제외할 pkl 인덱스 저장 ===")
    excluded_indices = chosen_df['index'].astype(int).tolist()
    with open('excluded_pkl_indices.json', 'w') as f:
        json.dump(excluded_indices, f)
    print(f"-> excluded_pkl_indices.json 저장 완료 ({len(excluded_indices)}개 인덱스)")
    print("-> main.py가 이 파일이 있으면 자동으로 학습 데이터에서 제외합니다.")


if __name__ == '__main__':
    main()
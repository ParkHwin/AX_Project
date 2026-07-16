"""
딱 한 번만 실행하는 전처리 스크립트.

LSWMD.pkl은 unlabeled(라벨 없음) 데이터까지 포함해서 80만 행 넘게 있는데,
학습에는 라벨 있는 17만 행 정도만 씁니다. 근데 main.py를 실행할 때마다 매번
pd.read_pickle(LSWMD.pkl)로 80만 행 전체를 메모리에 올렸다가 그중 17만 행만
남기고 버리는 짓을 반복하게 됨 -> 이게 메모리 피크의 진짜 원인.

이 스크립트를 딱 한 번 돌려서 라벨 있는 것만 걸러진 작은 pkl을 만들어두면,
이후 main.py는 이 작은 파일만 읽으면 되므로 매번 반복되던 메모리 피크가 사라짐.

사용법:
    python preprocess_pkl.py
    -> LSWMD_labeled_only.pkl 생성됨
    -> config.py의 PKL_PATH를 'LSWMD_labeled_only.pkl'로 바꾸면 적용됨
"""
import pandas as pd
import numpy as np
import gc

SRC_PKL = 'LSWMD.pkl'
OUT_PKL = 'LSWMD_labeled_only.pkl'


def get_exact_label(label):
    if isinstance(label, (list, np.ndarray)) and len(label) > 0:
        val = label[0][0] if isinstance(label[0], (list, np.ndarray)) else label[0]
        return str(val)
    return 'unlabeled'


if __name__ == '__main__':
    print(f"-> {SRC_PKL} 로딩 중 (전체, 시간이 좀 걸릴 수 있음)...")
    data = pd.read_pickle(SRC_PKL)
    print(f"-> 전체 {len(data)}행 로드 완료")

    data['clean_label'] = data['failureType'].apply(get_exact_label)
    labeled = data[data['clean_label'] != 'unlabeled'].copy()
    del data
    gc.collect()

    # waferMap, clean_label 두 컬럼만 남김 (main.py/data_utils.py가 실제로 쓰는 건 이게 전부)
    labeled = labeled[['waferMap', 'clean_label']].reset_index(drop=True)

    print(f"-> 라벨 있는 데이터 {len(labeled)}행만 추출 완료")
    print(labeled['clean_label'].value_counts())

    labeled.to_pickle(OUT_PKL)
    print(f"-> {OUT_PKL} 저장 완료. config.py의 PKL_PATH를 이 파일명으로 바꾸면 됨.")
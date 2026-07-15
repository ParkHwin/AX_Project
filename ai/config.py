"""
전역 설정값. 경로나 하이퍼파라미터 바꿀 때 이 파일만 건드리면 됨.
"""
import os

# 데이터 경로
PKL_PATH = 'LSWMD.pkl'

# 재현성
SEED = 42

# 전처리
TARGET_SIZE = (64, 64)

# 클래스 불균형 처리
NORMAL_TARGET = 10000
DEFECT_TARGET = 5000
MAX_AUGMENT_RATIO = 5

LABELS_OF_INTEREST = ['none', 'Center', 'Donut', 'Edge-Ring', 'Edge-Loc',
                       'Loc', 'Random', 'Scratch', 'Near-full']

# 학습 하이퍼파라미터
BATCH_SIZE = 64
NUM_WORKERS = 0  # Windows spawn 이슈 회피
EPOCHS = int(os.environ.get('SMOKE_EPOCHS', 20))
LR = 1e-3
WEIGHT_DECAY = 1e-4

# 클래스 가중치 (오분류 패턴 기반 재설계)
NONE_CLASS_WEIGHT = 2.3   # none 오분류 억제 강화
NEAR_FULL_CLASS_WEIGHT = 1.5  # 절대 샘플 수 희소성 보완

# none 오분류 분석 시 비교 대상 클래스
TARGET_CONFUSIONS = ['Loc', 'Scratch', 'Edge-Loc']

# 출력 파일명
MODEL_SAVE_PATH = 'resnet9_wafer.pth'
TRAINING_CURVES_PATH = 'training_curves.png'
MISCLASSIFIED_SAMPLES_PATH = 'none_misclassified_samples.png'
DENSITY_COMPARISON_PATH = 'none_density_comparison.png'
TEST_EVALUATION_PATH = 'test_evaluation.png'
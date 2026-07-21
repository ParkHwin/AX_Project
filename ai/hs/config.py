"""
전역 설정값. 경로나 하이퍼파라미터 바꿀 때 이 파일만 건드리면 됨.
프로젝트에서 사용하는 설정값을 한곳에 모아둔 파일
"""
import os

# 데이터 경로
PKL_PATH = 'LSWMD_labeled_only.pkl'

# =============================================================
# synth_wafer_images_v3(900장, 클래스당 100개)를 학습에 소량 병합할지 여부
#   INCLUDE_SYNTH_IN_TRAIN=1 python main.py  -> 섞어서 학습
#   (기본값 0) python main.py                 -> 안 섞고 REAL만 학습
# test(REAL held-out)는 이 옵션과 무관하게 항상 순수 REAL만 사용 -> 공정 비교 보장
# v3는 900장뿐이라 메모리 부담 거의 없음 (전체 학습 데이터 17만 장 대비 0.5%)
# =============================================================
INCLUDE_SYNTH_IN_TRAIN = os.environ.get('INCLUDE_SYNTH_IN_TRAIN', '0') == '1'
SYNTH_TRAIN_FOLDER = 'synth_wafer_images_v3'

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
EPOCHS = int(os.environ.get('SMOKE_EPOCHS', 21))
LR = 1e-3 # 0.001 
WEIGHT_DECAY = 1e-4 # 0.0001

# Early Stopping: val Macro F1이 이 횟수만큼 연속으로 최고치를 못 넘으면 학습 조기 종료
EARLY_STOPPING_PATIENCE = int(os.environ.get('PATIENCE', 5))

# 클래스 가중치 (오분류 패턴 기반 재설계)
# 클래스 가중치 (오분류 패턴 기반 재설계)
# [재실험] none precision이 낮게 나온 문제(결함이 none으로 새는 것) 확인 후
# 기본값을 2.3 -> 1.8로 낮춤. NONE_WEIGHT 환경변수로 바로 실험 가능하게 함.
#   NONE_WEIGHT=1.5 python main.py  처럼 값 바꿔가며 재실험 용이하게
NONE_CLASS_WEIGHT = float(os.environ.get('NONE_WEIGHT', 1.8))   # none 오분류 억제 (2.3->1.8로 완화)
NEAR_FULL_CLASS_WEIGHT = 1.5  # 절대 샘플 수 희소성 보완

# none 오분류 분석 시 비교 대상 클래스
TARGET_CONFUSIONS = ['Loc', 'Scratch', 'Edge-Loc']

# 출력 파일명
MODEL_SAVE_PATH = 'resnet9_wafer.pth'
TRAINING_CURVES_PATH = 'training_curves.png'
MISCLASSIFIED_SAMPLES_PATH = 'none_misclassified_samples.png'
DENSITY_COMPARISON_PATH = 'none_density_comparison.png'
TEST_EVALUATION_PATH = 'test_evaluation.png'
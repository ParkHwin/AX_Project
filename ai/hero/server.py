import sys
import os
import json
import numpy as np
import torch
import uvicorn
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List

# --- 경로 설정 (기존과 동일) ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'hs'))
if HS_DIR not in sys.path:
    sys.path.append(HS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

try:
    from hs.model import ResNet9
    from hs.data_utils import resize_for_dl
    from hs.dataset import WaferDataset
    import hs.config as config
except ImportError as e:
    print(f"Error: 필수 hs 모듈을 가져올 수 없습니다. 경로를 확인해주세요. {e}")
    sys.exit(1)

app = FastAPI(title="Wafer Map Classification API")

# --- 허용 파일 형식 정의 ---
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_MB = 10

# --- 모델 초기화 (기존과 동일, 생략) ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

hs_dir = os.path.join(PROJECT_ROOT, 'hs')
label_mapping_path = os.path.join(hs_dir, 'label_mapping.json')
weights_path = os.path.join(hs_dir, config.MODEL_SAVE_PATH)

if not os.path.exists(weights_path):
    print(f"Error: 모델 가중치 파일을 찾을 수 없습니다: {weights_path}")
    sys.exit(1)

with open(label_mapping_path, 'r', encoding='utf-8') as f:
    label_mapping = json.load(f)
reverse_label_mapping = {v: k for k, v in label_mapping.items()}
num_classes = len(label_mapping)

model = ResNet9(num_classes).to(device)
model.load_state_dict(torch.load(weights_path, map_location=device))
model.eval()


class Prediction(BaseModel):
    label: str
    confidence: float


class PredictionResult(BaseModel):
    top_predictions: List[Prediction]


# --- 입력 검증 전용 함수 ---
def validate_upload_file(file: UploadFile, content: bytes) -> None:
    """
    파일 형식 관련 문제는 여기서 미리 걸러내고,
    문제가 있으면 400 HTTPException을 바로 던진다.
    """
    # 1. 확장자 검사
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 확장자입니다: '{ext}'. png 또는 jpg 파일만 업로드해주세요."
        )

    # 2. Content-Type 검사 (확장자만으로는 위조 가능하므로 이중 체크)
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다: '{file.content_type}'. 이미지 파일만 업로드해주세요."
        )

    # 3. 파일 크기 검사
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 너무 큽니다({size_mb:.1f}MB). {MAX_FILE_SIZE_MB}MB 이하만 업로드 가능합니다."
        )

    # 4. 빈 파일 검사
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="빈 파일은 업로드할 수 없습니다.")


def load_and_validate_image(content: bytes) -> np.ndarray:
    """
    실제로 이미지를 열어보고, 이미지로서 유효한지 검증한다.
    여기서 발생하는 문제도 전부 '사용자 입력 문제'이므로 400으로 처리한다.
    """
    try:
        img = Image.open(BytesIO(content))
        img.verify()  # 이미지 구조 자체가 손상되지 않았는지 검증
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="이미지를 인식할 수 없습니다. 올바른 이미지 파일인지 확인해주세요."
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="이미지 파일이 손상되었거나 올바르지 않은 형식입니다."
        )

    # verify() 이후에는 파일 포인터를 다시 열어야 함
    try:
        img = Image.open(BytesIO(content))
        raw_arr = np.array(img)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="이미지 데이터를 배열로 변환하는 데 실패했습니다."
        )

    # 최소 크기 검증 (너무 작은 이미지는 웨이퍼맵으로 의미가 없음)
    if raw_arr.ndim < 2 or raw_arr.shape[0] < 8 or raw_arr.shape[1] < 8:
        raise HTTPException(
            status_code=400,
            detail="이미지 크기가 너무 작습니다. 유효한 웨이퍼맵 이미지를 업로드해주세요."
        )

    return raw_arr


@app.post("/predict", response_model=PredictionResult)
async def predict(file: UploadFile = File(...)):
    # --- 1단계: 파일 자체 검증 (400 영역) ---
    content = await file.read()
    validate_upload_file(file, content)
    raw_arr = load_and_validate_image(content)

    # --- 2단계: 전처리 (여기서 나는 에러도 대부분 입력 문제 → 400) ---
    try:
        resized = resize_for_dl(raw_arr)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"이미지 전처리 중 문제가 발생했습니다: {str(e)}"
        )

    # --- 3단계: 모델 추론 (여기부터는 서버/모델 문제 → 500) ---
    try:
        X = np.expand_dims(np.stack([resized]), axis=-1)
        y_dummy = np.array([0])
        single_dataset = WaferDataset(X, y_dummy)
        x_tensor = single_dataset.X.to(device)

        with torch.no_grad():
            logits = model(x_tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

        sorted_indices = np.argsort(-probs)
        top_predictions = [
            {"label": reverse_label_mapping[idx], "confidence": float(probs[idx])}
            for idx in sorted_indices
        ]

        return {"top_predictions": top_predictions}

    except Exception as e:
        # 여기 도달했다면 입력 문제가 아니라 모델/서버 내부 문제
        raise HTTPException(
            status_code=500,
            detail=f"모델 추론 중 서버 오류가 발생했습니다: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
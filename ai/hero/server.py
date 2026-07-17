import sys
import os
import json
import numpy as np
import torch
import uvicorn
from PIL import Image
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel

# --- 경로 설정: hs 폴더를 파이썬 패스에 추가 ---
# hs 내부에서 'import config'가 동작하려면 
# hs 폴더 자체가 파이썬 경로에 있어야 합니다.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'hs'))
if HS_DIR not in sys.path:
    sys.path.append(HS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# hs 모듈 가져오기
try:
    from hs.model import ResNet9
    from hs.data_utils import resize_for_dl
    from hs.dataset import WaferDataset
    # hs 내에서 'import config'를 사용하므로, 
    # 이제 'hs' 디렉토리가 sys.path에 있으므로 작동할 것입니다.
    import hs.config as config
except ImportError as e:
    print(f"Error: 필수 hs 모듈을 가져올 수 없습니다. 경로를 확인해주세요. {e}")
    sys.exit(1)

app = FastAPI(title="Wafer Map Classification API")

# --- 모델 초기화 ---
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

# --- 스키마 ---
from typing import List

class Prediction(BaseModel):
    label: str
    confidence: float

class PredictionResult(BaseModel):
    top_predictions: List[Prediction]

# --- 엔드포인트 ---
@app.post("/predict", response_model=PredictionResult)
async def predict(file: UploadFile = File(...)):
    try:
        # 파일 읽기 및 이미지 변환
        content = await file.read()
        img = Image.open(BytesIO(content))
        raw_arr = np.array(img)
        
        # 전처리
        resized = resize_for_dl(raw_arr)
        X = np.expand_dims(np.stack([resized]), axis=-1)
        
        # 추론
        # 더미 라벨 사용
        y_dummy = np.array([0])
        single_dataset = WaferDataset(X, y_dummy)
        x_tensor = single_dataset.X.to(device)
        
        with torch.no_grad():
            logits = model(x_tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            
        # 상위 확률 순서대로 정렬
        sorted_indices = np.argsort(-probs)
        top_predictions = [
            {"label": reverse_label_mapping[idx], "confidence": float(probs[idx])}
            for idx in sorted_indices
        ]
        
        return {"top_predictions": top_predictions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

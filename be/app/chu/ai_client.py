import os
import httpx
from dotenv import load_dotenv
from be.app.chu.exceptions import AIServerDownError

load_dotenv()

AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://localhost:8001/predict")
TIMEOUT_SECONDS = float(os.getenv("AI_SERVER_TIMEOUT", "5.0"))

MIME_MAP = {              
    "png":  "image/png",
    "jpg":  "image/jpeg",
    "jpeg": "image/jpeg",
}

async def call_ai_server(image_bytes: bytes, ext: str) -> dict:
    mime = MIME_MAP.get(ext, "image/png")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(
                AI_SERVER_URL,
                files={"file": (f"image.{ext}", image_bytes, mime)}
            )
            response.raise_for_status()
            result = response.json()
    except (httpx.RequestError, httpx.HTTPStatusError):
        raise AIServerDownError("AI 서버 연결 실패")

    # ai/hero 서버는 {"predictions": [{class_id, class_name, confidence, image_id}, ...]}
    # 형식(확률 높은 순 top-3)으로 응답한다 - 병렬 배열 형태로 변환해서 돌려준다.
    predictions = result.get("predictions")
    required = {"class_id", "class_name", "confidence"}
    if not predictions or not all(required.issubset(p.keys()) for p in predictions):
        raise AIServerDownError("AI 서버 응답 형식 오류")

    return {
        "class_id":   [p["class_id"] for p in predictions],
        "class_name": [p["class_name"] for p in predictions],
        "confidence": [p["confidence"] for p in predictions],
    }


async def call_ai_server_mock(image_bytes: bytes, ext: str) -> dict:  
    return {
    "class_id":   [3, 1, 5],
   "class_name": ["Edge-Ring", "Center", "Scratch"],
    "confidence": [0.91, 0.06, 0.02]
}
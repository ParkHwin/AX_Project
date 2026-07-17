import os
import httpx
from dotenv import load_dotenv
from chu.exceptions import AIServerDownError

load_dotenv()  # .env 파일 읽어서 환경변수로 등록

# 하드코딩 대신 .env에서 값 가져오기
AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://localhost:8001/predict")
TIMEOUT_SECONDS = float(os.getenv("AI_SERVER_TIMEOUT", "5.0"))


async def call_ai_server(image_bytes: bytes) -> dict:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(
                AI_SERVER_URL,
                files={"file": ("image.png", image_bytes, "image/png")}
            )
            response.raise_for_status()
            result = response.json()
    except httpx.RequestError:
        raise AIServerDownError("AI 서버 연결 실패")
    except httpx.HTTPStatusError:
        raise AIServerDownError("AI 서버가 에러 응답 반환")

    return {
        "class_id": result["class_id"],
        "class_name": result["class_name"],
        "confidence": result["confidence"]
    }


async def call_ai_server_mock(image_bytes: bytes) -> dict:
    return {"class_id": 3, "class_name": "Edge_Ring", "confidence": 0.91}
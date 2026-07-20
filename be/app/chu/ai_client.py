import os
import httpx
from dotenv import load_dotenv
from chu.exceptions import AIServerDownError

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

    required = {"class_id", "class_name", "confidence"}     
    if not required.issubset(result.keys()):
        raise AIServerDownError("AI 서버 응답 형식 오류")

    return {
        "class_id":   result["class_id"],
        "class_name": result["class_name"],
        "confidence": result["confidence"]
    }


async def call_ai_server_mock(image_bytes: bytes, ext: str) -> dict:  
    return {
    "class_id":   [3, 1, 5],
    "class_name": ["Edge_Ring", "Center", "Scratch"],
    "confidence": [0.91, 0.06, 0.02]
}
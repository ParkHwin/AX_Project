import json
import os

import httpx
from dotenv import load_dotenv

from be.app.chu.exceptions import DBServerDownError

load_dotenv()

# bc/waper 백엔드 주소 (api:8000, AI:8001과 겹치지 않게 8002 사용을 기본값으로 함)
DB_API_URL = os.getenv("DB_API_URL", "http://localhost:8002")
TIMEOUT_SECONDS = float(os.getenv("DB_API_TIMEOUT", "5.0"))


async def save_to_db(
    user_num: int,
    filename: str,
    image_bytes: bytes,
    mime: str,
    class_ids: list[int],
    confidences: list[float],
    gradcam_data: str | None = None,
    gradcam_heatmap_data: str | None = None,
    process_info: list | None = None,
) -> int:
    """AI 예측 상위 3개 + GradCAM + 원인공정 데이터를 bc/waper에 저장한다."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            image_response = await client.post(
                f"{DB_API_URL}/images",
                params={"user_num": user_num},
                files={"file": (filename, image_bytes, mime)},
            )
            image_response.raise_for_status()
            image_num = image_response.json()["image_num"]

            result_response = await client.post(
                f"{DB_API_URL}/results",
                json={
                    "user_num": user_num,
                    "image_num": image_num,
                    "class_id1": class_ids[0],
                    "class_id2": class_ids[1],
                    "class_id3": class_ids[2],
                    "confidence1": confidences[0],
                    "confidence2": confidences[1],
                    "confidence3": confidences[2],
                    "gradcam_data": gradcam_data,
                    "gradcam_heatmap_data": gradcam_heatmap_data,
                    "process_info": json.dumps(process_info, ensure_ascii=False) if process_info is not None else None,
                },
            )
            result_response.raise_for_status()
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        raise DBServerDownError("DB 서버 저장 실패") from e

    return result_response.json()["result_num"]

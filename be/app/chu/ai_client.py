import httpx
from chu.exceptions import AIServerDownError

# --------------------------------------------------------
# AI 서버 연동 관련 - 아래 값들 AI팀한테 확인하고 채워넣기
# --------------------------------------------------------

# 2번: AI 서버 주소/포트 확인 필요 (로컬 개발 기준 8001 맞는지)
AI_SERVER_URL = "http://localhost:8001/predict"

TIMEOUT_SECONDS = 5.0  # AI 추론이 오래 걸리면 여기 늘리기


async def call_ai_server(image_bytes: bytes) -> dict:
    """
    프론트에서 받은 이미지를 AI 서버로 넘기고 결과 받아오는 함수.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:

            # 1번: 이미지 전달 형식 확인 필요
            # -> multipart로 그대로 보내는 걸로 일단 짜둠 (파일 그대로 전송)
            # -> AI팀이 base64/JSON으로 달라고 하면 여기 통째로 바꿔야 함
            response = await client.post(
                AI_SERVER_URL,
                files={"file": ("image.png", image_bytes, "image/png")}
            )

            response.raise_for_status()
            result = response.json()

    except httpx.RequestError:
        # 5번 확인 필요: AI 서버가 아예 안 켜져있을 때 여기로 빠짐
        raise AIServerDownError("AI 서버 연결 실패 (서버 켜져있는지 확인)")

    except httpx.HTTPStatusError:
        # 4번: AI 서버가 400/500 에러 응답할 때 - 에러 응답 형식 AI팀한테 확인 후
        # 아래 raise 부분 그 형식에 맞게 수정
        raise AIServerDownError("AI 서버가 에러 응답 반환")

    # 3번: 필드명 확인 필요 - class_id / class_name / confidence
    # AI팀 응답이 다른 이름으로 오면 (예: predicted_class 등) 여기서 매핑
    return {
        "class_id": result["class_id"],
        "class_name": result["class_name"],
        "confidence": result["confidence"]
    }


# --------------------------------------------------------
# 목업용 - AI 서버 아직 준비 안됐을 때 임시로 이거 쓰기
# 위 call_ai_server 대신 이 함수를 router.py에서 부르면 됨
# --------------------------------------------------------
async def call_ai_server_mock(image_bytes: bytes) -> dict:
    return {
        "class_id": 3,
        "class_name": "Edge_Ring",
        "confidence": 0.91
    }
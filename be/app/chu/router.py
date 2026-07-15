import uuid
from fastapi import APIRouter, UploadFile, HTTPException

# 아직 AI 서버 준비 안됐으면 mock 쓰고, 준비되면 아래 줄만 바꾸기
from chu.ai_client import call_ai_server_mock as call_ai_server
# from chu.ai_client import call_ai_server  # <- 실제 연동 시 이걸로 교체
from chu.schemas import UploadResponse
from chu.exceptions import AIServerDownError, InvalidImageFormatError

router = APIRouter()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


@router.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile):
    # 1번 : 파일 형식 검증
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다: {ext}"
        )

    # 2번 : 이미지 읽기
    image_bytes = await file.read()

    # 3번 : AI 서버 호출 (현재는 목업)
    try:
        result = await call_ai_server(image_bytes)
    except AIServerDownError:
        raise HTTPException(status_code=503, detail="AI 서버 연결 실패")

    # 4번 : 응답 변환
    return UploadResponse(
        image_id=str(uuid.uuid4()),
        class_id=result["class_id"],
        class_name=result["class_name"],
        confidence=result["confidence"]
    )
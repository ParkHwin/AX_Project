import uuid
from fastapi import APIRouter, UploadFile, HTTPException

# 아직 AI 서버 준비 안됐으면 mock 쓰고, 준비되면 아래 줄만 바꾸기
from chu.ai_client import call_ai_server_mock as call_ai_server
# from chu.ai_client import call_ai_server  # <- 실제 연동 시 이걸로 교체
from chu.schemas import UploadResponse
from chu.exceptions import AIServerDownError, InvalidImageFormatError, FileTooLargeError
from PIL import Image
import io

router = APIRouter()

ALLOWED_EXTENSIONS = {"png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB 제한 - 필요하면 숫자만 조정


@router.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile):
    # 1번 케이스: 파일 자체가 없는 경우
    if not file:
        raise HTTPException(status_code=400, detail="파일이 첨부되지 않았습니다")

    # 2번 케이스: 확장자 검증
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식: {ext}")

    image_bytes = await file.read()

    # 3번 케이스: 용량 초과
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="파일 용량이 너무 큽니다 (최대 5MB)")

    # 4번 케이스: 확장자는 맞는데 실제로 열리지 않는 손상된 이미지
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.load()
    except Exception as e:
        print(f"이미지 검증 실패 원인: {e}")
        raise HTTPException(status_code=400, detail="손상되었거나 유효하지 않은 이미지 파일입니다")
    if img.mode != "P":
        raise HTTPException(status_code=400, detail="웨이퍼맵 PNG(팔레트 모드)만 허용됩니다")
    # 5번 케이스: AI 서버 다운/타임아웃
    try:
        result = await call_ai_server(image_bytes, ext)
    except AIServerDownError:
        raise HTTPException(status_code=503, detail="AI 서버 연결 실패")

    return UploadResponse(
        image_id=str(uuid.uuid4()),
        class_id=result["class_id"],
        class_name=result["class_name"],
        confidence=result["confidence"]
    )
import pytest
import io
from PIL import Image


@pytest.fixture
def valid_image_bytes():
    """테스트용 정상 이미지 바이트 생성 (실제 파일 없이 메모리에서 만듦)"""
    img = Image.new("RGB", (64, 64), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


@pytest.fixture
def invalid_image_bytes():
    """확장자는 이미지지만 실제로는 깨진 파일"""
    return b"this is not a real image"
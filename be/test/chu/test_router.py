from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_upload_success(valid_image_bytes):
    # 정상 케이스: 200과 응답 필드 확인
    response = client.post(
        "/api/upload",
        files={"file": ("test.png", valid_image_bytes, "image/png")}
    )
    assert response.status_code == 200
    body = response.json()
    assert "class_name" in body
    assert "confidence" in body


def test_upload_invalid_extension(valid_image_bytes):
    # 지원 안 하는 확장자 -> 400
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", valid_image_bytes, "text/plain")}
    )
    assert response.status_code == 400


def test_upload_corrupted_image(invalid_image_bytes):
    # 확장자는 맞지만 손상된 파일 -> 400
    response = client.post(
        "/api/upload",
        files={"file": ("test.png", invalid_image_bytes, "image/png")}
    )
    assert response.status_code == 400


def test_upload_too_large():
    # 용량 초과 -> 413
    big_bytes = b"0" * (6 * 1024 * 1024)  # 6MB 더미
    response = client.post(
        "/api/upload",
        files={"file": ("test.png", big_bytes, "image/png")}
    )
    assert response.status_code == 413
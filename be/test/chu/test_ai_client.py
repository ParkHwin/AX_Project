import pytest
from chu.ai_client import call_ai_server_mock


@pytest.mark.asyncio
async def test_mock_ai_response_format():
    # 목업 응답이 우리가 정한 필드명 규격을 지키는지 확인
    result = await call_ai_server_mock(b"dummy")
    assert "class_id" in result
    assert "class_name" in result
    assert "confidence" in result
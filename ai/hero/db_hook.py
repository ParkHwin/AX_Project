"""
DB 연동 지점.
팀원이 이 파일의 save_prediction() 함수 내부만 구현하면 됩니다.
server.py 쪽 로직은 건드릴 필요 없습니다.

예시 구현 방향:
    from sqlalchemy.orm import Session
    def save_prediction(db: Session, filename: str, predictions: list[dict]) -> int:
        ... DB에 저장하고 image_id(PK) 반환 ...
"""

from typing import List, Dict, Optional


def save_prediction(filename: str, predictions: List[Dict]) -> Optional[int]:
    """
    filename: 업로드된 원본 파일명
    predictions: [{"class_id": int, "class_name": str, "confidence": float}, ...] (top-k)

    반환값: DB에 저장 후 생성된 image_id (아직 미구현이므로 None 반환)
    """
    # TODO: 팀원이 여기에 실제 DB 저장 로직 구현
    return None
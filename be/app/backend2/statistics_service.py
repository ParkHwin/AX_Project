from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from bc.waper.app.models import Result
from be.app.backend2.analysis_service import get_class_name


# class_id 8은 정상 클래스인 none입니다.
NORMAL_CLASS_ID = 8


def get_analysis_statistics(
    db: Session,
    user_num: int,
) -> dict:
    """특정 사용자의 분석 결과 통계를 조회합니다."""

    try:
        # 해당 사용자의 분석 결과만 조회 대상으로 사용합니다.
        base_query = db.query(Result).filter(
            Result.user_num == user_num,
        )

        # 전체 분석 결과 개수
        total_count = base_query.count()

        # class_id가 8이면 정상 결과입니다.
        normal_count = (
            base_query
            .filter(Result.detect == NORMAL_CLASS_ID)
            .count()
        )

        # class_id가 8이 아니면 결함 결과입니다.
        defect_count = (
            base_query
            .filter(Result.detect != NORMAL_CLASS_ID)
            .count()
        )

        # 결함 class_id별 결과 개수를 집계합니다.
        defect_type_rows = (
            db.query(
                Result.detect,
                func.count(Result.result_num),
            )
            .filter(
                Result.user_num == user_num,
                Result.detect != NORMAL_CLASS_ID,
            )
            .group_by(Result.detect)
            .order_by(
                func.count(Result.result_num).desc(),
            )
            .all()
        )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "통계 조회 중 DB 오류가 발생했습니다.",
            },
        )

    defect_type_counts = [
        {
            "class_id": class_id,
            "class_name": get_class_name(class_id),
            "count": count,
        }
        for class_id, count in defect_type_rows
    ]

    return {
        "total_count": total_count,
        "normal_count": normal_count,
        "defect_count": defect_count,
        "defect_type_counts": defect_type_counts,
    }
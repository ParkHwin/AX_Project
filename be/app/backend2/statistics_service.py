from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from bc.waper.app.models import Result


def get_analysis_statistics(
    db: Session,
    user_num: int,
) -> dict:
    """특정 사용자의 분석 결과 통계를 조회합니다."""

    try:
        # 해당 사용자의 결과만 대상으로 합니다.
        base_query = db.query(Result).filter(
            Result.user_num == user_num,
        )

        # 전체 분석 결과 개수
        total_count = base_query.count()

        # 정상 결과 개수
        normal_count = (
            base_query
            .filter(Result.detect == "정상")
            .count()
        )

        # 불량 결과 개수
        defect_count = (
            base_query
            .filter(Result.detect == "불량")
            .count()
        )

        # 불량 종류별 결과 개수
        defect_type_rows = (
            db.query(
                Result.detect_type,
                func.count(Result.result_num),
            )
            .filter(
                Result.user_num == user_num,
                Result.detect == "불량",
                Result.detect_type.isnot(None),
            )
            .group_by(Result.detect_type)
            .order_by(
                func.count(Result.result_num).desc()
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
            "defect_type": defect_type,
            "count": count,
        }
        for defect_type, count in defect_type_rows
    ]

    return {
        "total_count": total_count,
        "normal_count": normal_count,
        "defect_count": defect_count,
        "defect_type_counts": defect_type_counts,
    }
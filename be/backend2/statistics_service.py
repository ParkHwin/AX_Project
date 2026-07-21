# from fastapi import HTTPException
# from sqlalchemy import func
# from sqlalchemy.exc import SQLAlchemyError
# from sqlalchemy.orm import Session

# from bc.waper.app.models import Result
# from be.app.backend2.analysis_service import get_class_name


# # class_id 8은 정상 클래스인 none입니다.
# NORMAL_CLASS_ID = 8


# def get_analysis_statistics(
#     db: Session,
#     user_num: int,
# ) -> dict:
#     """특정 사용자의 분석 결과 통계를 조회합니다."""

#     try:
#         # 해당 사용자의 분석 결과만 조회 대상으로 사용합니다.
#         base_query = db.query(Result).filter(
#             Result.user_num == user_num,
#         )

#         # 전체 분석 결과 개수
#         total_count = base_query.count()

#         # class_id가 8이면 정상 결과입니다.
#         normal_count = (
#             base_query
#             .filter(Result.detect == NORMAL_CLASS_ID)
#             .count()
#         )

#         # class_id가 8이 아니면 결함 결과입니다.
#         defect_count = (
#             base_query
#             .filter(Result.detect != NORMAL_CLASS_ID)
#             .count()
#         )

#         # 결함 class_id별 결과 개수를 집계합니다.
#         defect_type_rows = (
#             db.query(
#                 Result.detect,
#                 func.count(Result.result_num),
#             )
#             .filter(
#                 Result.user_num == user_num,
#                 Result.detect != NORMAL_CLASS_ID,
#             )
#             .group_by(Result.detect)
#             .order_by(
#                 func.count(Result.result_num).desc(),
#             )
#             .all()
#         )

#     except SQLAlchemyError:
#         db.rollback()

#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "code": "database_error",
#                 "message": "통계 조회 중 DB 오류가 발생했습니다.",
#             },
#         )

#     defect_type_counts = [
#         {
#             "class_id": class_id,
#             "class_name": get_class_name(class_id),
#             "count": count,
#         }
#         for class_id, count in defect_type_rows
#     ]

#     return {
#         "total_count": total_count,
#         "normal_count": normal_count,
#         "defect_count": defect_count,
#         "defect_type_counts": defect_type_counts,
#     }

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from bc.waper.app.models import Result
from be.backend2.analysis_service import (
    get_class_name,
    get_result_status,
)


# class_id1이 8(none)이면 최종 판정은 PASS입니다.
NORMAL_CLASS_ID = 8

# 검사 이력 화면의 신뢰도 추이 그래프에 표시할 최근 결과 개수입니다.
CONFIDENCE_TREND_LIMIT = 10


def get_analysis_statistics(
    db: Session,
    user_num: int,
) -> dict:
    """
    특정 사용자의 전체 분석 통계를 조회합니다.

    최종 판정과 클래스별 통계는 1위 예측인 class_id1을 기준으로 계산합니다.
    2위와 3위 예측은 참고 정보이므로 통계에 포함하지 않습니다.
    """

    try:
        # -------------------------------------------------
        # 1. 사용자별 전체 결과 조회 조건
        # -------------------------------------------------
        base_query = db.query(Result).filter(
            Result.user_num == user_num,
        )

        # 전체 검사 건수
        total_count = base_query.count()

        # -------------------------------------------------
        # 2. PASS / FAIL 건수
        # -------------------------------------------------

        # class_id1이 8(none)이면 PASS입니다.
        pass_count = (
            base_query
            .filter(Result.class_id1 == NORMAL_CLASS_ID)
            .count()
        )

        # class_id1이 0~7이면 FAIL입니다.
        fail_count = (
            base_query
            .filter(Result.class_id1 != NORMAL_CLASS_ID)
            .count()
        )

        # -------------------------------------------------
        # 3. 평균 신뢰도
        # -------------------------------------------------

        # 1위 예측 confidence1의 평균을 계산합니다.
        average_confidence_value = (
            db.query(func.avg(Result.confidence1))
            .filter(
                Result.user_num == user_num,
                Result.confidence1.isnot(None),
            )
            .scalar()
        )

        # -------------------------------------------------
        # 4. 결함 클래스별 검사 건수
        # -------------------------------------------------

        # 최종 판정인 class_id1을 기준으로만 집계합니다.
        # 정상 클래스인 8(none)은 결함 종류 통계에서 제외합니다.
        defect_type_rows = (
            db.query(
                Result.class_id1,
                func.count(Result.result_num),
            )
            .filter(
                Result.user_num == user_num,
                Result.class_id1 != NORMAL_CLASS_ID,
            )
            .group_by(Result.class_id1)
            .order_by(
                func.count(Result.result_num).desc(),
                Result.class_id1.asc(),
            )
            .all()
        )

        # -------------------------------------------------
        # 5. 최근 신뢰도 추이
        # -------------------------------------------------

        # 최근 결과를 먼저 가져옵니다.
        recent_confidence_results = (
            db.query(Result)
            .filter(
                Result.user_num == user_num,
                Result.confidence1.isnot(None),
            )
            .order_by(
                Result.detime.desc(),
                Result.result_num.desc(),
            )
            .limit(CONFIDENCE_TREND_LIMIT)
            .all()
        )

        # -------------------------------------------------
        # 6. 가장 최근 분석 결과
        # -------------------------------------------------

        latest_result = (
            db.query(Result)
            .filter(Result.user_num == user_num)
            .order_by(
                Result.detime.desc(),
                Result.result_num.desc(),
            )
            .first()
        )

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "통계 조회 중 DB 오류가 발생했습니다.",
            },
        ) from error

    # -------------------------------------------------
    # 7. 계산값 만들기
    # -------------------------------------------------

    # 데이터가 없을 때 0으로 나누는 오류가 발생하지 않도록 처리합니다.
    defect_rate = (
        round((fail_count / total_count) * 100, 2)
        if total_count > 0
        else 0.0
    )

    average_confidence = (
        round(float(average_confidence_value), 2)
        if average_confidence_value is not None
        else 0.0
    )

    # -------------------------------------------------
    # 8. 결함 클래스별 응답 변환
    # -------------------------------------------------

    defect_type_counts = [
        {
            "class_id": class_id,
            "class_name": get_class_name(class_id),
            "count": count,
        }
        for class_id, count in defect_type_rows
    ]

    # DB에서는 최신순으로 조회했지만,
    # 그래프는 오래된 값부터 최신 값 순서로 보여주는 편이 자연스럽습니다.
    confidence_trend = [
        {
            "analysis_id": result.result_num,
            "image_name": result.image_name,
            "confidence": float(result.confidence1),
            "created_at": result.detime,
        }
        for result in reversed(recent_confidence_results)
    ]

    # 결과가 하나도 없으면 latest_result는 null로 반환합니다.
    latest_result_item = None

    if latest_result is not None:
        latest_result_item = {
            "analysis_id": latest_result.result_num,
            "image_id": latest_result.image_num,
            "image_name": latest_result.image_name,
            "top_class_id": latest_result.class_id1,
            "top_class_name": (
                latest_result.class_name1
                or get_class_name(latest_result.class_id1)
            ),
            "confidence": (
                float(latest_result.confidence1)
                if latest_result.confidence1 is not None
                else 0.0
            ),
            "result_status": get_result_status(
                latest_result.class_id1,
            ),
            "created_at": latest_result.detime,
        }

    return {
        "total_count": total_count,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "defect_rate": defect_rate,
        "average_confidence": average_confidence,
        "defect_type_counts": defect_type_counts,
        "confidence_trend": confidence_trend,
        "latest_result": latest_result_item,
    }
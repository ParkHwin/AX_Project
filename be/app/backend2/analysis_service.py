# from math import ceil

# from fastapi import HTTPException
# from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# from sqlalchemy.orm import Session

# from bc.waper.app.models import Result
# from be.app.backend2.schemas import (
#     AnalysisCreateRequest,
#     AnalysisUpdateRequest,
# )


# # AI팀에서 확정한 label_mapping.json과 반드시 동일해야 합니다.
# CLASS_NAME_BY_ID = {
#     0: "Center",
#     1: "Donut",
#     2: "Edge-Ring",
#     3: "Edge-Loc",
#     4: "Loc",
#     5: "Random",
#     6: "Scratch",
#     7: "Near-full",
#     8: "none",
# }


# def get_class_name(class_id: int) -> str | None:
#     """클래스 번호를 클래스 이름으로 변환합니다."""

#     return CLASS_NAME_BY_ID.get(class_id)


# def convert_result_to_dict(result: Result) -> dict:
#     """DB Result 객체를 API 응답 형식으로 변환합니다."""

#     class_id = result.detect

#     return {
#         "analysis_id": result.result_num,
#         "user_num": result.user_num,
#         "image_id": result.image_num,
#         "class_id": class_id,
#         "class_name": get_class_name(class_id),
#         "created_at": result.detime,
#     }


# def find_result_or_404(
#     db: Session,
#     analysis_id: int,
#     user_num: int,
# ) -> Result:
#     """사용자의 분석 결과를 조회하고, 없으면 404 오류를 발생시킵니다."""

#     try:
#         result = (
#             db.query(Result)
#             .filter(
#                 Result.result_num == analysis_id,
#                 Result.user_num == user_num,
#             )
#             .first()
#         )

#     except SQLAlchemyError:
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "code": "database_error",
#                 "message": "분석 결과 조회 중 DB 오류가 발생했습니다.",
#             },
#         )

#     if result is None:
#         raise HTTPException(
#             status_code=404,
#             detail={
#                 "code": "analysis_not_found",
#                 "message": "분석 결과를 찾을 수 없습니다.",
#             },
#         )

#     return result


# def create_analysis(
#     db: Session,
#     request: AnalysisCreateRequest,
# ) -> dict:
#     """새로운 분석 결과를 저장합니다."""

#     result = Result(
#         user_num=request.user_num,
#         image_num=request.image_id,

#         # API의 class_id를 DB Result.detect에 저장합니다.
#         detect=request.class_id,
#     )

#     try:
#         db.add(result)
#         db.commit()
#         db.refresh(result)

#     except IntegrityError:
#         db.rollback()

#         raise HTTPException(
#             status_code=400,
#             detail={
#                 "code": "invalid_user_or_image",
#                 "message": "존재하지 않는 사용자 또는 이미지입니다.",
#             },
#         )

#     except SQLAlchemyError:
#         db.rollback()

#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "code": "database_error",
#                 "message": "분석 결과 저장 중 DB 오류가 발생했습니다.",
#             },
#         )

#     return convert_result_to_dict(result)


# def get_analysis_list(
#     db: Session,
#     user_num: int,
#     page: int,
#     size: int,
# ) -> dict:
#     """사용자의 분석 결과 목록을 최신순으로 조회합니다."""

#     try:
#         query = db.query(Result).filter(
#             Result.user_num == user_num,
#         )

#         total_count = query.count()
#         offset = (page - 1) * size

#         results = (
#             query.order_by(Result.detime.desc())
#             .offset(offset)
#             .limit(size)
#             .all()
#         )

#     except SQLAlchemyError:
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "code": "database_error",
#                 "message": "분석 결과 목록 조회 중 DB 오류가 발생했습니다.",
#             },
#         )

#     total_pages = (
#         ceil(total_count / size)
#         if total_count > 0
#         else 0
#     )

#     return {
#         "items": [
#             convert_result_to_dict(result)
#             for result in results
#         ],
#         "page": page,
#         "size": size,
#         "total_count": total_count,
#         "total_pages": total_pages,
#     }


# def get_analysis_detail(
#     db: Session,
#     analysis_id: int,
#     user_num: int,
# ) -> dict:
#     """분석 결과 한 건을 조회합니다."""

#     result = find_result_or_404(
#         db=db,
#         analysis_id=analysis_id,
#         user_num=user_num,
#     )

#     return convert_result_to_dict(result)


# def update_analysis(
#     db: Session,
#     analysis_id: int,
#     user_num: int,
#     request: AnalysisUpdateRequest,
# ) -> dict:
#     """분석 결과의 클래스 번호를 수정합니다."""

#     if request.class_id is None:
#         raise HTTPException(
#             status_code=400,
#             detail={
#                 "code": "empty_update_request",
#                 "message": "수정할 class_id를 입력해야 합니다.",
#             },
#         )

#     result = find_result_or_404(
#         db=db,
#         analysis_id=analysis_id,
#         user_num=user_num,
#     )

#     # API의 class_id를 DB Result.detect에 저장합니다.
#     result.detect = request.class_id

#     try:
#         db.commit()
#         db.refresh(result)

#     except SQLAlchemyError:
#         db.rollback()

#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "code": "database_error",
#                 "message": "분석 결과 수정 중 DB 오류가 발생했습니다.",
#             },
#         )

#     return convert_result_to_dict(result)


# def delete_analysis(
#     db: Session,
#     analysis_id: int,
#     user_num: int,
# ) -> None:
#     """분석 결과 한 건을 삭제합니다."""

#     result = find_result_or_404(
#         db=db,
#         analysis_id=analysis_id,
#         user_num=user_num,
#     )

#     try:
#         db.delete(result)
#         db.commit()

#     except SQLAlchemyError:
#         db.rollback()

#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "code": "database_error",
#                 "message": "분석 결과 삭제 중 DB 오류가 발생했습니다.",
#             },
#         )

###

from math import ceil

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from bc.waper.app.models import Result
from be.app.backend2.schemas import (
    AnalysisCreateRequest,
    AnalysisUpdateRequest,
)


# AI팀에서 확정한 label_mapping.json과 반드시 동일해야 합니다.
CLASS_NAME_BY_ID = {
    0: "Center",
    1: "Donut",
    2: "Edge-Loc",
    3: "Edge-Ring",
    4: "Loc",
    5: "Near-full",
    6: "Random",
    7: "Scratch",
    8: "none",
}


def get_class_name(class_id: int) -> str | None:
    """클래스 번호를 클래스 이름으로 변환합니다."""

    return CLASS_NAME_BY_ID.get(class_id)


def convert_result_to_dict(result: Result) -> dict:
    """DB Result 객체를 API 응답 형식으로 변환합니다."""

    class_id = result.detect

    return {
        "result_num": result.result_num,
        "user_num": result.user_num,
        "image_num": result.image_num,
        "class_id": class_id,
        "class_name": get_class_name(class_id),
        "detime": result.detime,
    }


def find_result_or_404(
    db: Session,
    result_num: int,
    user_num: int,
) -> Result:
    """사용자의 분석 결과를 조회하고, 없으면 404 오류를 발생시킵니다."""

    try:
        result = (
            db.query(Result)
            .filter(
                Result.result_num == result_num,
                Result.user_num == user_num,
            )
            .first()
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "분석 결과 조회 중 DB 오류가 발생했습니다.",
            },
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "analysis_not_found",
                "message": "분석 결과를 찾을 수 없습니다.",
            },
        )

    return result


def create_analysis(
    db: Session,
    request: AnalysisCreateRequest,
) -> dict:
    """새로운 분석 결과를 저장합니다."""

    result = Result(
        user_num=request.user_num,
        image_num=request.image_num,

        # API의 class_id를 DB Result.detect에 저장합니다.
        detect=request.class_id,
    )

    try:
        db.add(result)
        db.commit()
        db.refresh(result)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_user_or_image",
                "message": "존재하지 않는 사용자 또는 이미지입니다.",
            },
        )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "분석 결과 저장 중 DB 오류가 발생했습니다.",
            },
        )

    return convert_result_to_dict(result)


def get_analysis_list(
    db: Session,
    user_num: int,
    page: int,
    size: int,
) -> dict:
    """사용자의 분석 결과 목록을 최신순으로 조회합니다."""

    try:
        query = db.query(Result).filter(
            Result.user_num == user_num,
        )

        total_count = query.count()
        offset = (page - 1) * size

        results = (
            query.order_by(Result.detime.desc())
            .offset(offset)
            .limit(size)
            .all()
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "분석 결과 목록 조회 중 DB 오류가 발생했습니다.",
            },
        )

    total_pages = (
        ceil(total_count / size)
        if total_count > 0
        else 0
    )

    return {
        "items": [
            convert_result_to_dict(result)
            for result in results
        ],
        "page": page,
        "size": size,
        "total_count": total_count,
        "total_pages": total_pages,
    }


def get_analysis_detail(
    db: Session,
    result_num: int,
    user_num: int,
) -> dict:
    """분석 결과 한 건을 조회합니다."""

    result = find_result_or_404(
        db=db,
        result_num=result_num,
        user_num=user_num,
    )

    return convert_result_to_dict(result)


def update_analysis(
    db: Session,
    result_num: int,
    user_num: int,
    request: AnalysisUpdateRequest,
) -> dict:
    """분석 결과의 클래스 번호를 수정합니다."""

    if request.class_id is None:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "empty_update_request",
                "message": "수정할 class_id를 입력해야 합니다.",
            },
        )

    result = find_result_or_404(
        db=db,
        result_num=result_num,
        user_num=user_num,
    )

    # API의 class_id를 DB Result.detect에 저장합니다.
    result.detect = request.class_id

    try:
        db.commit()
        db.refresh(result)

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "분석 결과 수정 중 DB 오류가 발생했습니다.",
            },
        )

    return convert_result_to_dict(result)


def delete_analysis(
    db: Session,
    result_num: int,
    user_num: int,
) -> None:
    """분석 결과 한 건을 삭제합니다."""

    result = find_result_or_404(
        db=db,
        result_num=result_num,
        user_num=user_num,
    )

    try:
        db.delete(result)
        db.commit()

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "분석 결과 삭제 중 DB 오류가 발생했습니다.",
            },
        )
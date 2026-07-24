# # from math import ceil

# # from fastapi import HTTPException
# # from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# # from sqlalchemy.orm import Session

# # from bc.waper.app.models import Result
# # from be.app.backend2.schemas import (
# #     AnalysisCreateRequest,
# #     AnalysisUpdateRequest,
# # )


# # # AI팀에서 확정한 label_mapping.json과 반드시 동일해야 합니다.
# # CLASS_NAME_BY_ID = {
# #     0: "Center",
# #     1: "Donut",
# #     2: "Edge-Ring",
# #     3: "Edge-Loc",
# #     4: "Loc",
# #     5: "Random",
# #     6: "Scratch",
# #     7: "Near-full",
# #     8: "none",
# # }


# # def get_class_name(class_id: int) -> str | None:
# #     """클래스 번호를 클래스 이름으로 변환합니다."""

# #     return CLASS_NAME_BY_ID.get(class_id)


# # def convert_result_to_dict(result: Result) -> dict:
# #     """DB Result 객체를 API 응답 형식으로 변환합니다."""

# #     class_id = result.detect

# #     return {
# #         "analysis_id": result.result_num,
# #         "user_num": result.user_num,
# #         "image_id": result.image_num,
# #         "class_id": class_id,
# #         "class_name": get_class_name(class_id),
# #         "created_at": result.detime,
# #     }


# # def find_result_or_404(
# #     db: Session,
# #     analysis_id: int,
# #     user_num: int,
# # ) -> Result:
# #     """사용자의 분석 결과를 조회하고, 없으면 404 오류를 발생시킵니다."""

# #     try:
# #         result = (
# #             db.query(Result)
# #             .filter(
# #                 Result.result_num == analysis_id,
# #                 Result.user_num == user_num,
# #             )
# #             .first()
# #         )

# #     except SQLAlchemyError:
# #         raise HTTPException(
# #             status_code=500,
# #             detail={
# #                 "code": "database_error",
# #                 "message": "분석 결과 조회 중 DB 오류가 발생했습니다.",
# #             },
# #         )

# #     if result is None:
# #         raise HTTPException(
# #             status_code=404,
# #             detail={
# #                 "code": "analysis_not_found",
# #                 "message": "분석 결과를 찾을 수 없습니다.",
# #             },
# #         )

# #     return result


# # def create_analysis(
# #     db: Session,
# #     request: AnalysisCreateRequest,
# # ) -> dict:
# #     """새로운 분석 결과를 저장합니다."""

# #     result = Result(
# #         user_num=request.user_num,
# #         image_num=request.image_id,

# #         # API의 class_id를 DB Result.detect에 저장합니다.
# #         detect=request.class_id,
# #     )

# #     try:
# #         db.add(result)
# #         db.commit()
# #         db.refresh(result)

# #     except IntegrityError:
# #         db.rollback()

# #         raise HTTPException(
# #             status_code=400,
# #             detail={
# #                 "code": "invalid_user_or_image",
# #                 "message": "존재하지 않는 사용자 또는 이미지입니다.",
# #             },
# #         )

# #     except SQLAlchemyError:
# #         db.rollback()

# #         raise HTTPException(
# #             status_code=500,
# #             detail={
# #                 "code": "database_error",
# #                 "message": "분석 결과 저장 중 DB 오류가 발생했습니다.",
# #             },
# #         )

# #     return convert_result_to_dict(result)


# # def get_analysis_list(
# #     db: Session,
# #     user_num: int,
# #     page: int,
# #     size: int,
# # ) -> dict:
# #     """사용자의 분석 결과 목록을 최신순으로 조회합니다."""

# #     try:
# #         query = db.query(Result).filter(
# #             Result.user_num == user_num,
# #         )

# #         total_count = query.count()
# #         offset = (page - 1) * size

# #         results = (
# #             query.order_by(Result.detime.desc())
# #             .offset(offset)
# #             .limit(size)
# #             .all()
# #         )

# #     except SQLAlchemyError:
# #         raise HTTPException(
# #             status_code=500,
# #             detail={
# #                 "code": "database_error",
# #                 "message": "분석 결과 목록 조회 중 DB 오류가 발생했습니다.",
# #             },
# #         )

# #     total_pages = (
# #         ceil(total_count / size)
# #         if total_count > 0
# #         else 0
# #     )

# #     return {
# #         "items": [
# #             convert_result_to_dict(result)
# #             for result in results
# #         ],
# #         "page": page,
# #         "size": size,
# #         "total_count": total_count,
# #         "total_pages": total_pages,
# #     }


# # def get_analysis_detail(
# #     db: Session,
# #     analysis_id: int,
# #     user_num: int,
# # ) -> dict:
# #     """분석 결과 한 건을 조회합니다."""

# #     result = find_result_or_404(
# #         db=db,
# #         analysis_id=analysis_id,
# #         user_num=user_num,
# #     )

# #     return convert_result_to_dict(result)


# # def update_analysis(
# #     db: Session,
# #     analysis_id: int,
# #     user_num: int,
# #     request: AnalysisUpdateRequest,
# # ) -> dict:
# #     """분석 결과의 클래스 번호를 수정합니다."""

# #     if request.class_id is None:
# #         raise HTTPException(
# #             status_code=400,
# #             detail={
# #                 "code": "empty_update_request",
# #                 "message": "수정할 class_id를 입력해야 합니다.",
# #             },
# #         )

# #     result = find_result_or_404(
# #         db=db,
# #         analysis_id=analysis_id,
# #         user_num=user_num,
# #     )

# #     # API의 class_id를 DB Result.detect에 저장합니다.
# #     result.detect = request.class_id

# #     try:
# #         db.commit()
# #         db.refresh(result)

# #     except SQLAlchemyError:
# #         db.rollback()

# #         raise HTTPException(
# #             status_code=500,
# #             detail={
# #                 "code": "database_error",
# #                 "message": "분석 결과 수정 중 DB 오류가 발생했습니다.",
# #             },
# #         )

# #     return convert_result_to_dict(result)


# # def delete_analysis(
# #     db: Session,
# #     analysis_id: int,
# #     user_num: int,
# # ) -> None:
# #     """분석 결과 한 건을 삭제합니다."""

# #     result = find_result_or_404(
# #         db=db,
# #         analysis_id=analysis_id,
# #         user_num=user_num,
# #     )

# #     try:
# #         db.delete(result)
# #         db.commit()

# #     except SQLAlchemyError:
# #         db.rollback()

# #         raise HTTPException(
# #             status_code=500,
# #             detail={
# #                 "code": "database_error",
# #                 "message": "분석 결과 삭제 중 DB 오류가 발생했습니다.",
# #             },
# #         )

# ###

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
#     2: "Edge-Loc",
#     3: "Edge-Ring",
#     4: "Loc",
#     5: "Near-full",
#     6: "Random",
#     7: "Scratch",
#     8: "none",
# }


# def get_class_name(class_id: int) -> str | None:
#     """클래스 번호를 클래스 이름으로 변환합니다."""

#     return CLASS_NAME_BY_ID.get(class_id)


# def convert_result_to_dict(result: Result) -> dict:
#     """DB Result 객체를 API 응답 형식으로 변환합니다."""

#     class_id = result.detect

#     return {
#         "result_num": result.result_num,
#         "user_num": result.user_num,
#         "image_num": result.image_num,
#         "class_id": class_id,
#         "class_name": get_class_name(class_id),
#         "detime": result.detime,
#     }


# def find_result_or_404(
#     db: Session,
#     result_num: int,
#     user_num: int,
# ) -> Result:
#     """사용자의 분석 결과를 조회하고, 없으면 404 오류를 발생시킵니다."""

#     try:
#         result = (
#             db.query(Result)
#             .filter(
#                 Result.result_num == result_num,
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
#         image_num=request.image_num,

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
#     result_num: int,
#     user_num: int,
# ) -> dict:
#     """분석 결과 한 건을 조회합니다."""

#     result = find_result_or_404(
#         db=db,
#         result_num=result_num,
#         user_num=user_num,
#     )

#     return convert_result_to_dict(result)


# def update_analysis(
#     db: Session,
#     result_num: int,
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
#         result_num=result_num,
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
#     result_num: int,
#     user_num: int,
# ) -> None:
#     """분석 결과 한 건을 삭제합니다."""

#     result = find_result_or_404(
#         db=db,
#         result_num=result_num,
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

import json
from math import ceil

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from bc.waper.app.main import LABEL_MAPPING
from bc.waper.app.models import Result
from be.app.sg.schemas import (
    AnalysisCreateRequest,
    AnalysisUpdateRequest,
)


# AI팀의 ai/hs/label_mapping.json과 동일한 클래스 매핑입니다.
# CLASS_NAME_BY_ID = {
#     0: "Center",
#     1: "Donut",
#     2: "Edge-Loc",
#     3: "Edge-Ring",
#     4: "Loc",
#     5: "Near-full",
#     6: "Random",
#     7: "Scratch",
#     8: "none",
# }

NORMAL_CLASS_ID = 8

 
   # label_mapping.json이 바뀌어도 8번이 "none"이라는 전제가 깨지면
   # 서버 시작 시점에 바로 알 수 있도록 검증합니다.
assert LABEL_MAPPING.get(str(NORMAL_CLASS_ID)) == "none", (
    f"label_mapping.json의 {NORMAL_CLASS_ID}번이 'none'이 아닙니다: "
    f"{LABEL_MAPPING.get(str(NORMAL_CLASS_ID))!r}"
    )

def get_class_name(class_id: int) -> str:
    """
    클래스 번호를 사람이 읽을 수 있는 이름으로 변환합니다.
    """

    return LABEL_MAPPING.get(str(class_id), "Unknown")


def get_result_status(class_id: int) -> str:
    """
    1위 클래스 번호를 기준으로 PASS 또는 FAIL을 결정합니다.

    class_id가 8(none)이면 정상인 PASS,
    나머지 0~7이면 결함인 FAIL입니다.
    """

    if class_id == NORMAL_CLASS_ID:
        return "PASS"

    return "FAIL"


def validate_top_predictions(top_predictions: list) -> None:
    """
    Top 3 요청에 같은 클래스가 중복으로 들어오는 것을 방지합니다.

    예:
    1위 none
    2위 Donut
    3위 none

    위와 같은 데이터는 잘못된 Top 3 결과로 판단합니다.
    """

    class_ids = [
        prediction.class_id
        for prediction in top_predictions
    ]

    if len(set(class_ids)) != len(class_ids):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "duplicate_prediction_class",
                "message": "Top 3 예측에는 같은 클래스가 중복될 수 없습니다.",
            },
        )


def convert_prediction_to_dict(
    rank: int,
    class_id: int,
    class_name: str | None,
    confidence: float | None,
) -> dict:
    """
    DB의 순위별 컬럼을 프론트가 사용하기 쉬운 예측 객체로 변환합니다.
    """

    return {
        "rank": rank,
        "class_id": class_id,
        "class_name": class_name or get_class_name(class_id),
        "confidence": (
            float(confidence)
            if confidence is not None
            else 0.0
        ),
    }


def convert_result_to_list_item(result: Result) -> dict:
    """
    DB Result 객체를 검사 이력 목록용 응답으로 변환합니다.

    목록 화면에서는 1위 예측만 반환합니다.
    """

    top_class_id = result.class_id1

    return {
        "analysis_id": result.result_num,
        "user_num": result.user_num,
        "image_id": result.image_num,
        "image_name": result.image_name,
        "top_class_id": top_class_id,
        "top_class_name": (
            result.class_name1
            or get_class_name(top_class_id)
        ),
        "confidence": (
            float(result.confidence1)
            if result.confidence1 is not None
            else 0.0
        ),
        "result_status": get_result_status(top_class_id),
        "created_at": result.detime,
    }


def convert_result_to_detail_dict(result: Result) -> dict:
    """
    DB Result 객체를 분석 상세 응답으로 변환합니다.

    DB의 class_id1/2/3 형태를
    top_predictions 배열 형태로 가공합니다.
    """

    top_predictions = [
        convert_prediction_to_dict(
            rank=1,
            class_id=result.class_id1,
            class_name=result.class_name1,
            confidence=result.confidence1,
        ),
        convert_prediction_to_dict(
            rank=2,
            class_id=result.class_id2,
            class_name=result.class_name2,
            confidence=result.confidence2,
        ),
        convert_prediction_to_dict(
            rank=3,
            class_id=result.class_id3,
            class_name=result.class_name3,
            confidence=result.confidence3,
        ),
    ]

    process_info = None
    if result.process_info:
        try:
            process_info = json.loads(result.process_info)
        except (json.JSONDecodeError, TypeError):
            process_info = None

    return {
        "analysis_id": result.result_num,
        "user_num": result.user_num,
        "image_id": result.image_num,
        "image_name": result.image_name,
        "result_status": get_result_status(result.class_id1),
        "top_predictions": top_predictions,
        "created_at": result.detime,
        "gradcam_data": result.gradcam_data,
        "process_info": process_info,
    }


def find_result_or_404(
    db: Session,
    result_num: int,
    user_num: int,
) -> Result:
    """
    사용자 번호와 결과 번호가 모두 일치하는 분석 결과를 조회합니다.

    결과가 없으면 404 오류를 발생시킵니다.
    """

    try:
        result = (
            db.query(Result)
            .filter(
                Result.result_num == result_num,
                Result.user_num == user_num,
            )
            .first()
        )

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "분석 결과 조회 중 DB 오류가 발생했습니다.",
            },
        ) from error

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
    """
    Top 3 분석 결과를 result 테이블에 저장합니다.

    요청에서는 class_id와 confidence만 받고,
    class_name은 서버의 매핑표로 만들어 저장합니다.
    """

    validate_top_predictions(request.top_predictions)

    first_prediction = request.top_predictions[0]
    second_prediction = request.top_predictions[1]
    third_prediction = request.top_predictions[2]

    result = Result(
        user_num=request.user_num,
        image_num=request.image_num,

        class_id1=first_prediction.class_id,
        class_name1=get_class_name(first_prediction.class_id),
        confidence1=first_prediction.confidence,

        class_id2=second_prediction.class_id,
        class_name2=get_class_name(second_prediction.class_id),
        confidence2=second_prediction.confidence,

        class_id3=third_prediction.class_id,
        class_name3=get_class_name(third_prediction.class_id),
        confidence3=third_prediction.confidence,
    )

    try:
        db.add(result)
        db.commit()
        db.refresh(result)

    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_user_or_image",
                "message": "존재하지 않는 사용자 또는 이미지입니다.",
            },
        ) from error

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "분석 결과 저장 중 DB 오류가 발생했습니다.",
            },
        ) from error

    return convert_result_to_detail_dict(result)


def get_analysis_list(
    db: Session,
    user_num: int,
    page: int,
    size: int,
) -> dict:
    """
    사용자의 분석 결과 목록을 최신순으로 조회합니다.

    목록에서는 1위 예측과 신뢰도만 반환합니다.
    """

    try:
        query = db.query(Result).filter(
            Result.user_num == user_num,
        )

        total_count = query.count()
        offset = (page - 1) * size

        results = (
            query.order_by(
                Result.detime.desc(),
                Result.result_num.desc(),
            )
            .offset(offset)
            .limit(size)
            .all()
        )

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "분석 결과 목록 조회 중 DB 오류가 발생했습니다.",
            },
        ) from error

    total_pages = (
        ceil(total_count / size)
        if total_count > 0
        else 0
    )

    return {
        "items": [
            convert_result_to_list_item(result)
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
    """
    분석 결과 한 건을 Top 3 구조로 조회합니다.
    """

    result = find_result_or_404(
        db=db,
        result_num=result_num,
        user_num=user_num,
    )

    return convert_result_to_detail_dict(result)


def update_analysis(
    db: Session,
    result_num: int,
    user_num: int,
    request: AnalysisUpdateRequest,
) -> dict:
    """
    저장된 Top 3 예측 결과 전체를 수정합니다.

    일부 순위만 바꾸지 않고
    1위부터 3위까지 함께 교체합니다.
    """

    validate_top_predictions(request.top_predictions)

    result = find_result_or_404(
        db=db,
        result_num=result_num,
        user_num=user_num,
    )

    first_prediction = request.top_predictions[0]
    second_prediction = request.top_predictions[1]
    third_prediction = request.top_predictions[2]

    result.class_id1 = first_prediction.class_id
    result.class_name1 = get_class_name(first_prediction.class_id)
    result.confidence1 = first_prediction.confidence

    result.class_id2 = second_prediction.class_id
    result.class_name2 = get_class_name(second_prediction.class_id)
    result.confidence2 = second_prediction.confidence

    result.class_id3 = third_prediction.class_id
    result.class_name3 = get_class_name(third_prediction.class_id)
    result.confidence3 = third_prediction.confidence

    try:
        db.commit()
        db.refresh(result)

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "분석 결과 수정 중 DB 오류가 발생했습니다.",
            },
        ) from error

    return convert_result_to_detail_dict(result)


def delete_analysis(
    db: Session,
    result_num: int,
    user_num: int,
) -> None:
    """
    분석 결과 한 건을 삭제합니다.
    """

    result = find_result_or_404(
        db=db,
        result_num=result_num,
        user_num=user_num,
    )

    try:
        db.delete(result)
        db.commit()

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "code": "database_error",
                "message": "분석 결과 삭제 중 DB 오류가 발생했습니다.",
            },
        ) from error
    

from datetime import datetime, timedelta
from sqlalchemy import case, func

WEEKDAY_NAMES = ["월", "화", "수", "목", "금", "토", "일"]


def get_analysis_dashboard(db: Session, user_num: int) -> dict:
    """오늘 기준 대시보드 통계(시간대별/요일별 포함)를 계산합니다."""

    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = today_start + timedelta(days=1)

    try:
        today_query = db.query(Result).filter(
            Result.user_num == user_num,
            Result.detime >= today_start,
            Result.detime < today_end,
        )
        today_count = today_query.count()
        today_pass_count = today_query.filter(Result.class_id1 == NORMAL_CLASS_ID).count()
        today_fail_count = today_query.filter(Result.class_id1 != NORMAL_CLASS_ID).count()
        today_defect_rate = (
            round((today_fail_count / today_count) * 100, 2) if today_count > 0 else 0.0
        )

        avg_value = (
            db.query(func.avg(Result.confidence1))
            .filter(Result.user_num == user_num, Result.detime >= today_start, Result.detime < today_end)
            .scalar()
        )
        average_confidence = round(float(avg_value), 2) if avg_value is not None else 0.0

        hourly_rows = (
            db.query(func.hour(Result.detime), func.count(Result.result_num))
            .filter(Result.user_num == user_num, Result.detime >= today_start, Result.detime < today_end)
            .group_by(func.hour(Result.detime))
            .all()
        )
        hourly_map = {int(h): c for h, c in hourly_rows}
        hourly_counts = [{"hour": f"{h:02d}:00", "count": hourly_map.get(h, 0)} for h in range(24)]

        week_start = today_start - timedelta(days=6)
        weekday_rows = (
            db.query(
                func.weekday(Result.detime),
                func.count(Result.result_num),
                func.sum(case((Result.class_id1 != NORMAL_CLASS_ID, 1), else_=0)),
            )
            .filter(Result.user_num == user_num, Result.detime >= week_start)
            .group_by(func.weekday(Result.detime))
            .all()
        )
        weekday_map = {int(w): (int(t), int(f or 0)) for w, t, f in weekday_rows}
        weekday_defect_rates = [
            {
                "weekday": name,
                "total_count": weekday_map.get(i, (0, 0))[0],
                "fail_count": weekday_map.get(i, (0, 0))[1],
                "defect_rate": (
                    round((weekday_map.get(i, (0, 0))[1] / weekday_map.get(i, (0, 0))[0]) * 100, 2)
                    if weekday_map.get(i, (0, 0))[0] > 0 else 0.0
                ),
            }
            for i, name in enumerate(WEEKDAY_NAMES)
        ]

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail={"code": "database_error", "message": "대시보드 조회 중 DB 오류가 발생했습니다."},
        ) from error

    return {
        "today_count": today_count,
        "today_pass_count": today_pass_count,
        "today_fail_count": today_fail_count,
        "today_defect_rate": today_defect_rate,
        "average_confidence": average_confidence,
        "hourly_counts": hourly_counts,
        "weekday_defect_rates": weekday_defect_rates,
    }
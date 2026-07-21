# from collections.abc import Generator

# from fastapi import (
#     APIRouter,
#     Depends,
#     Query,
#     Response,
#     status,
# )
# from sqlalchemy.orm import Session

# from bc.waper.app.database import SessionLocal
# from be.app.backend2 import analysis_service
# from be.app.backend2 import statistics_service
# from be.app.backend2.schemas import (
#     AnalysisCreateRequest,
#     AnalysisListResponse,
#     AnalysisResponse,
#     AnalysisStatisticsResponse,
#     AnalysisUpdateRequest,
# )


# router = APIRouter(
#     prefix="/api/analyses",
#     tags=["analyses"],
# )


# def get_db() -> Generator[Session, None, None]:
#     """요청마다 DB 세션을 열고 처리가 끝나면 닫습니다."""

#     db = SessionLocal()

#     try:
#         yield db
#     finally:
#         db.close()


# @router.post(
#     "",
#     response_model=AnalysisResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_analysis(
#     request: AnalysisCreateRequest,
#     db: Session = Depends(get_db),
# ):
#     return analysis_service.create_analysis(
#         db=db,
#         request=request,
#     )


# @router.get(
#     "",
#     response_model=AnalysisListResponse,
# )
# def get_analysis_list(
#     user_num: int = Query(..., ge=1),
#     page: int = Query(1, ge=1),
#     size: int = Query(20, ge=1, le=100),
#     db: Session = Depends(get_db),
# ):
#     return analysis_service.get_analysis_list(
#         db=db,
#         user_num=user_num,
#         page=page,
#         size=size,
#     )


# @router.get(
#     "/statistics",
#     response_model=AnalysisStatisticsResponse,
# )
# def get_analysis_statistics(
#     user_num: int = Query(..., ge=1),
#     db: Session = Depends(get_db),
# ):
#     return statistics_service.get_analysis_statistics(
#         db=db,
#         user_num=user_num,
#     )


# @router.get(
#     "/{result_num}",
#     response_model=AnalysisResponse,
# )
# def get_analysis_detail(
#     result_num: int,
#     user_num: int = Query(..., ge=1),
#     db: Session = Depends(get_db),
# ):
#     return analysis_service.get_analysis_detail(
#         db=db,
#         result_num=result_num,
#         user_num=user_num,
#     )


# @router.patch(
#     "/{result_num}",
#     response_model=AnalysisResponse,
# )
# def update_analysis(
#     result_num: int,
#     request: AnalysisUpdateRequest,
#     user_num: int = Query(..., ge=1),
#     db: Session = Depends(get_db),
# ):
#     return analysis_service.update_analysis(
#         db=db,
#         result_num=result_num,
#         user_num=user_num,
#         request=request,
#     )


# @router.delete(
#     "/{result_num}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# def delete_analysis(
#     result_num: int,
#     user_num: int = Query(..., ge=1),
#     db: Session = Depends(get_db),
# ):
#     analysis_service.delete_analysis(
#         db=db,
#         result_num=result_num,
#         user_num=user_num,
#     )

#     return Response(
#         status_code=status.HTTP_204_NO_CONTENT,
#     )


from collections.abc import Generator

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from bc.waper.app.database import SessionLocal
from be.app.sg import analysis_service
from be.app.sg import statistics_service
from be.app.sg.schemas import (
    AnalysisCreateRequest,
    AnalysisListResponse,
    AnalysisResponse,
    AnalysisStatisticsResponse,
    AnalysisUpdateRequest,
)


router = APIRouter(
    prefix="/api/analyses",
    tags=["analyses"],
)


def get_db() -> Generator[Session, None, None]:
    """
    요청마다 DB 세션을 생성합니다.

    API 처리가 끝나거나 오류가 발생해도
    finally에서 세션을 닫습니다.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# 1. 분석 결과 생성
# =========================================================

@router.post(
    "",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="분석 결과 생성",
)
def create_analysis(
    request: AnalysisCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Top 3 AI 예측 결과를 저장합니다.

    요청에서는 각 예측의 class_id와 confidence를 받고,
    class_name은 서비스에서 클래스 매핑표로 생성합니다.
    """

    return analysis_service.create_analysis(
        db=db,
        request=request,
    )


# =========================================================
# 2. 분석 결과 목록
# =========================================================

@router.get(
    "",
    response_model=AnalysisListResponse,
    summary="분석 결과 목록 조회",
)
def get_analysis_list(
    user_num: int = Query(
        ...,
        ge=1,
        description="조회할 사용자 번호입니다.",
    ),
    page: int = Query(
        1,
        ge=1,
        description="조회할 페이지 번호입니다.",
    ),
    size: int = Query(
        20,
        ge=1,
        le=100,
        description="한 페이지에 반환할 결과 개수입니다.",
    ),
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 분석 결과를 최신순으로 조회합니다.

    목록 화면에서는 각 결과의 1위 예측과 신뢰도를 반환합니다.
    """

    return analysis_service.get_analysis_list(
        db=db,
        user_num=user_num,
        page=page,
        size=size,
    )


# =========================================================
# 3. 분석 통계
# =========================================================

@router.get(
    "/statistics",
    response_model=AnalysisStatisticsResponse,
    summary="분석 결과 통계 조회",
)
def get_analysis_statistics(
    user_num: int = Query(
        ...,
        ge=1,
        description="통계를 조회할 사용자 번호입니다.",
    ),
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 전체 검사 통계를 조회합니다.

    다음 값을 포함합니다.

    - 전체 검사 수
    - PASS 수
    - FAIL 수
    - 불량률
    - 평균 신뢰도
    - 결함 클래스별 건수
    - 최근 신뢰도 추이
    - 가장 최근 분석 결과
    """

    return statistics_service.get_analysis_statistics(
        db=db,
        user_num=user_num,
    )


# =========================================================
# 4. 분석 결과 상세 조회
# =========================================================

@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
    summary="분석 결과 상세 조회",
)
def get_analysis_detail(
    analysis_id: int = Path(
        ...,
        ge=1,
        description="조회할 분석 결과 번호입니다.",
    ),
    user_num: int = Query(
        ...,
        ge=1,
        description="분석 결과 소유자의 사용자 번호입니다.",
    ),
    db: Session = Depends(get_db),
):
    """
    분석 결과 한 건을 조회합니다.

    상세 응답에는 1위부터 3위까지의 예측 결과가 포함됩니다.
    """

    return analysis_service.get_analysis_detail(
        db=db,

        # API에서는 analysis_id라고 부르지만
        # 실제 DB 컬럼은 result_num입니다.
        result_num=analysis_id,

        user_num=user_num,
    )


# =========================================================
# 5. 분석 결과 수정
# =========================================================

@router.patch(
    "/{analysis_id}",
    response_model=AnalysisResponse,
    summary="분석 결과 수정",
)
def update_analysis(
    request: AnalysisUpdateRequest,
    analysis_id: int = Path(
        ...,
        ge=1,
        description="수정할 분석 결과 번호입니다.",
    ),
    user_num: int = Query(
        ...,
        ge=1,
        description="분석 결과 소유자의 사용자 번호입니다.",
    ),
    db: Session = Depends(get_db),
):
    """
    저장된 Top 3 예측 전체를 수정합니다.

    일부 순위만 수정하지 않고
    1위부터 3위까지의 결과를 한 번에 교체합니다.
    """

    return analysis_service.update_analysis(
        db=db,
        result_num=analysis_id,
        user_num=user_num,
        request=request,
    )


# =========================================================
# 6. 분석 결과 삭제
# =========================================================

@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="분석 결과 삭제",
)
def delete_analysis(
    analysis_id: int = Path(
        ...,
        ge=1,
        description="삭제할 분석 결과 번호입니다.",
    ),
    user_num: int = Query(
        ...,
        ge=1,
        description="분석 결과 소유자의 사용자 번호입니다.",
    ),
    db: Session = Depends(get_db),
):
    """
    분석 결과 한 건을 삭제합니다.

    삭제가 성공하면 응답 본문 없이 204 상태 코드를 반환합니다.
    """

    analysis_service.delete_analysis(
        db=db,
        result_num=analysis_id,
        user_num=user_num,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
from collections.abc import Generator

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from bc.waper.app.database import SessionLocal
from be.app.backend2 import analysis_service
from be.app.backend2 import statistics_service
from be.app.backend2.schemas import (
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
    """요청마다 DB 세션을 열고 처리가 끝나면 닫습니다."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_analysis(
    request: AnalysisCreateRequest,
    db: Session = Depends(get_db),
):
    return analysis_service.create_analysis(
        db=db,
        request=request,
    )


@router.get(
    "",
    response_model=AnalysisListResponse,
)
def get_analysis_list(
    user_num: int = Query(..., ge=1),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return analysis_service.get_analysis_list(
        db=db,
        user_num=user_num,
        page=page,
        size=size,
    )


@router.get(
    "/statistics",
    response_model=AnalysisStatisticsResponse,
)
def get_analysis_statistics(
    user_num: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return statistics_service.get_analysis_statistics(
        db=db,
        user_num=user_num,
    )


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
)
def get_analysis_detail(
    analysis_id: int,
    user_num: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return analysis_service.get_analysis_detail(
        db=db,
        analysis_id=analysis_id,
        user_num=user_num,
    )


@router.patch(
    "/{analysis_id}",
    response_model=AnalysisResponse,
)
def update_analysis(
    analysis_id: int,
    request: AnalysisUpdateRequest,
    user_num: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return analysis_service.update_analysis(
        db=db,
        analysis_id=analysis_id,
        user_num=user_num,
        request=request,
    )


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_analysis(
    analysis_id: int,
    user_num: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    analysis_service.delete_analysis(
        db=db,
        analysis_id=analysis_id,
        user_num=user_num,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
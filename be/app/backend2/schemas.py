# from datetime import datetime

# from pydantic import BaseModel, Field


# class AnalysisCreateRequest(BaseModel):
#     """분석 결과 생성 요청 형식입니다."""

#     user_num: int = Field(..., ge=1)
#     image_id: int = Field(..., ge=1)
#     class_id: int = Field(..., ge=0, le=8)


# class AnalysisUpdateRequest(BaseModel):
#     """분석 결과 수정 요청 형식입니다."""

#     class_id: int | None = Field(default=None, ge=0, le=8)


# class AnalysisResponse(BaseModel):
#     """분석 결과 한 건의 응답 형식입니다."""

#     analysis_id: int
#     user_num: int
#     image_id: int
#     class_id: int
#     class_name: str | None = None
#     created_at: datetime


# class AnalysisListResponse(BaseModel):
#     """분석 결과 목록과 페이징 정보를 반환합니다."""

#     items: list[AnalysisResponse]
#     page: int
#     size: int
#     total_count: int
#     total_pages: int


# class DefectTypeCountItem(BaseModel):
#     """결함 클래스별 개수를 반환합니다."""

#     class_id: int
#     class_name: str | None = None
#     count: int


# class AnalysisStatisticsResponse(BaseModel):
#     """사용자별 분석 결과 통계 응답 형식입니다."""

#     total_count: int
#     normal_count: int
#     defect_count: int
#     defect_type_counts: list[DefectTypeCountItem]

from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisCreateRequest(BaseModel):
    """분석 결과 생성 요청 형식입니다."""

    user_num: int = Field(..., ge=1)
    image_num: int = Field(..., ge=1)
    class_id: int = Field(..., ge=0, le=8)


class AnalysisUpdateRequest(BaseModel):
    """분석 결과 수정 요청 형식입니다."""

    class_id: int | None = Field(default=None, ge=0, le=8)


class AnalysisResponse(BaseModel):
    """분석 결과 한 건의 응답 형식입니다."""

    result_num: int
    user_num: int
    image_num: int
    class_id: int
    class_name: str | None = None
    detime: datetime


class AnalysisListResponse(BaseModel):
    """분석 결과 목록과 페이징 정보를 반환합니다."""

    items: list[AnalysisResponse]
    page: int
    size: int
    total_count: int
    total_pages: int


class DefectTypeCountItem(BaseModel):
    """결함 클래스별 개수를 반환합니다."""

    class_id: int
    class_name: str | None = None
    count: int


class AnalysisStatisticsResponse(BaseModel):
    """사용자별 분석 결과 통계 응답 형식입니다."""

    total_count: int
    normal_count: int
    defect_count: int
    defect_type_counts: list[DefectTypeCountItem]
# # from datetime import datetime

# # from pydantic import BaseModel, Field


# # class AnalysisCreateRequest(BaseModel):
# #     """분석 결과 생성 요청 형식입니다."""

# #     user_num: int = Field(..., ge=1)
# #     image_id: int = Field(..., ge=1)
# #     class_id: int = Field(..., ge=0, le=8)


# # class AnalysisUpdateRequest(BaseModel):
# #     """분석 결과 수정 요청 형식입니다."""

# #     class_id: int | None = Field(default=None, ge=0, le=8)


# # class AnalysisResponse(BaseModel):
# #     """분석 결과 한 건의 응답 형식입니다."""

# #     analysis_id: int
# #     user_num: int
# #     image_id: int
# #     class_id: int
# #     class_name: str | None = None
# #     created_at: datetime


# # class AnalysisListResponse(BaseModel):
# #     """분석 결과 목록과 페이징 정보를 반환합니다."""

# #     items: list[AnalysisResponse]
# #     page: int
# #     size: int
# #     total_count: int
# #     total_pages: int


# # class DefectTypeCountItem(BaseModel):
# #     """결함 클래스별 개수를 반환합니다."""

# #     class_id: int
# #     class_name: str | None = None
# #     count: int


# # class AnalysisStatisticsResponse(BaseModel):
# #     """사용자별 분석 결과 통계 응답 형식입니다."""

# #     total_count: int
# #     normal_count: int
# #     defect_count: int
# #     defect_type_counts: list[DefectTypeCountItem]

# from datetime import datetime

# from pydantic import BaseModel, Field


# class AnalysisCreateRequest(BaseModel):
#     """분석 결과 생성 요청 형식입니다."""

#     user_num: int = Field(..., ge=1)
#     image_num: int = Field(..., ge=1)
#     class_id: int = Field(..., ge=0, le=8)


# class AnalysisUpdateRequest(BaseModel):
#     """분석 결과 수정 요청 형식입니다."""

#     class_id: int | None = Field(default=None, ge=0, le=8)


# class AnalysisResponse(BaseModel):
#     """분석 결과 한 건의 응답 형식입니다."""

#     result_num: int
#     user_num: int
#     image_num: int
#     class_id: int
#     class_name: str | None = None
#     detime: datetime


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
from typing import Literal

from pydantic import BaseModel, Field


# PASS/FAIL 외의 문자열이 들어가지 않도록 제한합니다.
ResultStatus = Literal["PASS", "FAIL"]


# =========================================================
# 1. AI 예측 관련 스키마
# =========================================================

class PredictionRequestItem(BaseModel):
    """
    분석 결과를 생성하거나 수정할 때 전달하는 예측 한 건입니다.

    배열의 첫 번째 항목이 1위,
    두 번째 항목이 2위,
    세 번째 항목이 3위 예측입니다.
    """

    class_id: int = Field(
        ...,
        ge=0,
        le=8,
        description="AI 클래스 번호입니다. 0~8만 허용합니다.",
    )

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="AI 예측 신뢰도입니다.",
    )


class PredictionResponseItem(BaseModel):
    """
    프론트에 반환하는 예측 한 건입니다.
    """

    rank: int = Field(
        ...,
        ge=1,
        le=3,
        description="예측 순위입니다. 1위부터 3위까지 사용합니다.",
    )

    class_id: int = Field(
        ...,
        ge=0,
        le=8,
        description="AI 클래스 번호입니다.",
    )

    class_name: str = Field(
        ...,
        max_length=50,
        description="사람이 읽을 수 있는 클래스 이름입니다.",
    )

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="해당 클래스의 예측 신뢰도입니다.",
    )


# =========================================================
# 2. 분석 결과 생성·수정 요청
# =========================================================

class AnalysisCreateRequest(BaseModel):
    """
    분석 결과 생성 요청입니다.

    class_name은 프론트에서 받지 않습니다.
    백엔드가 class_id를 기준으로 클래스 이름을 결정합니다.
    """

    user_num: int = Field(
        ...,
        ge=1,
        description="분석 결과의 사용자 번호입니다.",
    )

    image_num: int = Field(
        ...,
        ge=1,
        description="분석한 이미지 번호입니다.",
    )

    top_predictions: list[PredictionRequestItem] = Field(
        ...,
        min_length=3,
        max_length=3,
        description="1위부터 3위까지의 AI 예측 결과입니다.",
    )


class AnalysisUpdateRequest(BaseModel):
    """
    분석 결과 수정 요청입니다.

    Top 3 중 하나만 따로 수정하지 않고,
    Top 3 전체를 한 번에 교체하는 구조입니다.
    """

    top_predictions: list[PredictionRequestItem] = Field(
        ...,
        min_length=3,
        max_length=3,
        description="수정할 1위부터 3위까지의 전체 예측 결과입니다.",
    )


# =========================================================
# 3. 분석 목록 응답
# =========================================================

class AnalysisListItem(BaseModel):
    """
    검사 이력 목록의 한 줄에 필요한 데이터입니다.

    목록 화면에서는 1위 예측만 반환하고,
    2위와 3위는 상세 조회에서 반환합니다.
    """

    analysis_id: int
    user_num: int
    image_id: int
    image_name: str | None = None

    top_class_id: int = Field(
        ...,
        ge=0,
        le=8,
    )

    top_class_name: str

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
    )

    result_status: ResultStatus
    created_at: datetime


class AnalysisListResponse(BaseModel):
    """
    분석 결과 목록과 페이징 정보를 반환합니다.
    """

    items: list[AnalysisListItem]

    page: int = Field(..., ge=1)
    size: int = Field(..., ge=1)

    total_count: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)


# =========================================================
# 4. 분석 상세·생성·수정 응답
# =========================================================

class AnalysisResponse(BaseModel):
    """
    분석 결과 한 건의 상세 응답입니다.

    POST 생성 응답, GET 상세 응답,
    PATCH 수정 응답에서 공통으로 사용할 수 있습니다.
    """

    analysis_id: int
    user_num: int
    image_id: int
    image_name: str | None = None

    result_status: ResultStatus

    top_predictions: list[PredictionResponseItem] = Field(
        ...,
        min_length=3,
        max_length=3,
    )

    created_at: datetime

    # Grad-CAM 히트맵 (base64 PNG 문자열) 및 원인공정 후보 목록
    gradcam_data: str | None = None
    process_info: list | None = None


# =========================================================
# 5. 통계 응답
# =========================================================

class DefectTypeCountItem(BaseModel):
    """
    1위 판정 클래스별 검사 건수를 반환합니다.

    class_id1을 기준으로 집계하며,
    2위와 3위 후보는 통계에 포함하지 않습니다.
    """

    class_id: int = Field(..., ge=0, le=8)
    class_name: str
    count: int = Field(..., ge=0)


class ConfidenceTrendItem(BaseModel):
    """
    검사 이력 화면의 신뢰도 추이 그래프에 사용할 항목입니다.
    """

    analysis_id: int
    image_name: str | None = None

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
    )

    created_at: datetime


class LatestAnalysisItem(BaseModel):
    """
    검사 이력 화면의 최근 판정 카드에 사용할 항목입니다.
    """

    analysis_id: int
    image_id: int
    image_name: str | None = None

    top_class_id: int = Field(..., ge=0, le=8)
    top_class_name: str

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
    )

    result_status: ResultStatus
    created_at: datetime


class AnalysisStatisticsResponse(BaseModel):
    """
    검사 이력 화면에서 사용하는 사용자별 통계입니다.
    """

    total_count: int = Field(..., ge=0)
    pass_count: int = Field(..., ge=0)
    fail_count: int = Field(..., ge=0)

    defect_rate: float = Field(
        ...,
        ge=0,
        le=100,
        description="FAIL 건수 / 전체 검사 건수 × 100입니다.",
    )

    average_confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="1위 예측 confidence1의 평균입니다.",
    )

    defect_type_counts: list[DefectTypeCountItem]
    confidence_trend: list[ConfidenceTrendItem]

    latest_result: LatestAnalysisItem | None = None


# =========================================================
# 6. 대시보드 응답
# =========================================================

class HourlyCountItem(BaseModel):
    """
    최근 시간대별 검사 건수를 반환합니다.
    """

    hour: str = Field(
        ...,
        description="예: 07:00, 08:00",
    )

    count: int = Field(..., ge=0)


class WeekdayDefectRateItem(BaseModel):
    """
    요일별 검사 건수와 불량률을 반환합니다.
    """

    weekday: str = Field(
        ...,
        description="예: 월, 화, 수",
    )

    total_count: int = Field(..., ge=0)
    fail_count: int = Field(..., ge=0)

    defect_rate: float = Field(
        ...,
        ge=0,
        le=100,
    )


class AnalysisDashboardResponse(BaseModel):
    """
    대시보드 상단 통계와 그래프에 필요한 응답입니다.
    """

    today_count: int = Field(..., ge=0)
    today_pass_count: int = Field(..., ge=0)
    today_fail_count: int = Field(..., ge=0)

    today_defect_rate: float = Field(
        ...,
        ge=0,
        le=100,
    )

    average_confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="오늘 또는 지정 기간의 confidence1 평균입니다.",
    )

    hourly_counts: list[HourlyCountItem]
    weekday_defect_rates: list[WeekdayDefectRateItem]


# =========================================================
# 7. 삭제 응답
# =========================================================

class AnalysisDeleteResponse(BaseModel):
    """
    분석 결과 삭제 완료 응답입니다.
    """

    analysis_id: int
    message: str
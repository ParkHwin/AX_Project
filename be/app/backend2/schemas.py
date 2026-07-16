from datetime import datetime
from typing import Literal

from pydantic import BaseModel

DetectValue = Literal["정상", "불량"]


class AnalysisCreateRequest(BaseModel):
 #"""분석 결과 생성 요청 형식입니다."""
    user_num: int
    image_id: int
    detect: DetectValue
    class_name: str | None = None


class AnalysisUpdateRequest(BaseModel):
# """분석 결과 수정 요청 형식입니다."""
    detect: DetectValue | None = None
    class_name: str | None = None


class AnalysisResponse(BaseModel):
#"""분석 결과 한 건의 응답 형식입니다."""
    analysis_id: int
    user_num: int
    image_id: int
    detect: str
    class_name: str | None = None
    created_at: datetime


class AnalysisListResponse(BaseModel):
 #"""분석 결과 목록과 페이징 정보를 반환합니다."""
    items: list[AnalysisResponse]
    page: int
    size: int
    total_count: int
    total_pages: int

class DefectTypeCountItem(BaseModel):
#"""결함 종류별 개수를 반환합니다."""
    defect_type: str
    count: int


class AnalysisStatisticsResponse(BaseModel):
#"""사용자별 분석 결과 통계 응답 형식입니다."""
    total_count: int
    normal_count: int
    defect_count: int
    defect_type_counts: list[DefectTypeCountItem]
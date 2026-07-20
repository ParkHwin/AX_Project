"""API 요청/응답 형식 — 비밀번호는 응답에 포함하지 않는다."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    position: str | None = None
    department: str | None = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_num: int
    email: str
    name: str
    position: str | None
    department: str | None


class ImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    image_num: int
    user_num: int
    time: datetime


class ResultCreate(BaseModel):
    user_num: int
    image_num: int
    # AI 분석 결과 상위 3개를 확률 순으로 저장 (0~8 코드, 매핑 표는 라벨_매핑.md)
    class_id1: int = Field(ge=0, le=8)
    class_id2: int = Field(ge=0, le=8)
    class_id3: int = Field(ge=0, le=8)
    # 각 class_id에 대응하는 확률 (0.0 ~ 1.0)
    confidence1: float = Field(ge=0, le=1)
    confidence2: float = Field(ge=0, le=1)
    confidence3: float = Field(ge=0, le=1)


class ResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    result_num: int
    user_num: int
    image_num: int
    class_id1: int
    class_id2: int
    class_id3: int
    confidence1: float
    confidence2: float
    confidence3: float
    detime: datetime

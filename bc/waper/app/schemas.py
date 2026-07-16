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
    # AI가 출력하는 코드 그대로 저장 (매핑 표는 라벨_매핑.md — 8이 정상)
    detect: int = Field(ge=0, le=9)


class ResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    result_num: int
    user_num: int
    image_num: int
    detect: int
    detime: datetime

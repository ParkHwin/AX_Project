"""API 요청/응답 형식 — 비밀번호는 응답에 포함하지 않는다."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    user_id: str
    password: str
    name: str
    email: str


class UserLogin(BaseModel):
    user_id: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_num: int
    user_id: str
    name: str
    email: str


class ImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    image_num: int
    user_num: int
    time: datetime


class ResultCreate(BaseModel):
    user_num: int
    image_num: int
    detect: str
    detect_type: str | None = None


class ResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    result_num: int
    user_num: int
    image_num: int
    detect: str
    detect_type: str | None
    detime: datetime

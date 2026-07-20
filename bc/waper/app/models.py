"""테이블 정의 — user / test_image / result."""

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    LargeBinary,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "user"

    user_num = Column(BigInteger, primary_key=True, autoincrement=True)
    # 로그인은 이메일로 한다 (프론트 가입 폼에 아이디 입력란이 없음)
    email = Column(String(100), nullable=False, unique=True)
    # pass는 파이썬 예약어라 속성명은 pass_, 실제 컬럼명만 pass로 매핑
    pass_ = Column("pass", String(255), nullable=False)
    name = Column(String(50), nullable=False)
    position = Column(String(50), nullable=True)  # 직책
    department = Column(String(50), nullable=True)  # 부서

    images = relationship("TestImage", back_populates="user", cascade="all, delete")
    results = relationship("Result", back_populates="user", cascade="all, delete")


class TestImage(Base):
    __tablename__ = "test_image"

    image_num = Column(BigInteger, primary_key=True, autoincrement=True)
    user_num = Column(
        BigInteger, ForeignKey("user.user_num", ondelete="CASCADE"), nullable=False
    )
    image = Column(LargeBinary(length=(2**32) - 1), nullable=False)  # LONGBLOB
    # 업로드한 원본 파일 이름 (브라우저가 안 보내주는 경우가 있어 NULL 허용)
    image_name = Column(String(255), nullable=True)
    time = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", back_populates="images")
    results = relationship("Result", back_populates="test_image", cascade="all, delete")


class Result(Base):
    __tablename__ = "result"

    result_num = Column(BigInteger, primary_key=True, autoincrement=True)
    user_num = Column(
        BigInteger, ForeignKey("user.user_num", ondelete="CASCADE"), nullable=False
    )
    image_num = Column(
        BigInteger, ForeignKey("test_image.image_num", ondelete="CASCADE"), nullable=False
    )
    # AI 분석 결과 상위 3개를 확률 순으로 저장 (0~8 코드, 매핑 표는 라벨_매핑.md)
    class_id1 = Column(SmallInteger, nullable=False)
    class_id2 = Column(SmallInteger, nullable=False)
    class_id3 = Column(SmallInteger, nullable=False)
    # 각 class_id에 대응하는 클래스 이름 (label_mapping.json 기준, 서버가 채움)
    class_name1 = Column(String(50), nullable=False)
    class_name2 = Column(String(50), nullable=False)
    class_name3 = Column(String(50), nullable=False)
    # 각 class_id에 대응하는 확률 (0.0 ~ 1.0)
    confidence1 = Column(Float, nullable=False)
    confidence2 = Column(Float, nullable=False)
    confidence3 = Column(Float, nullable=False)
    # 분석 대상 이미지의 원본 파일 이름 (test_image에서 복사, 서버가 채움)
    image_name = Column(String(255), nullable=True)
    detime = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", back_populates="results")
    test_image = relationship("TestImage", back_populates="results")

"""앱 시작점 — 여기서 DB/테이블 자동 생성이 실행된다."""

import hashlib
import json
import time
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db, init_database

init_database()  # 1. waper DB 생성 (없으면)

# 두 서버(bc/waper, be/app)가 동시에 시작될 때 concurrent DDL 충돌(MySQL 1684) 방지
for _attempt in range(5):
    try:
        Base.metadata.create_all(bind=engine)  # 2. 테이블 생성 (없으면)
        break
    except OperationalError as _e:
        if _attempt < 4 and "1684" in str(_e):
            time.sleep(1.0)
        else:
            raise


def _add_columns_if_missing():
    """기존 result 테이블에 신규 컬럼이 없으면 추가 (멱등, 무손실)."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "result" not in inspector.get_table_names():
        return  # create_all이 이미 신규 컬럼 포함해서 생성함
    existing = {col["name"] for col in inspector.get_columns("result")}
    with engine.connect() as conn:
        if "gradcam_data" not in existing:
            conn.execute(text("ALTER TABLE result ADD COLUMN gradcam_data MEDIUMTEXT NULL"))
        if "gradcam_heatmap_data" not in existing:
            conn.execute(text("ALTER TABLE result ADD COLUMN gradcam_heatmap_data MEDIUMTEXT NULL"))
        if "process_info" not in existing:
            conn.execute(text("ALTER TABLE result ADD COLUMN process_info TEXT NULL"))
        conn.commit()


for _attempt in range(5):
    try:
        _add_columns_if_missing()  # 3. 신규 컬럼 추가 (기존 테이블 마이그레이션)
        break
    except OperationalError as _e:
        if _attempt < 4 and "1684" in str(_e):
            time.sleep(1.0)
        else:
            raise

app = FastAPI(title="Waper API")  # 3. 앱 준비

# 코드(0~8) → 클래스 이름 매핑 (bc/waper/label_mapping.json)
LABEL_MAPPING: dict[str, str] = json.loads(
    (Path(__file__).resolve().parent.parent / "label_mapping.json").read_text(
        encoding="utf-8"
    )
)

# 프론트(Vite dev 서버)에서 호출할 수 있도록 CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/users/signup", response_model=schemas.UserOut)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="이미 가입된 이메일입니다.")
    user = models.User(
        email=payload.email,
        pass_=hash_password(payload.password),
        name=payload.name,
        position=payload.position,
        department=payload.department,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/users/login", response_model=schemas.UserOut)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or user.pass_ != hash_password(payload.password):
        raise HTTPException(
            status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
    return user


@app.post("/images", response_model=schemas.ImageOut)
def upload_image(
    user_num: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    if not db.get(models.User, user_num):
        raise HTTPException(status_code=404, detail="존재하지 않는 회원입니다.")
    image_bytes = file.file.read()
    image = models.TestImage(
        user_num=user_num, image=image_bytes, image_name=file.filename
    )
    db.add(image)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(models.TestImage)
            .filter(models.TestImage.image_name == file.filename)
            .first()
        )
        if existing:
            return existing
        raise HTTPException(
            status_code=409, detail="이미 존재하는 이미지 이름입니다."
        )
    db.refresh(image)
    return image


@app.get("/users/{user_num}/images", response_model=list[schemas.ImageOut])
def list_images(user_num: int, db: Session = Depends(get_db)):
    return (
        db.query(models.TestImage)
        .filter(models.TestImage.user_num == user_num)
        .order_by(models.TestImage.time.desc())
        .all()
    )


@app.post("/results", response_model=schemas.ResultOut)
def create_result(payload: schemas.ResultCreate, db: Session = Depends(get_db)):
    if not db.get(models.User, payload.user_num):
        raise HTTPException(status_code=404, detail="존재하지 않는 회원입니다.")
    image = db.get(models.TestImage, payload.image_num)
    if not image:
        raise HTTPException(status_code=404, detail="존재하지 않는 이미지입니다.")
    result = models.Result(
        **payload.model_dump(),
        class_name1=LABEL_MAPPING[str(payload.class_id1)],
        class_name2=LABEL_MAPPING[str(payload.class_id2)],
        class_name3=LABEL_MAPPING[str(payload.class_id3)],
        image_name=image.image_name,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@app.get("/users/{user_num}/results", response_model=list[schemas.ResultOut])
def list_results(user_num: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Result)
        .filter(models.Result.user_num == user_num)
        .order_by(models.Result.detime.desc())
        .all()
    )

"""앱 시작점 — 여기서 DB/테이블 자동 생성이 실행된다."""

import hashlib

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db, init_database

init_database()  # 1. waper DB 생성 (없으면)
Base.metadata.create_all(bind=engine)  # 2. 테이블 생성 (없으면)

app = FastAPI(title="Waper API")  # 3. 앱 준비

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
    image = models.TestImage(user_num=user_num, image=file.file.read())
    db.add(image)
    db.commit()
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
    if not db.get(models.TestImage, payload.image_num):
        raise HTTPException(status_code=404, detail="존재하지 않는 이미지입니다.")
    result = models.Result(**payload.model_dump())
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

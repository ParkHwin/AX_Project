from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chu.router import router as chu_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 나중에 프론트 도메인으로 좁히기
    allow_methods=["POST"],
    allow_headers=["*"],
)

app.include_router(chu_router)
from fastapi import FastAPI
from chu.router import router as chu_router

app = FastAPI()
app.include_router(chu_router)
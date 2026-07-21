from bc.waper.app.main import app
from be.app.sg.router import router as backend2_router



#from fastapi import FastAPI
from be.app.chu.router import router as chu_router

#app = FastAPI()
app.include_router(chu_router)
app.include_router(backend2_router)

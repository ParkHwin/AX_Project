from bc.waper.app.main import app
from be.app.backend2.router import router as backend2_router


app.include_router(backend2_router)
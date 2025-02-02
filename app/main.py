from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.main_router import api_router
from app.core.security import get_current_active_superuser
import app.core.config as config
from app.core.database import engine


settings = config.get_settings()
app = FastAPI()

# CORS config - allow all (public API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get(
    "/admin/info",
    description="Get detailed database information",
    name="Get Database Info",
    dependencies=[Depends(get_current_active_superuser)],
)
async def info(settings: Annotated[config.Settings, Depends(config.get_settings)]):
    return {
        "app_name": settings.APP_NAME,
        "db_host": settings.DB_HOST,
        "db_name": settings.DB_NAME,
    }

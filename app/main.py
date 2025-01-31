from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI
from sqlmodel import SQLModel
from app.routers.main_router import api_router
from app.core.security import get_current_active_superuser

import core.config as config
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


settings = config.get_settings()
app = FastAPI(lifespan=lifespan)

app.include_router(api_router)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


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

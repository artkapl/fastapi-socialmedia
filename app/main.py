from typing import Annotated
from fastapi import Depends, FastAPI
from sqlmodel import SQLModel

import config
from .database import engine
from .routers import posts, users


settings = config.get_settings()
app = FastAPI()

app.include_router(posts.router)
app.include_router(users.router)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/db-info", description="Get detailed database information", name="Get Database Info")
async def info(settings: Annotated[config.Settings, Depends(config.get_settings)]):
    return {
        "app_name": settings.app_name,
        "db_host": settings.db_host,
        "db_name": settings.db_name,
    }

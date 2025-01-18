from functools import lru_cache
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Response, status
import psycopg
from psycopg.rows import dict_row

import config
from schema import Post
from .routers import posts_sql


@lru_cache
def get_settings():
    return config.Settings()


settings = get_settings()
app = FastAPI()

app.include_router(posts_sql.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/info", description="Get detailed database information", name="Get DB Info")
async def info(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
        "db_host": settings.db_host,
        "db_name": settings.db_name,
    }

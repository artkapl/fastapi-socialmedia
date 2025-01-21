from functools import lru_cache
from typing import Annotated
from fastapi import Depends, FastAPI
from psycopg.rows import dict_row

import config
from .routers import posts_orm


settings = config.get_settings()
app = FastAPI()

app.include_router(posts_orm.router)


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

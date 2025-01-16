from functools import lru_cache
from typing import Annotated
from fastapi import Depends, FastAPI

import config

app = FastAPI()

@lru_cache
def get_settings():
    return config.Settings()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/info")
async def info(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
        "db_host": settings.db_host,
        "db_port": settings.db_port,
        "db_name": settings.db_name,
    }
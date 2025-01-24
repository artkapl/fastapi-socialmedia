from typing import Annotated
from fastapi import APIRouter, Depends

from app import config
from . import posts, users, auth

###################
### MAIN ROUTER ###
###################

api_router = APIRouter()

settings = config.get_settings()

api_router.include_router(posts.router, prefix=settings.API_PREFIX)
api_router.include_router(users.router, prefix=settings.API_PREFIX)
api_router.include_router(auth.router)

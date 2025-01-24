from fastapi import APIRouter

from . import posts, users, auth

###################
### MAIN ROUTER ###
###################

api_router = APIRouter()

api_router.include_router(posts.router)
api_router.include_router(users.router)
api_router.include_router(auth.router)

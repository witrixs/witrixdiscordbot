from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.guilds import router as guilds_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(guilds_router)


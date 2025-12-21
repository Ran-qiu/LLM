from fastapi import APIRouter

from app.api.endpoints import auth, chat, models, users, statistics, tags, shares, templates


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(shares.router, prefix="/shares", tags=["shares"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])

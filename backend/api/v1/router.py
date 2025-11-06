from fastapi import APIRouter
from app.api.v1.endpoints.devops import router as devops_router
from app.api.v1.endpoints.devops_epic import router as devops_epic
from app.api.v1.endpoints.chat import router as chat_router

router = APIRouter()

router.include_router(chat_router, prefix="/chat", tags=["Chat AI Assistant"])

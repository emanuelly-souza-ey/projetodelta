from fastapi import APIRouter


from .endpoints.chat import router as chat_router
from .endpoints.validate_connection import router as validate_router

router = APIRouter()

router.include_router(chat_router, prefix="/chat", tags=["Chat AI Assistant"])
router.include_router(validate_router, prefix="/validate", tags=["Connection Validation"])

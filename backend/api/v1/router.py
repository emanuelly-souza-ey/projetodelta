from fastapi import APIRouter

from .endpoints.chat import router as chat_router
from .endpoints.validate_connection import router as validate_router
from .endpoints.examples import router as examples_router

router = APIRouter()

router.include_router(chat_router, prefix="/chat", tags=["Chat AI Assistant"])
router.include_router(validate_router, prefix="/validate", tags=["Connection Validation"])
router.include_router(examples_router, prefix="/examples", tags=["Classification Examples"])

try:
    from .endpoints.intent import router as intent_router
    router.include_router(intent_router, prefix="/test-intent", tags=["Intent Testing"])
except ImportError:
    pass


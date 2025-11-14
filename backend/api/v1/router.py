from fastapi import APIRouter
from .endpoints.chat import router as chat_router
from .endpoints.validate_connection import router as validate_router
from .endpoints.examples import router as examples_router
from backend.services.azure_client import chat_completion
from .endpoints.team import router as team_router
from .endpoints.projects import router as projects_router

router = APIRouter()

router.include_router(chat_router, prefix="/chat", tags=["Chat AI Assistant"])
router.include_router(validate_router, prefix="/validate", tags=["Connection Validation"])
router.include_router(examples_router, prefix="/examples", tags=["Classification Examples"])
router.include_router(team_router, prefix="/team", tags=["Project Team"])
router.include_router(projects_router, prefix="/projects", tags=["Projects"])

try:
    from .endpoints.intent import router as intent_router
    router.include_router(intent_router, prefix="/test-intent", tags=["Intent Testing"])
except ImportError:
    pass

@router.post("/chat/")
async def chat_endpoint(payload: dict):
    user_message = payload.get("message", "")
    result = await chat_completion(user_message)
    return {"response": result}
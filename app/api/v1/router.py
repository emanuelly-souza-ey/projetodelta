from fastapi import APIRouter
from app.api.v1.endpoints.devops import router as devops_router
from app.api.v1.endpoints.devops_epic import router as devops_epic

router = APIRouter()

router.include_router(devops_router, prefix="/devops", tags=["Azure DevOps"])
router.include_router(devops_epic, prefix="/epic", tags=["Epic Projects"])
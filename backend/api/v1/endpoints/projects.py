"""
Projects endpoint for retrieving available projects.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from backend.intents.project_search.service import ProjectSearchService
from backend.intents.project_search.models import ProjectSearchQuery
from backend.models.project_models import EpicProject


router = APIRouter()


class ProjectItem(BaseModel):
    """Simplified project model for frontend."""
    id: int
    name: str
    state: Optional[str] = None
    description: Optional[str] = None


class ProjectsResponse(BaseModel):
    """Response model for projects endpoint."""
    projects: List[ProjectItem] = Field(..., description="List of available projects")
    total_count: int = Field(..., description="Total number of projects")
    message: str = Field(..., description="Descriptive message")


@router.get("/", response_model=ProjectsResponse)
async def get_projects(
    state: Optional[str] = Query(None, description="Filter by project state (Active, Closed)")
):
    """
    Get all available projects from Azure DevOps.
    
    This endpoint retrieves Epic work items (projects) from Azure DevOps.
    Optionally filter by state.
    
    Args:
        state: Optional state filter (Active, Closed)
        
    Returns:
        ProjectsResponse with list of projects
        
    Raises:
        HTTPException: If the query fails
    """
    try:
        # Create service instance
        project_service = ProjectSearchService(session_id="anonymous")
        
        # Create query parameters
        query_params = ProjectSearchQuery(
            search_terms=[],
            filters={"state": state} if state else None,
            state=state
        )
        
        # Execute query
        result = await project_service.query_data(query_params)
        
        # Convert to simplified response
        project_items = [
            ProjectItem(
                id=p.id,
                name=p.name,
                state=p.state,
                description=p.description
            )
            for p in result.projects
        ]
        
        return ProjectsResponse(
            projects=project_items,
            total_count=result.total_found,
            message=f"Found {result.total_found} project(s)"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving projects: {str(e)}"
        )


@router.get("/active", response_model=ProjectsResponse)
async def get_active_projects():
    """
    Get only active projects.
    
    Convenience endpoint to retrieve only active projects.
    
    Returns:
        ProjectsResponse with list of active projects
    """
    return await get_projects(state="Active")


@router.get("/names")
async def get_project_names(
    state: Optional[str] = Query(None, description="Filter by project state")
):
    """
    Get simple list of project names.
    
    Lightweight endpoint that returns only project names,
    useful for autocomplete/dropdown menus.
    
    Args:
        state: Optional state filter
        
    Returns:
        Dict with list of project names
    """
    try:
        project_service = ProjectSearchService(session_id="anonymous")
        query_params = ProjectSearchQuery(
            search_terms=None,
            filters={"state": state} if state else None,
            state=state
        )
        
        result = await project_service.query_data(query_params)
        project_names = [p.name for p in result.projects]
        
        return {
            "project_names": project_names,
            "total_count": len(project_names)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving project names: {str(e)}"
        )

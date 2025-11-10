"""
Data models for project selection intent.
"""

from pydantic import Field
from typing import Optional, List, ClassVar

from backend.intents.base_intent.models import BaseQueryParams, BaseResponse
from backend.models.project_models import EpicProject


class ProjectSelectionQuery(BaseQueryParams):
    """Parameters for project selection queries."""
    
    REQUIRES_PROJECT: ClassVar[bool] = False
    
    user_query: Optional[str] = Field(
        None,
        description="Full user question text"
    )
    
    project_name: Optional[str] = Field(
        None,
        description="Specific project name to select"
    )

class ProjectSelectionResponse(BaseResponse):
    """Response for project selection queries."""
    
    selected: bool = Field(
        False,
        description="Whether a project was selected"
    )
    
    selected_project: Optional[EpicProject] = Field(
        None,
        description="The selected project if any"
    )
    
    ambiguous_projects: Optional[List[EpicProject]] = Field(
        None,
        description="Multiple matching projects requiring clarification"
    )
    
    suggested_projects: Optional[List[EpicProject]] = Field(
        None,
        description="Suggested projects from fallback search"
    )
    
    message: str = Field(
        "",
        description="Direct response message"
    )

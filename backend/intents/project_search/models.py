"""
Data models for project search intent.
"""

from pydantic import Field
from typing import Optional, List, Dict, ClassVar

from backend.intents.base_intent.models import BaseQueryParams, BaseResponse
from backend.models.project_models import EpicProject


class ProjectSearchQuery(BaseQueryParams):
    """Parameters for project search queries."""
    
    REQUIRES_PROJECT: ClassVar[bool] = False
    
    user_query: Optional[str] = Field(
        None,
        description="Full user question text"
    )
    
    search_terms: List[str] = Field(
        default_factory=list,
        description="Keywords extracted from the query for searching"
    )
    
    filters: Optional[Dict[str, str]] = Field(
        None,
        description="Optional filters like state (active/closed), tags, etc."
    )


class ProjectSearchResponse(BaseResponse):
    """Response for project search queries."""
    
    projects: List[EpicProject] = Field(
        default_factory=list,
        description="List of projects found matching the search"
    )
    
    total_found: int = Field(
        0,
        description="Total number of projects found"
    )
    
    search_summary: str = Field(
        "",
        description="Brief description of what was searched"
    )
    
    message: str = Field(
        "",
        description="Formatted presentation of results"
    )

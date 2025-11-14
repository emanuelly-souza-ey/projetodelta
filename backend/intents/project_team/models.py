"""
Models for project_team intent.
"""

from typing import Optional, List, ClassVar
from pydantic import BaseModel, Field

from backend.intents.base_intent.models import BaseQueryParams, BaseResponse


class ProjectTeamQuery(BaseQueryParams):
    """Parameters for project team queries."""
    
    REQUIRES_PROJECT: ClassVar[bool] = False


class TeamMember(BaseModel):
    """Individual team member data."""
    
    id: Optional[str] = Field(None, description="Member unique identifier")
    name: str = Field(..., description="Member display name")
    email: Optional[str] = Field(None, description="Member email address")
    role: Optional[str] = Field(None, description="Member role in the project")


class ProjectTeamResponse(BaseResponse):
    """Response with project team members data."""
    
    members: List[TeamMember] = Field(
        default_factory=list,
        description="List of team members"
    )
    total_count: int = Field(
        0,
        description="Total number of team members"
    )
    message: Optional[str] = Field(
        None,
        description="Optional message related to the project team"
    )
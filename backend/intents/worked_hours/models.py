"""
Data models for worked hours intent.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, ClassVar

from backend.intents.base_intent import BaseQueryParams, BaseResponse


class WorkedHoursQuery(BaseQueryParams):
    """Parameters extracted from user query for worked hours."""
    
    REQUIRES_PROJECT: ClassVar[bool] = True  # This intent requires a selected project
    
    person_name: Optional[str] = Field(
        None,
        description="Name of the person/team member"
    )
    
    start_date: Optional[str] = Field(
        None,
        description="Start date in ISO format (YYYY-MM-DD)"
    )
    
    end_date: Optional[str] = Field(
        None,
        description="End date in ISO format (YYYY-MM-DD)"
    )


class HourBreakdown(BaseModel):
    """Breakdown of hours for a specific item."""
    date: str
    task_title: str
    hours: float
    state: Optional[str] = None


class WorkedHoursResponse(BaseResponse):
    """Structured response for worked hours query."""
    
    person: Optional[str] = Field(None, description="Person name")
    total_hours: float = Field(0.0, description="Total hours worked")
    start_date: str = Field(..., description="Period start date")
    end_date: str = Field(..., description="Period end date")
    breakdown: List[HourBreakdown] = Field(default_factory=list, description="Hour breakdown by task")

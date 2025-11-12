"""
Models for get_tasks intent.
"""

from typing import Optional, List, ClassVar
from pydantic import BaseModel, Field

from backend.intents.base_intent.models import BaseQueryParams, BaseResponse


class GetTasksQuery(BaseQueryParams):
    """Parameters for get tasks queries."""
    
    REQUIRES_PROJECT: ClassVar[bool] = True
    
    user_query: Optional[str] = Field(
        None,
        description="Full user question text"
    )
    
    person_name: Optional[str] = Field(
        None,
        description="Name or partial name of one assigned person, if more than one leave empty"
    )
    
    task_state: Optional[str] = Field(
        None,
        description="Task state filter (Active, Completed, In Progress, etc.)"
    )
    
    task_type: Optional[str] = Field(
        None,
        description="Work item type filter (Task, Bug, User Story, etc.)"
    )
    
    start_date: Optional[str] = Field(
        None,
        description="Start date filter in YYYY-MM-DD format"
    )
    
    end_date: Optional[str] = Field(
        None,
        description="End date filter in YYYY-MM-DD format"
    )


class TaskItem(BaseModel):
    """Individual task item data."""
    
    id: int = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    state: str = Field(..., description="Task state")
    assigned_to: Optional[str] = Field(None, description="Assigned person name")
    work_item_type: Optional[str] = Field(None, description="Work item type")
    created_date: Optional[str] = Field(None, description="Creation date")
    changed_date: Optional[str] = Field(None, description="Last modification date")
    description: Optional[str] = Field(None, description="Task description")


class GetTasksResponse(BaseResponse):
    """Response for get tasks queries."""
    
    tasks: List[TaskItem] = Field(
        default_factory=list,
        description="List of tasks matching the criteria"
    )
    
    total_count: int = Field(
        0,
        description="Total number of tasks found"
    )
    
    tasks_by_person: dict = Field(
        default_factory=dict,
        description="Tasks grouped by assigned person (person_name: [task_titles])"
    )
    
    task_count_by_person: dict = Field(
        default_factory=dict,
        description="Number of tasks per person (person_name: count)"
    )
    
    filtered_by: dict = Field(
        default_factory=dict,
        description="Applied filters for the query"
    )
    
    message: str = Field(
        "",
        description="Human-readable summary message"
    )
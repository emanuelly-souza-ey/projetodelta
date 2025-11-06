"""
Base models for intent parameter extraction and responses.
All intent models should inherit from these base classes.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List, ClassVar
from abc import ABC


class BaseQueryParams(BaseModel, ABC):
    """
    Abstract base class for intent query parameters.
    Each intent should create its own QueryParams inheriting from this.
    
    Note: project_id is NOT extracted from user query - it's automatically
    enriched from conversation context by BaseIntentHandler.
    
    Example:
        class WorkedHoursQuery(BaseQueryParams):
            REQUIRES_PROJECT: ClassVar[bool] = True  # Override if project is required
            
            person_name: Optional[str]
            start_date: Optional[str]
            end_date: Optional[str]
    """
    
    # Class variable - NOT a Pydantic field, instructor cannot modify it
    REQUIRES_PROJECT: ClassVar[bool] = False
    
    project_id: Optional[str] = Field(
        None,
        description="Azure DevOps project ID from context",
        exclude=True  # Exclude from LLM extraction
    )
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        extra = "allow"  # Allow extra fields for flexibility


class BaseResponse(BaseModel, ABC):
    """
    Abstract base class for intent responses.
    Each intent should create its own Response inheriting from this.
    
    Example:
        class WorkedHoursResponse(BaseResponse):
            total_hours: float
            breakdown: List[HourBreakdown]
    """
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        extra = "allow"  # Allow extra fields for flexibility


class ErrorResponse(BaseModel):
    """Standard error response for all intents."""
    error_type: str = Field(..., description="Error type/category")
    error_message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

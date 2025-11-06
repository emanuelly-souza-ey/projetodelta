"""
Data models for the router agent system.
Uses dynamic intent registry instead of hardcoded categories.
"""

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


def get_intent_categories():
    """Get all registered intent categories dynamically."""
    # Import here to avoid circular dependency
    from backend.intents import IntentRegistry
    return IntentRegistry.get_categories()


def get_category_info():
    """Get category descriptions dynamically."""
    from backend.intents import IntentRegistry
    intents = IntentRegistry.get_all()
    return {
        category: f"{metadata.name} - {metadata.description}"
        for category, metadata in intents.items()
    }


class UserIntent(BaseModel):
    """
    Classified user intent.
    Category is validated against dynamically registered intents.
    """
    category: str = Field(..., description="Classified category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence (0-1)")
    reasoning: str = Field(..., description="Why this category")
    original_query: str = Field(default="", description="Original query")
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate that category is registered."""
        valid_categories = get_intent_categories()
        if v not in valid_categories:
            raise ValueError(
                f"Invalid category '{v}'. Must be one of: {', '.join(valid_categories)}"
            )
        return v


class RouterState(BaseModel):
    """Router workflow state."""
    user_query: str
    classified_intent: Optional[UserIntent] = None
    route_decision: Optional[str] = None
    error: Optional[str] = None

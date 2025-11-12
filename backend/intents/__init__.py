"""
Intent handlers module.
Auto-discovery and registration system for intents.
"""

from typing import Protocol, Dict, Any, Optional
from .registry import IntentRegistry


class IntentHandler(Protocol):
    """Protocol for intent handlers."""
    
    async def handle(self, query: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle the intent.
        
        Args:
            query: User query
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dictionary with data and conversation_id
        """
        ...


# Import all intents to trigger auto-registration
# These imports execute the register_intent() calls in each __init__.py
from . import worked_hours
from . import project_progress
from . import delayed_tasks
from . import project_team
from . import get_tasks
from . import project_selection  # Project selection - select specific project
from . import project_search  # Project search - explore and discover projects
from . import available_intents  # Help and available actions
from . import other  # DevOps queries not yet implemented
from . import default  # Non-DevOps queries

# Import examples (optional - only if examples.py exists)
try:
    from .worked_hours import examples as _  # noqa
    from .project_selection import examples as _  # noqa
    from .project_search import examples as _  # noqa
except ImportError:
    # No problem if examples.py doesn't exist for some intents
    pass


def get_handler(intent: str, session_id: Optional[str] = None) -> IntentHandler:
    """
    Factory function to get the appropriate handler for an intent.
    Uses the dynamic registry instead of hardcoded mapping.
    
    Args:
        intent: Intent category string
        session_id: Optional session ID for logging
        
    Returns:
        Handler instance for the intent
    """
    try:
        return IntentRegistry.get_handler(intent, session_id=session_id)
    except ValueError:
        # Fallback to not implemented handler if intent not found
        from .not_implemented import create_not_implemented_handler
        return create_not_implemented_handler(
            session_id=session_id,
            intent_name=intent  # Pass the unknown intent name for logging
        )


def get_all_intents() -> Dict[str, Any]:
    """Get all registered intents metadata."""
    return IntentRegistry.get_all()


def get_intent_descriptions() -> str:
    """Get formatted descriptions for LLM prompts."""
    return IntentRegistry.get_descriptions()


__all__ = [
    "get_handler",
    "get_all_intents",
    "get_intent_descriptions",
    "IntentHandler",
    "IntentRegistry"
]

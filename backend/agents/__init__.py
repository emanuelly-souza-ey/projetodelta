"""
Agents module for projetodelta.
Provides intent classification, routing, and answer generation.
"""

from .models import (
    UserIntent,
    RouterState
)

from .router_agent import RouterAgent

from .answer_agent import AnswerAgent
from .memory import ConversationMemory, get_memory


__all__ = [
    # Models
    "UserIntent",
    "RouterState",
    
    # Router Agent
    "RouterAgent",
    
    # Answer Agent
    "AnswerAgent",
    
    # Memory
    "ConversationMemory",
    "get_memory",
]

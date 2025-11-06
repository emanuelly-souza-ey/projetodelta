"""
Dynamic intent registry system.
Intents auto-register themselves with metadata.
"""

from typing import Dict, List, Type, Any, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass


@dataclass
class IntentMetadata:
    """Metadata for an intent."""
    category: str  # Unique identifier (e.g., "worked_hours")
    name: str  # Display name (e.g., "Horas Trabalhadas")
    description: str  # Full description for classification
    handler_class: Type[Any]  # Handler class for this intent
    agent_name: str = None  # Optional agent name (defaults to category_agent)
    
    def get_agent_name(self) -> str:
        """Get agent name, using category as default if not specified."""
        return self.agent_name or f"{self.category}_agent"


class IntentRegistry:
    """
    Central registry for all intents.
    Intents auto-register on import.
    """
    
    _intents: Dict[str, IntentMetadata] = {}
    
    @classmethod
    def register(cls, metadata: IntentMetadata):
        """Register an intent with its metadata."""
        if metadata.category in cls._intents:
            raise ValueError(f"Intent '{metadata.category}' is already registered")
        cls._intents[metadata.category] = metadata
    
    @classmethod
    def get_all(cls) -> Dict[str, IntentMetadata]:
        """Get all registered intents."""
        return cls._intents.copy()
    
    @classmethod
    def get(cls, category: str) -> IntentMetadata:
        """Get metadata for a specific intent."""
        if category not in cls._intents:
            raise ValueError(f"Intent '{category}' not found")
        return cls._intents[category]
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get list of all registered categories."""
        return list(cls._intents.keys())
    
    @classmethod
    def get_descriptions(cls) -> str:
        """Get formatted descriptions for all intents (for LLM prompt)."""
        lines = []
        for category, metadata in cls._intents.items():
            lines.append(f"- {category}: {metadata.name} - {metadata.description}")
        return "\n".join(lines)
    
    @classmethod
    def get_handler(cls, category: str, session_id: Optional[str] = None):
        """
        Get handler instance for an intent.
        Handles both classes and factory functions.
        
        Args:
            category: Intent category
            session_id: Optional session ID for logging
        """
        metadata = cls.get(category)
        handler_factory = metadata.handler_class
        
        # If it's a callable (class or factory function), call it with session_id
        if callable(handler_factory):
            return handler_factory(session_id=session_id)
        
        # If it's already an instance, return it
        return handler_factory


# Export for convenience
def register_intent(metadata: IntentMetadata):
    """Decorator or function to register an intent."""
    IntentRegistry.register(metadata)


def get_intent_registry() -> IntentRegistry:
    """Get the intent registry."""
    return IntentRegistry

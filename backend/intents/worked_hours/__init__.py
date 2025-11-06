"""
Worked Hours Intent.
Auto-registers with the intent registry.
"""

from backend.intents.registry import IntentMetadata, register_intent
from backend.intents.base_intent import BaseIntentHandler
from .extractor import WorkedHoursExtractor
from .service import WorkedHoursService
from .models import WorkedHoursQuery, WorkedHoursResponse


# Factory function to create handler with composition
def create_worked_hours_handler(session_id: str = None):
    """
    Create handler using composition of extractor and service.
    
    Args:
        session_id: Optional chat session ID for logging
    """
    intent_name = "worked_hours"
    
    return BaseIntentHandler(
        extractor=WorkedHoursExtractor(session_id=session_id, intent_name=intent_name),
        service=WorkedHoursService(session_id=session_id, intent_name=intent_name),
        session_id=session_id,
        intent_name=intent_name
    )


# Intent metadata
INTENT_METADATA = IntentMetadata(
    category="worked_hours",
    name="Horas Trabalhadas e Previstas",
    description="Consultas sobre horas trabalhadas, horas previstas, tempo gasto em tarefas",
    handler_class=create_worked_hours_handler,
    agent_name="hours_agent"
)

# Auto-register this intent
register_intent(INTENT_METADATA)

__all__ = ["create_worked_hours_handler", "WorkedHoursQuery", "WorkedHoursResponse", "INTENT_METADATA"]

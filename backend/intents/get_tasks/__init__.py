"""
Get Tasks Intent.
Auto-registers with the intent registry.
"""

from backend.intents.registry import IntentMetadata, register_intent
from backend.intents.base_intent import BaseIntentHandler
from .extractor import GetTasksExtractor
from .service import GetTasksService
from .models import GetTasksQuery, GetTasksResponse


def create_get_tasks_handler(session_id=None):
    """
    Create handler using composition of extractor and service.
    
    Args:
        session_id: Optional chat session ID for logging
    """
    intent_name = "get_tasks"
    
    return BaseIntentHandler(
        extractor=GetTasksExtractor(session_id=session_id, intent_name=intent_name),
        service=GetTasksService(session_id=session_id, intent_name=intent_name),
        session_id=session_id,
        intent_name=intent_name
    )


# Register intent with metadata
INTENT_METADATA = IntentMetadata(
    category="get_tasks",
    name="Obter Tarefas",
    description="Consultar tarefas do Azure DevOps. Exemplos: 'quais são minhas tarefas?', 'tarefas ativas do projeto X', 'tasks atribuídas para João', 'work items em progresso', 'tasks com tag de atraso",
    handler_class=create_get_tasks_handler,
    agent_name="devops_agent",
    requires_llm=True
)

register_intent(INTENT_METADATA)

__all__ = [
    "create_get_tasks_handler", 
    "GetTasksQuery",
    "GetTasksResponse",
    "INTENT_METADATA"
]
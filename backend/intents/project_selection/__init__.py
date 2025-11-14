"""
Project Selection Intent.
Auto-registers with the intent registry.
"""

from backend.intents.registry import IntentMetadata, register_intent
from backend.intents.base_intent import BaseIntentHandler
from .extractor import ProjectSelectionExtractor
from .service import ProjectSelectionService
from .models import ProjectSelectionQuery, ProjectSelectionResponse


def create_project_selection_handler(session_id=None):
    """
    Create handler using composition of extractor and service.
    
    Args:
        session_id: Optional chat session ID for logging
    """
    intent_name = "project_selection"
    
    return BaseIntentHandler(
        extractor=ProjectSelectionExtractor(session_id=session_id, intent_name=intent_name),
        service=ProjectSelectionService(session_id=session_id, intent_name=intent_name),
        session_id=session_id,
        intent_name=intent_name
    )


INTENT_METADATA = IntentMetadata(
    category="project_selection",
    name="Seleção de Projeto",
    description="Selecionar um projeto ESPECÍFICO por nome ou número para trabalhar nele. O usuário DEVE mencionar qual projeto quer selecionar. Exemplos: 'selecionar projeto Delta', 'quero trabalhar no projeto 1', 'escolher projeto X', 'mudar para projeto GenAI', 'seleciona o projeto ABC'. NÃO use este intent para: desselecionar, voltar para todos os projetos, ver todos os projetos.",
    handler_class=create_project_selection_handler,
    agent_name="project_agent"
)

register_intent(INTENT_METADATA)

__all__ = [
    "create_project_selection_handler",
    "ProjectSelectionQuery",
    "ProjectSelectionResponse",
    "INTENT_METADATA"
]

"""
Project Search Intent.
Auto-registers with the intent registry.
"""

from backend.intents.registry import IntentMetadata, register_intent
from backend.intents.base_intent import BaseIntentHandler
from .extractor import ProjectSearchExtractor
from .service import ProjectSearchService
from .models import ProjectSearchQuery, ProjectSearchResponse


# Factory function to create handler with composition
def create_project_search_handler(session_id: str = None):
    """
    Create handler using composition of extractor and service.
    
    Args:
        session_id: Optional chat session ID for logging
    """
    intent_name = "project_search"
    
    return BaseIntentHandler(
        extractor=ProjectSearchExtractor(session_id=session_id, intent_name=intent_name),
        service=ProjectSearchService(session_id=session_id, intent_name=intent_name),
        session_id=session_id,
        intent_name=intent_name
    )


# Intent metadata
INTENT_METADATA = IntentMetadata(
    category="project_search",
    name="Busca e Exploração de Projetos",
    description="Explorar, buscar e listar projetos disponíveis usando palavras-chave. Exemplos: 'mostrar projetos de IA', 'quais projetos temos?', 'listar projetos ativos', 'buscar projetos com Python'",
    handler_class=create_project_search_handler,
    agent_name="search_agent"
)

# Auto-register this intent
register_intent(INTENT_METADATA)

__all__ = ["create_project_search_handler", "ProjectSearchQuery", "ProjectSearchResponse", "INTENT_METADATA"]

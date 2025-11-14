"""
Project Team Intent.
Auto-registers with the intent registry.
"""

from typing import Optional, Dict

from backend.intents.registry import IntentMetadata, register_intent
from backend.intents.base_intent import BaseIntentHandler, BaseExtractor
from .service import ProjectTeamService
from .models import ProjectTeamQuery, ProjectTeamResponse


class _MinimalExtractor(BaseExtractor[ProjectTeamQuery]):
    """Minimal extractor that returns base parameters without LLM processing."""
    
    async def extract_params(self, query: str, context: Optional[Dict] = None) -> ProjectTeamQuery:
        return ProjectTeamQuery()


def create_project_team_handler(session_id=None):
    """
    Create handler using composition of minimal extractor and service.
    
    Args:
        session_id: Optional chat session ID for logging
    """
    intent_name = "project_team"
    
    
    return BaseIntentHandler(
        extractor=_MinimalExtractor(session_id=session_id, intent_name=intent_name),
        service=ProjectTeamService(session_id=session_id, intent_name=intent_name),
        session_id=session_id,
        intent_name=intent_name
    )


# Register intent with metadata
INTENT_METADATA = IntentMetadata(
    category="project_team",
    name="Equipe do Projeto",
    description="Consultar membros da equipe, integrantes, colaboradores do projeto. Exemplos: 'quem está no time?', 'quem está na equipe?', 'mostrar equipe', 'listar integrantes', 'quais são os membros?', 'pessoas do projeto'",
    handler_class=create_project_team_handler,
    agent_name="devops_agent",
    requires_llm=True
)

register_intent(INTENT_METADATA)

__all__ = [
    "create_project_team_handler",
    "ProjectTeamQuery",
    "ProjectTeamResponse",
    "INTENT_METADATA"
]

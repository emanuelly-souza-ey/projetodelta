"""
Project Progress Intent.
TODO: Implement full functionality.
"""

from backend.intents.registry import IntentMetadata, register_intent
from backend.intents.not_implemented import create_not_implemented_handler


# Intent metadata
INTENT_METADATA = IntentMetadata(
    category="project_progress",
    name="Progresso Geral do Projeto",
    description="Consultas sobre o andamento, status e progresso geral do projeto",
    handler_class=create_not_implemented_handler,
    agent_name="progress_agent"
)

# Auto-register this intent
register_intent(INTENT_METADATA)

__all__ = ["create_not_implemented_handler", "INTENT_METADATA"]

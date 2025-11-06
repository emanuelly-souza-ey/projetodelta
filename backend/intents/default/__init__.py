"""
Default Intent.
Fallback for queries that are NOT related to Azure DevOps.
"""

from backend.intents.registry import IntentMetadata, register_intent
from .handler import create_default_handler


# Intent metadata
INTENT_METADATA = IntentMetadata(
    category="default",
    name="Consulta Não Relacionada",
    description="Perguntas não relacionadas ao Azure DevOps (clima, futebol, conversas gerais, etc.)",
    handler_class=create_default_handler,
    agent_name="default_agent",
    requires_llm=False  # Direct response, no LLM needed
)

# Auto-register this intent
register_intent(INTENT_METADATA)

__all__ = ["create_default_handler", "INTENT_METADATA"]

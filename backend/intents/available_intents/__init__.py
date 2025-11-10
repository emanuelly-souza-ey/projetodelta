"""
Default Intent.
Fallback for queries that are NOT related to Azure DevOps.
"""

from backend.intents.registry import IntentMetadata, register_intent
from .handler import create_available_actions_handler


# Intent metadata
INTENT_METADATA = IntentMetadata(
    category="available_intents",
    name="Ajuda e Funcionalidades",
    description="Consultas sobre o que o assistente pode fazer, lista de funcionalidades disponíveis, comandos e ações possíveis (ex: 'o que você pode fazer?', 'me ajuda', 'quais são as opções?')",
    handler_class=create_available_actions_handler,
    agent_name="help_agent",
    requires_llm=False  # Direct response, no LLM processing needed
)

# Auto-register this intent
register_intent(INTENT_METADATA)

__all__ = ["create_available_actions_handler", "INTENT_METADATA"]

"""
Project Team Intent.
TODO: Implement full functionality.
"""

from backend.intents.registry import IntentMetadata, register_intent
from backend.intents.not_implemented import create_not_implemented_handler


# Intent metadata
INTENT_METADATA = IntentMetadata(
    category="project_team",
    name="Equipe do Projeto",
    description="Consultas sobre membros da equipe, recursos humanos, responsáveis",
    handler_class=create_not_implemented_handler,
    agent_name="team_agent"
)

# Auto-register this intent
register_intent(INTENT_METADATA)

# Placeholder handler
__all__ = ["create_not_implemented_handler", "INTENT_METADATA"]

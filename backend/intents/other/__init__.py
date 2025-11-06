"""
Other DevOps Intent.
For Azure DevOps queries that are valid but not yet implemented.
"""

from backend.intents.registry import IntentMetadata, register_intent
from .handler import create_other_handler


# Intent metadata
INTENT_METADATA = IntentMetadata(
    category="other",
    name="Outras Consultas DevOps",
    description="Consultas válidas sobre Azure DevOps que ainda não foram implementadas (repos, builds, releases, etc.)",
    handler_class=create_other_handler,
    agent_name="other_agent",
    requires_llm=False  # Direct response for not-yet-implemented features
)

# Auto-register this intent
register_intent(INTENT_METADATA)

__all__ = ["create_other_handler", "INTENT_METADATA"]

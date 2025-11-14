"""
Project Deselection Intent.
Clears the currently selected project to view all projects.
"""

from backend.intents.registry import IntentMetadata, register_intent
from .handler import create_project_deselection_handler


# Intent metadata
INTENT_METADATA = IntentMetadata(
    category="project_deselection",
    name="Deseleção de Projeto",
    description="Desselecionar/remover/limpar o projeto atual para voltar a ver informações de TODOS os projetos disponíveis. Use APENAS quando o usuário quer explicitamente SAIR/DESSELECIONAR/REMOVER o projeto atual ou contexto específico. Palavras-chave: 'desselecionar', 'remover projeto', 'limpar projeto', 'sair do projeto', 'voltar para todos', 'remover seleção', 'limpar seleção'.",
    handler_class=create_project_deselection_handler,
    agent_name="project_deselection_agent",
    requires_llm=False  # Direct response, no LLM needed
)

# Auto-register this intent
register_intent(INTENT_METADATA)

__all__ = ["create_project_deselection_handler", "INTENT_METADATA"]

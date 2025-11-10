"""
Example prompts for project_search intent classification.
"""

from backend.intents.intent_examples import register_examples

EXAMPLES = [
    "Mostrar projetos de IA disponíveis",
    "Quais projetos temos no momento?",
    "Listar projetos ativos",
    "Buscar projetos com Python",
    "Encontrar projetos de Machine Learning"
]

# Auto-register examples
register_examples("project_search", EXAMPLES)
"""
Example prompts for project_team intent classification.
"""

from backend.intents.intent_examples import register_examples

EXAMPLES = [
    # Basic team queries
    "Quem está no time?",
    "Mostrar equipe do projeto",
    "Listar integrantes",
    "Quais são os membros da equipe?",
    
    # Team information
    "Quem faz parte do projeto?",
    "Mostre os colaboradores",
    "Lista de pessoas no projeto",
    "Equipe atual",
    
    # Variations
    "Integrantes do time",
    "Membros do projeto",
    "Pessoas trabalhando no projeto",
    "Quem trabalha neste projeto?"
]

# Auto-register examples
register_examples("project_team", EXAMPLES)

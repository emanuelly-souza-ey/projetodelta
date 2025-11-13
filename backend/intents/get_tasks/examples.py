"""
Example prompts for get_tasks intent classification.
"""

from backend.intents.intent_examples import register_examples

EXAMPLES = [
    # Basic task queries
    "Quais são minhas tarefas?",
    "Mostrar minhas tasks",
    "Listar work items atribuídos para mim",
    
    # State-based queries
    "Tarefas ativas",
    "Tasks em progresso", 
    "Work items completados",
    "Tarefas pendentes",
    
    # Person-based queries
    "Tarefas do João",
    "Tasks atribuídas para Maria",
    "Work items da equipe",
    
    # Type-based queries
    "Mostrar bugs",
    "Listar user stories",
    "Tasks do tipo Feature",
    
    # Combined queries
    "Bugs ativos do Pedro",
    "User stories completadas esta semana",
    "Tasks em progresso do projeto X",
    
    # Date-based queries
    "Tarefas desta semana",
    "Work items do mês passado",
    "Tasks criadas hoje"
]

# Auto-register examples
register_examples("get_tasks", EXAMPLES)
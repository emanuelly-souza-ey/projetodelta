"""
Example prompts for worked_hours intent classification.
"""

from backend.intents.intent_examples import register_examples

EXAMPLES = [
    "Quantas horas trabalhei hoje?",
    "Mostrar horas trabalhadas esta semana",
    "Qual foi meu tempo trabalhado ontem?",
    "Horas previstas vs trabalhadas do projeto",
    "Relatório de tempo gasto nas tarefas"
]

# Auto-register examples
register_examples("worked_hours", EXAMPLES)
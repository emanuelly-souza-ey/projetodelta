"""
Example prompts for project_selection intent classification.
"""

from backend.intents.intent_examples import register_examples

EXAMPLES = [
    "Selecionar projeto Delta",
    "Quero trabalhar no GenAI",
    "Mudar para projeto Python Tools",
    "Escolher o primeiro projeto",
    "2"  # Number selection after listing
]

# Auto-register examples
register_examples("project_selection", EXAMPLES)
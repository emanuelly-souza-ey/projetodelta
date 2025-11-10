"""
Examples endpoint for intent classification testing.
Provides example prompts to test router agent classification.
"""

from fastapi import APIRouter, Query
from typing import Optional, List
from backend.intents.intent_examples import IntentExamplesRegistry, ExamplePrompt

router = APIRouter()


@router.get("/examples", response_model=List[ExamplePrompt])
async def get_classification_examples(
    category: Optional[str] = Query(None, description="Filtrar por categoria específica de intent")
):
    """
    Obter exemplos de prompts para teste de classificação de intents.
    
    - **category**: (Opcional) Categoria do intent para filtrar exemplos específicos
    
    Returns:
        Lista de exemplos de prompts com suas categorias
    """
    examples = IntentExamplesRegistry.get_all(category)
    return examples


@router.get("/examples/categories", response_model=List[str])
async def get_example_categories():
    """
    Obter lista de categorias que possuem exemplos disponíveis.
    
    Returns:
        Lista de categorias de intents com exemplos
    """
    categories = IntentExamplesRegistry.get_categories()
    return categories
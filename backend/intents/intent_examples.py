"""
Intent examples registry system.
Intents can optionally register example prompts for classification testing.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class ExamplePrompt(BaseModel):
    """Example prompt for intent classification testing."""
    
    category: str
    prompt: str
    expected_confidence: Optional[float] = None


class IntentExamplesRegistry:
    """
    Central registry for intent classification examples.
    Intents can optionally register examples for testing.
    """
    
    _examples: Dict[str, List[str]] = {}
    
    @classmethod
    def register(cls, category: str, examples: List[str]):
        """
        Register examples for an intent category.
        
        Args:
            category: Intent category name
            examples: List of example prompts in Portuguese
        """
        cls._examples[category] = examples
    
    @classmethod
    def get(cls, category: str) -> List[str]:
        """
        Get examples for a specific category.
        
        Args:
            category: Intent category name
            
        Returns:
            List of example prompts for the category
        """
        return cls._examples.get(category, [])
    
    @classmethod
    def get_all(cls, category: Optional[str] = None) -> List[ExamplePrompt]:
        """
        Get all examples, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of ExamplePrompt objects
        """
        if category:
            prompts = cls._examples.get(category, [])
            return [ExamplePrompt(category=category, prompt=p) for p in prompts]
        
        result = []
        for cat, prompts in cls._examples.items():
            result.extend([ExamplePrompt(category=cat, prompt=p) for p in prompts])
        return result
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get list of categories that have examples."""
        return list(cls._examples.keys())


def register_examples(category: str, examples: List[str]):
    """
    Helper function to register examples for an intent.
    
    Args:
        category: Intent category name
        examples: List of example prompts
    """
    IntentExamplesRegistry.register(category, examples)


__all__ = [
    "ExamplePrompt", 
    "IntentExamplesRegistry", 
    "register_examples"
]
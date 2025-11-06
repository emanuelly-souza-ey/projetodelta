"""
Router Agent implementation using instructor and langgraph.
Classifies user intents and routes to appropriate specialized agents.
Uses dynamic intent registry.
"""

from typing import Optional
from backend.config import get_azure_config
from backend.config.logging import chat_logger
# Moved import inside functions to avoid circular dependency
from backend.intents.registry import IntentRegistry
from .models import UserIntent, RouterState


class RouterAgent:
    """
    Router agent that classifies user queries and routes them to specialized agents.
    Uses instructor for structured outputs and is designed to work with langgraph.
    """
    
    CLASSIFICATION_PROMPT = """Você é um assistente de classificação de intenções. 
        Analise a consulta do usuário e determine qual categoria melhor representa sua intenção.

        Categorias disponíveis:
        {categories}

        Instruções:
        1. Analise cuidadosamente a consulta do usuário
        2. Identifique palavras-chave e o contexto da pergunta
        3. Selecione a categoria que melhor representa a intenção
        4. Se não houver correspondência clara, escolha a categoria mais próxima
        5. Em caso de dúvida, use a categoria "other"
        6. Forneça uma pontuação de confiança honesta (0.0 a 1.0)
        7. Explique brevemente seu raciocínio

        Consulta do usuário: {query}
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the router agent using shared Azure config.
        
        Args:
            session_id: Optional chat session ID for logging
        """
        self.azure_config = get_azure_config()
        self.session_id = session_id
        
        # Use structured component logger for ROUTER
        if session_id:
            self.logger = chat_logger.get_component_logger(
                session_id=session_id,
                component='ROUTER'
            )
        else:
            self.logger = None
        
    def classify_intent(self, query: str) -> UserIntent:
        """Classify user intent using dynamically registered intents."""
        if self.logger:
            self.logger.info(f"Classifying intent for query: {query}")
        
        # Import here to avoid circular dependency
        from backend.intents import get_intent_descriptions
        categories_text = get_intent_descriptions()
        prompt = self.CLASSIFICATION_PROMPT.format(categories=categories_text, query=query)
        
        # When response_model is provided, instructor returns the Pydantic model directly
        intent = self.azure_config.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are an intent classification assistant."},
                {"role": "user", "content": prompt}
            ],
            response_model=UserIntent,
            temperature=0.3,
            max_tokens=500
        )
        
        # intent is UserIntent when response_model is provided
        intent.original_query = query  # type: ignore[attr-defined]
        
        if self.logger:
            self.logger.info(
                f"Intent classified: {intent.category} (confidence: {intent.confidence:.2f}) - {intent.reasoning}"  # type: ignore[attr-defined]
            )
        
        return intent  # type: ignore[return-value]
    
    def route_to_agent(self, intent: UserIntent) -> str:
        """Determine which agent should handle the intent using dynamic registry."""
        try:
            intent_metadata = IntentRegistry.get(intent.category)
            return intent_metadata.get_agent_name()
        except ValueError:
            # Fallback to default agent if intent not found in registry
            if self.logger:
                self.logger.warning(
                    f"Intent '{intent.category}' not found in registry, using default handler"
                )
            return "default_agent"
    
    def process_query(self, query: str) -> dict:
        """Process a user query: classify and route."""
        try:
            intent = self.classify_intent(query)
            target_agent = self.route_to_agent(intent)
            
            return {
                "success": True,
                "query": query,
                "intent": {
                    "category": intent.category,
                    "confidence": intent.confidence,
                    "reasoning": intent.reasoning
                },
                "route_to": target_agent,
                "error": None
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "query": query,
                "intent": None,
                "route_to": "default_agent",
                "error": str(e)
            }


__all__ = ["RouterAgent"]

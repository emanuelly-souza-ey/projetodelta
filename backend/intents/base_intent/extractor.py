"""
Base extractor for parameter extraction from natural language.
All intent extractors should inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict

from backend.config import get_azure_config
from backend.config.logging import chat_logger
from .models import BaseQueryParams


class BaseExtractor(ABC):
    """
    Abstract base class for parameter extractors.
    Uses LLM to extract structured parameters from natural language queries.
    
    Each intent must implement:
    - EXTRACTION_PROMPT: Prompt template for parameter extraction
    - extract_params(): Method to extract parameters
    """
    
    # Subclasses must define their own extraction prompt
    EXTRACTION_PROMPT: str = ""
    
    def __init__(self, session_id: Optional[str] = None, intent_name: Optional[str] = None):
        """
        Initialize the extractor with shared Azure config.
        
        Args:
            session_id: Optional chat session ID for logging
            intent_name: Optional intent name for structured logging
        """
        self.azure_config = get_azure_config()
        self.session_id = session_id
        self.intent_name = intent_name
        
        # Use structured component logger if session_id provided
        if session_id:
            self.logger = chat_logger.get_component_logger(
                session_id=session_id,
                component='EXTRACTOR',
                intent_name=intent_name
            )
        else:
            self.logger = None
    
    @abstractmethod
    async def extract_params(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> BaseQueryParams:
        """
        Extract parameters from natural language query.
        
        Args:
            query: User's natural language query
            context: Optional conversation context from previous interactions
            
        Returns:
            BaseQueryParams subclass with extracted parameters
            
        Example implementation:
            async def extract_params(self, query, context):
                if self.logger:
                    self.logger.info(f"Extracting parameters from query: {query}")
                
                prompt = self.EXTRACTION_PROMPT.format(query=query, context=context)
                
                try:
                    params = self.azure_config.create_chat_completion(
                        messages=[
                            {"role": "system", "content": "You are a parameter extraction assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        response_model=YourQueryParamsClass,
                        temperature=0.1,
                        max_tokens=500
                    )
                    
                    if self.logger:
                        self.logger.info(f"Parameters extracted successfully: {params.dict()}")
                    
                    return params
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Failed to extract parameters: {str(e)}", exc_info=True)
                    raise
        """
        pass
    
    def _format_context(self, context: Optional[Dict]) -> str:
        """
        Helper method to format conversation context.
        
        Args:
            context: Conversation context dictionary
            
        Returns:
            Formatted context string for prompt
        """
        if not context:
            return "No previous context available."
        
        parts = []
        if context.get("last_query"):
            parts.append(f"Previous query: {context['last_query']}")
        if context.get("last_params"):
            parts.append(f"Previous parameters: {context['last_params']}")
        if context.get("last_intent"):
            parts.append(f"Previous intent: {context['last_intent']}")
        
        return "\n".join(parts) if parts else "No previous context available."

"""
Base handler for intent orchestration.
Uses composition to combine extractor and service.
"""

from typing import Dict, Any, Optional
from uuid import uuid4
import time

from backend.agents.memory import get_memory
from backend.config.logging import chat_logger
from .extractor import BaseExtractor
from .service import BaseService


def _to_dict(obj: Any) -> Dict[str, Any]:
    """
    Convert object to dictionary, handling Pydantic models.
    
    Args:
        obj: Object to convert (can be dict, Pydantic model, or other)
        
    Returns:
        Dictionary representation
    """
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return obj
    else:
        return {"value": obj}


class BaseIntentHandler:
    """
    Concrete handler that uses composition to combine extractor and service.
    No need to subclass - just provide extractor and service instances.
    
    Usage:
        handler = BaseIntentHandler(
            extractor=MyExtractor(),
            service=MyService(),
            session_id="chat_123"
        )
    """
    
    def __init__(
        self, 
        extractor: BaseExtractor, 
        service: BaseService,
        session_id: Optional[str] = None,
        intent_name: Optional[str] = None
    ):
        """
        Initialize handler with extractor and service.
        
        Args:
            extractor: Instance of BaseExtractor subclass
            service: Instance of BaseService subclass
            session_id: Optional chat session ID for logging
            intent_name: Optional intent name for structured logging
        """
        self.memory = get_memory()
        self.extractor = extractor
        self.service = service
        self.session_id = session_id
        self.intent_name = intent_name
        
        # Use structured component logger if session_id provided
        if session_id:
            self.logger = chat_logger.get_component_logger(
                session_id=session_id,
                component='HANDLER',
                intent_name=intent_name
            )
        else:
            self.logger = None
    
    async def handle(self, query: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Orchestrates the complete intent handling flow.
        
        Flow:
        1. Get conversation context from memory
        2. Extract parameters from query (using extractor)
        3. Query service for data (using service)
        4. Save to memory
        5. Return structured response
        
        Args:
            query: User query
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dictionary with data and conversation_id
        """
        start_time = time.time()
        
        if self.logger:
            self.logger.info(f"Starting intent handling for query: {query}")
        
        try:
            # 1. Get conversation context
            context = self.memory.get_context(conversation_id) if conversation_id else {}
            
            if self.logger and context:
                self.logger.info(f"Retrieved conversation context: {len(context)} items")
            
            # 2. Extract parameters from query
            if self.logger:
                self.logger.info("Extracting parameters...")
            
            params = await self.extractor.extract_params(query, context)
            params_dict = _to_dict(params)
            
            if self.logger:
                self.logger.info(f"Parameters extracted: {params_dict}")
            
            # 3. Query service for data
            if self.logger:
                self.logger.info("Querying service for data...")
            
            response_data = await self.service.query_data(params)
            
            if self.logger:
                self.logger.info("Data retrieved successfully from service")
            
            # 4. Convert to dictionary (handle both dict and Pydantic models)
            data = _to_dict(response_data)
            
            # 5. Save to memory
            new_conversation_id = self.memory.save(
                conversation_id or str(uuid4()),
                query=query,
                intent=self.__class__.__name__,
                params=params_dict,
                result=data
            )
            
            elapsed_time = time.time() - start_time
            
            if self.logger:
                self.logger.info(f"Intent handling completed successfully in {elapsed_time:.2f}s")
            
            return {
                "data": data,
                "conversation_id": new_conversation_id,
                "success": True
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            
            if self.logger:
                self.logger.error(
                    f"Intent handling failed after {elapsed_time:.2f}s: {type(e).__name__} - {str(e)}",
                    exc_info=True
                )
            
            # Return error in structured format
            error_id = conversation_id or str(uuid4())
            return {
                "data": {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "message": f"Error processing query: {str(e)}"
                },
                "conversation_id": error_id,
                "success": False
            }

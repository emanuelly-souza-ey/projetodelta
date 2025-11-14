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
            
            # 3. Enrich params with project_id from context
            project_context = context.get("project_context", {})
            context_project_id = project_context.get("project_id")
            if context_project_id:
                # Handle both Pydantic model and dict
                if hasattr(params, 'project_id'):
                    params.project_id = context_project_id
                elif isinstance(params, dict):
                    params['project_id'] = context_project_id
                    
                if self.logger:
                    self.logger.info(f"Enriched params with project_id from context: {context_project_id}")
            
            # 4. Validate project requirement
            # Check if params is dict or has the attribute
            requires_project = False
            if isinstance(params, dict):
                requires_project = params.get('REQUIRES_PROJECT', False)
            else:
                requires_project = getattr(params.__class__, 'REQUIRES_PROJECT', False)
            
            if requires_project:
                # Check project_id in both dict and object formats
                has_project = False
                if isinstance(params, dict):
                    has_project = bool(params.get('project_id'))
                else:
                    has_project = bool(getattr(params, 'project_id', None))
                    
                if not has_project:
                    error_msg = "Este intent requer que um projeto esteja selecionado. Por favor, selecione um projeto primeiro."
                    if self.logger:
                        self.logger.warning(f"Project required but not found in context")
                    raise ValueError(error_msg)
            # [_] TODO Return Natural language message if this action needs a project selected
            
            params_dict = _to_dict(params)
            
            if self.logger:
                self.logger.info(f"Parameters extracted: {params_dict}")
            
            # 4. Query service for data
            if self.logger:
                self.logger.info("Querying service for data...")
            
            # Add conversation_id to params for services that need it (like deselection)
            params_dict['conversation_id'] = conversation_id
            
            response_data = await self.service.query_data(params_dict)
            
            if self.logger:
                self.logger.info("Data retrieved successfully from service")
            
            # 4. Convert to dictionary (handle both dict and Pydantic models)
            data = _to_dict(response_data)
            
            # 5. Save to memory (preserving project context, except for project_selection and project_deselection)
            # For project_selection, let the new project context from service take precedence
            # For project_deselection, the service already cleared the context, don't preserve it
            preserve_context = None
            if self.intent_name not in ["project_selection", "project_deselection"]:
                preserve_context = project_context
            
            new_conversation_id = self.memory.save(
                conversation_id or str(uuid4()),
                query=query,
                intent=self.__class__.__name__,
                params=params_dict,
                result=data,
                project_context=preserve_context
            )
            
            elapsed_time = time.time() - start_time
            
            if self.logger:
                self.logger.info(f"Intent handling completed successfully in {elapsed_time:.2f}s")
            
            return {
                "data": data,
                "conversation_id": new_conversation_id,
                "extracted_params": params_dict,
                "success": True
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            
            if self.logger:
                self.logger.error(
                    f"Intent handling failed after {elapsed_time:.2f}s: {type(e).__name__} - {str(e)}",
                    exc_info=True
                )
            
            # Return error in structured format with debug info
            error_id = conversation_id or str(uuid4())
            return {
                "data": {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "message": f"Error processing query: {str(e)}",
                    "debug_info": {
                        "original_query": query,
                        "intent": self.intent_name,
                        "elapsed_time": f"{elapsed_time:.2f}s"
                    }
                },
                "conversation_id": error_id,
                "success": False
            }

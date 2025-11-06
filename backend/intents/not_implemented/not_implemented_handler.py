"""
Not Implemented Intent Handler.
Placeholder for intents that are not yet fully implemented.
"""

from typing import Dict, Optional

from backend.intents.base_intent import (
    BaseExtractor, 
    BaseService, 
    BaseIntentHandler,
    BaseQueryParams,
    BaseResponse
)


class NotImplementedQueryParams(BaseQueryParams):
    """Query parameters for not implemented intent - just captures the raw query."""
    query: str


class NotImplementedResponse(BaseResponse):
    """Response for not implemented intent."""
    message: str
    query: str


class NotImplementedExtractor(BaseExtractor):
    """Placeholder extractor - no actual extraction needed."""
    
    def __init__(self, session_id: Optional[str] = None, intent_name: Optional[str] = None):
        super().__init__(session_id=session_id, intent_name=intent_name)
    
    async def extract_params(
        self, 
        query: str, 
        context: Optional[Dict] = None
    ) -> NotImplementedQueryParams:
        """No parameter extraction needed for placeholder."""
        if self.logger:
            self.logger.info(f"Not implemented intent - query: {query}")
        return NotImplementedQueryParams(query=query)


class NotImplementedService(BaseService):
    """Placeholder service - returns not implemented message."""
    
    def __init__(self, session_id: Optional[str] = None, intent_name: Optional[str] = None):
        super().__init__(session_id=session_id, intent_name=intent_name)
    
    async def query_data(self, params: BaseQueryParams) -> NotImplementedResponse:
        """No service query for placeholder."""
        if self.logger:
            self.logger.info("Returning not implemented message")
        
        # Extract query from params (handle NotImplementedQueryParams or any BaseQueryParams)
        query_text = getattr(params, 'query', 'unknown query')
        
        return NotImplementedResponse(
            message="Esta funcionalidade ainda não está implementada, mas será adicionada em breve!",
            query=query_text
        )


def create_not_implemented_handler(session_id: Optional[str] = None, intent_name: str = "not_implemented"):
    """
    Factory function to create not implemented handler.
    
    Args:
        session_id: Optional chat session ID for logging
        intent_name: Optional intent name for logging (defaults to "not_implemented")
    """
    return BaseIntentHandler(
        extractor=NotImplementedExtractor(session_id=session_id, intent_name=intent_name),
        service=NotImplementedService(session_id=session_id, intent_name=intent_name),
        session_id=session_id,
        intent_name=intent_name
    )

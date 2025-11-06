"""
Base Intent Package.
Provides abstract base classes for all intent implementations.

This package defines the contract that all intents must follow:
- models.py: Base classes for query parameters and responses
- extractor.py: Base class for parameter extraction from natural language
- service.py: Base class for data querying from external sources
- handler.py: Base class for orchestrating the complete flow

Usage:
    To create a new intent, inherit from these base classes:
    
    # In your_intent/models.py
    from backend.intents.base_intent import BaseQueryParams, BaseResponse
    
    class YourIntentQuery(BaseQueryParams):
        param1: str
        param2: Optional[int]
    
    class YourIntentResponse(BaseResponse):
        result: str
        data: List[Dict]
    
    # In your_intent/extractor.py
    from backend.intents.base_intent import BaseExtractor
    
    class YourIntentExtractor(BaseExtractor):
        EXTRACTION_PROMPT = "..."
        
        async def extract_params(self, query, context):
            # Implementation here
            pass
    
    # In your_intent/service.py
    from backend.intents.base_intent import BaseService
    
    class YourIntentService(BaseService):
        async def query_data(self, params):
            # Implementation here
            pass
    
    # In your_intent/handler.py
    from backend.intents.base_intent import BaseIntentHandler
    
    class YourIntentHandler(BaseIntentHandler):
        def __init__(self):
            super().__init__()
            self.extractor = YourIntentExtractor()
            self.service = YourIntentService()
        
        async def extract_params(self, query, context):
            return await self.extractor.extract_params(query, context)
        
        async def query_service(self, params):
            return await self.service.query_data(params)
"""

from .models import BaseQueryParams, BaseResponse, ErrorResponse
from .extractor import BaseExtractor
from .service import BaseService
from .handler import BaseIntentHandler

__all__ = [
    # Models
    "BaseQueryParams",
    "BaseResponse",
    "ErrorResponse",
    
    # Extractor
    "BaseExtractor",
    
    # Service
    "BaseService",
    
    # Handler
    "BaseIntentHandler",
]

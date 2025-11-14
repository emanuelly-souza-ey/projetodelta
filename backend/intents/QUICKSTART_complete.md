# Intent Creation Quickstart Guide

This guide provides a quick reference for creating new intents in the system.

## Basic Structure

Each intent requires two main files:

```
your_intent/
├── models.py      # Contains your business logic
├── extractor.py      # Contains your business logic
├── service.py      # Contains your business logic
└── __init__.py    # Intent registration and metadata, create a handler here
```

## Step 1: Create Handler (__init__.py)

```python
from typing import Dict, Optional
from backend.intents.base_intent import BaseExtractor, BaseService, BaseIntentHandler

# This belongs to extractor.py
class YourExtractor(BaseExtractor[ModelQuery]):
    EXTRACTION_PROMPT ="""Here goes your prompt for the extractor"""

    async def extract_params(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Extract parameters from user query using llm. Note BaseExtractor has his own self.logger
        Args:
            query: User's input text
            context: Optional conversation context
        Returns:
            Dict with extracted parameters
        """
        ...
        
        # Uses instructor to extract structured parameters
        params = cast(
            <ModelQuery>,
            self.azure_config.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a parameter extraction assistant. Extract information accurately."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_model=<ModelQuery>,
            )
        )
        return params

# This belongs to service.py
class YourService(BaseService[ModelQuery, ModelResponse]):
    def _build_wiql_query(self, params: ModelQuery) -> str:
        """Here goes wiql query to extract data"""

    async def query_data(self, params: ModelQuery) -> ModelResponse:
        """
        Implement your business logic here.
        Args:
            params: Parameters from extractor
        Returns:
            Dict with response data
        """
        ...

        return self._process(<response from queries>)

def create_your_handler(session_id: Optional[str] = None, intent_name: Optional[str] = None):
    """Factory function for intent handler creation."""
    intent_name = ""
    return BaseIntentHandler(
        extractor=YourExtractor(),
        service=YourService(),
        session_id=session_id,
        intent_name=intent_name
    )

```

## Step 2: Register Intent (__init__.py)

```python
from backend.intents.registry import IntentMetadata, register_intent
from .handler import create_your_handler

INTENT_METADATA = IntentMetadata(
    category="your_category",      # Intent category for grouping
    name="Your Intent Name",       # Human-readable name
    description="What your intent does",
    handler_class=create_your_handler,
    agent_name="your_agent_name"   # Agent responsible for this intent
    requires_llm = True  # Whether this intent requires LLM processing (Answer Agent)
)

register_intent(INTENT_METADATA)

__all__ = ["create_your_handler", "INTENT_METADATA"]#handler, query_model, response_model, intent_metadata
```


## Step 3: Create models 
Example

```python
class ModelQuery(BaseQueryParams):
    """Parameters extracted from user query, it is meant to be used by instructor"""
    
    REQUIRES_PROJECT: ClassVar[bool] = True  # This intent requires a selected project
    
    person_name: Optional[str] = Field(
        None,
        description="Name of the person/team member"
    )

#you can also use the already defined model in backend\models
class WorkedHoursResponse(BaseResponse):
    """Structured response for worked hours query, it is meant to be used by fast api, in pydactic"""
    
    person: Optional[str] = Field(None, description="Person name")

```

## Step 4: Create test endpoint (backend\api\v1\endpoints\intent.py)
In the meain root of the proyect search for the router and add a route for the individual intent for testing

## Advanced Features

### Project Requirement
To make your intent require a project context:

```python
from pydantic import BaseModel

class YourParams(BaseModel):
    REQUIRES_PROJECT = True  # This flag enforces project context
    project_id: str
    # other parameters...
```

### Automatic Features

The system automatically handles:
- Error handling and logging
- Conversation context management
- Project validation (if required)
- Session tracking
- Memory management

### Best Practices

1. **Composition over Inheritance**
   - Don't inherit from `BaseIntentHandler`
   - Use the factory pattern with `create_your_handler()`

2. **Parameter Extraction**
   - Keep extractors focused on parsing user input
   - Use Pydantic models for parameter validation

3. **Business Logic**
   - Keep services focused on data operations
   - Handle async operations properly

4. **Error Handling**
   - Let the base handler manage exceptions
   - Return structured error responses

## Example Usage

```python
# The system will automatically:
handler = create_your_handler(
    session_id="user_session_123",
    intent_name="custom_intent"
)

# Handle the request
response = await handler.handle(
    query="user query",
    conversation_id="conv_123"
)
```

The response will include:
- Structured data from your service
- Conversation tracking
- Error handling if needed
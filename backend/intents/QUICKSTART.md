# Intent Creation Quickstart Guide

This guide provides a quick reference for creating new intents in the system.

## Basic Structure

Each intent requires two main files:

```
your_intent/
├── handler.py      # Contains your business logic
└── __init__.py    # Intent registration and metadata
```

## Step 1: Create Handler (handler.py)

```python
from typing import Dict, Optional
from backend.intents.base_intent import BaseExtractor, BaseService, BaseIntentHandler

class YourExtractor(BaseExtractor):
    async def extract_params(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Extract parameters from user query.
        Args:
            query: User's input text
            context: Optional conversation context
        Returns:
            Dict with extracted parameters
        """
        return {
            "param1": "value1",
            # Add your parameter extraction logic
        }

class YourService(BaseService):
    async def query_data(self, params: Dict) -> Dict:
        """
        Implement your business logic here.
        Args:
            params: Parameters from extractor
        Returns:
            Dict with response data
        """
        return {
            "result": "your_data",
            # Add your business logic
        }

def create_your_handler(session_id: Optional[str] = None, intent_name: Optional[str] = None):
    """Factory function for intent handler creation."""
    return BaseIntentHandler(
        extractor=YourExtractor(),
        service=YourService(),
        session_id=session_id,
        intent_name=intent_name or "your_intent"
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
)

register_intent(INTENT_METADATA)

__all__ = ["create_your_handler", "INTENT_METADATA"]
```

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
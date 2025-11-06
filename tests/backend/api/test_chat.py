# -*- coding: utf-8 -*-
"""
Comprehensive tests for Chat API endpoint.
Tests complete conversation flow, error handling, and edge cases.

Run: python -m pytest tests/backend/api/test_chat.py -v
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.api.v1.endpoints.chat import (
    router,
    ChatRequest,
    ChatResponse,
    chat,
    clear_conversation,
    list_conversations
)


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def mock_router_agent():
    """Mock RouterAgent to avoid real Azure OpenAI calls."""
    with patch('backend.api.v1.endpoints.chat.RouterAgent') as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        
        # Default successful routing
        mock_instance.process_query.return_value = {
            "success": True,
            "intent": {
                "category": "worked_hours",
                "confidence": 0.95,
                "reasoning": "User asked about worked hours"
            }
        }
        yield mock_instance


@pytest.fixture
def mock_answer_agent():
    """Mock AnswerAgent to avoid real Azure OpenAI calls."""
    with patch('backend.api.v1.endpoints.chat.AnswerAgent') as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        
        # Default response
        mock_instance.generate_response.return_value = "Você trabalhou 40 horas esta semana."
        yield mock_instance


@pytest.fixture
def mock_handler():
    """Mock intent handler."""
    mock = AsyncMock()
    mock.handle.return_value = {
        "data": {
            "hours": 40,
            "week": "current"
        },
        "conversation_id": "test-conv-123"
    }
    return mock


@pytest.fixture
def mock_get_handler(mock_handler):
    """Mock get_handler factory function."""
    with patch('backend.api.v1.endpoints.chat.get_handler') as mock:
        mock.return_value = mock_handler
        yield mock


@pytest.fixture
def mock_memory():
    """Mock conversation memory."""
    with patch('backend.api.v1.endpoints.chat.get_memory') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # Default context
        mock_instance.get_context.return_value = {
            "last_query": "quantas horas trabalhei?",
            "last_params": {},
            "last_intent": "worked_hours",
            "history": []
        }
        
        # Conversation management
        mock_instance.clear.return_value = True
        mock_instance.get_all_conversations.return_value = ["conv-1", "conv-2"]
        
        yield mock_instance


# ==============================================================================
# TESTS: Successful Chat Flow
# ==============================================================================

@pytest.mark.asyncio
async def test_chat_successful_flow(
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test complete successful chat flow."""
    # Arrange
    request = ChatRequest(
        message="Quantas horas trabalhei esta semana?",
        conversation_id="test-conv-123"
    )
    
    # Act
    response = await chat(request)
    
    # Assert
    assert isinstance(response, ChatResponse)
    assert response.message == "Você trabalhou 40 horas esta semana."
    assert response.intent == "worked_hours"
    assert response.confidence == 0.95
    assert response.data == {"hours": 40, "week": "current"}
    assert response.conversation_id == "test-conv-123"
    assert response.error is None
    
    # Verify agent calls
    mock_router_agent.process_query.assert_called_once_with(
        "Quantas horas trabalhei esta semana?"
    )
    mock_get_handler.assert_called_once_with("worked_hours", session_id="test-conv-123")
    mock_handler.handle.assert_called_once_with(
        query="Quantas horas trabalhei esta semana?",
        conversation_id="test-conv-123"
    )
    mock_answer_agent.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_chat_without_conversation_id(
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test chat without providing conversation_id."""
    # Arrange
    request = ChatRequest(message="Olá!")
    
    # Act
    response = await chat(request)
    
    # Assert
    assert isinstance(response, ChatResponse)
    assert response.conversation_id == "test-conv-123"  # From handler
    
    # Verify session_id defaults to "anonymous"
    mock_get_handler.assert_called_once_with("worked_hours", session_id="anonymous")


@pytest.mark.asyncio
async def test_chat_with_empty_data(
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test chat when handler returns no data."""
    # Arrange
    mock_handler.handle.return_value = {
        "conversation_id": "test-conv-123"
        # No "data" field
    }
    request = ChatRequest(message="test")
    
    # Act
    response = await chat(request)
    
    # Assert
    assert response.data == {}  # Should default to empty dict


@pytest.mark.asyncio
async def test_chat_context_flow(
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test that context is retrieved and passed to answer agent."""
    # Arrange
    request = ChatRequest(
        message="E ontem?",
        conversation_id="test-conv-123"
    )
    
    expected_context = {
        "last_query": "quantas horas trabalhei?",
        "last_params": {},
        "last_intent": "worked_hours",
        "history": []
    }
    mock_memory.get_context.return_value = expected_context
    
    # Act
    response = await chat(request)
    
    # Assert
    mock_memory.get_context.assert_called_once_with("test-conv-123")
    
    # Verify context was passed to answer agent
    call_args = mock_answer_agent.generate_response.call_args
    assert call_args[1]['context'] == expected_context


# ==============================================================================
# TESTS: Different Intent Categories
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.parametrize("intent_category,query", [
    ("worked_hours", "Quantas horas trabalhei?"),
    ("project_progress", "Como está o projeto?"),
    ("delayed_tasks", "Quais tarefas estão atrasadas?"),
    ("project_team", "Quem está no time?"),
    ("daily_activities", "O que fiz hoje?"),
    ("other", "Consulta genérica"),
    ("default", "Pergunta não relacionada ao DevOps"),
])
async def test_chat_different_intents(
    intent_category,
    query,
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test chat with different intent categories."""
    # Arrange
    mock_router_agent.process_query.return_value = {
        "success": True,
        "intent": {
            "category": intent_category,
            "confidence": 0.85,
            "reasoning": "Test"
        }
    }
    request = ChatRequest(message=query)
    
    # Act
    response = await chat(request)
    
    # Assert
    assert response.intent == intent_category
    mock_get_handler.assert_called_once_with(intent_category, session_id="anonymous")


# ==============================================================================
# TESTS: Error Handling
# ==============================================================================

@pytest.mark.asyncio
async def test_chat_router_failure(
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_memory
):
    """Test chat when router fails to classify."""
    # Arrange
    mock_router_agent.process_query.return_value = {
        "success": False,
        "error": "Classification failed"
    }
    request = ChatRequest(message="test")
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await chat(request)
    
    assert exc_info.value.status_code == 500
    assert "Router error" in exc_info.value.detail
    assert "Classification failed" in exc_info.value.detail


@pytest.mark.asyncio
async def test_chat_handler_exception(
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test chat when handler raises exception."""
    # Arrange
    mock_handler.handle.side_effect = ValueError("Invalid parameters")
    request = ChatRequest(message="test")
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await chat(request)
    
    assert exc_info.value.status_code == 500
    assert "Error processing request" in exc_info.value.detail


@pytest.mark.asyncio
async def test_chat_answer_agent_exception(
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test chat when answer agent fails."""
    # Arrange
    mock_answer_agent.generate_response.side_effect = Exception("Azure API error")
    request = ChatRequest(message="test")
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await chat(request)
    
    assert exc_info.value.status_code == 500
    assert "Error processing request" in exc_info.value.detail


@pytest.mark.asyncio
async def test_chat_propagates_http_exception(
    mock_router_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test that HTTPException is propagated correctly."""
    # Arrange
    mock_router_agent.process_query.side_effect = HTTPException(
        status_code=401,
        detail="Unauthorized"
    )
    request = ChatRequest(message="test")
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await chat(request)
    
    # Should propagate the original HTTPException
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized"


# ==============================================================================
# TESTS: Conversation Management
# ==============================================================================

@pytest.mark.asyncio
async def test_clear_conversation_success(mock_memory):
    """Test clearing conversation successfully."""
    # Arrange
    conversation_id = "test-conv-123"
    mock_memory.clear.return_value = True
    
    # Act
    response = await clear_conversation(conversation_id)
    
    # Assert
    assert response == {
        "status": "success",
        "message": "Conversation cleared"
    }
    mock_memory.clear.assert_called_once_with(conversation_id)


@pytest.mark.asyncio
async def test_clear_conversation_not_found(mock_memory):
    """Test clearing non-existent conversation."""
    # Arrange
    conversation_id = "non-existent"
    mock_memory.clear.return_value = False
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await clear_conversation(conversation_id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Conversation not found"


@pytest.mark.asyncio
async def test_list_conversations(mock_memory):
    """Test listing all conversations."""
    # Arrange
    expected_conversations = ["conv-1", "conv-2", "conv-3"]
    mock_memory.get_all_conversations.return_value = expected_conversations
    
    # Act
    response = await list_conversations()
    
    # Assert
    assert response == {
        "conversations": expected_conversations,
        "count": 3
    }
    mock_memory.get_all_conversations.assert_called_once()


@pytest.mark.asyncio
async def test_list_conversations_empty(mock_memory):
    """Test listing conversations when none exist."""
    # Arrange
    mock_memory.get_all_conversations.return_value = []
    
    # Act
    response = await list_conversations()
    
    # Assert
    assert response == {
        "conversations": [],
        "count": 0
    }


# ==============================================================================
# TESTS: Pydantic Models Validation
# ==============================================================================

def test_chat_request_validation():
    """Test ChatRequest model validation."""
    # Valid request
    request = ChatRequest(message="Hello", conversation_id="conv-1")
    assert request.message == "Hello"
    assert request.conversation_id == "conv-1"
    
    # Valid request without conversation_id
    request = ChatRequest(message="Hello")
    assert request.message == "Hello"
    assert request.conversation_id is None
    
    # Invalid - missing message
    with pytest.raises(ValueError):
        ChatRequest(conversation_id="conv-1")


def test_chat_response_validation():
    """Test ChatResponse model validation."""
    # Valid response
    response = ChatResponse(
        message="Test response",
        intent="worked_hours",
        confidence=0.95,
        data={"hours": 40},
        conversation_id="conv-1",
        error=None
    )
    assert response.message == "Test response"
    assert response.intent == "worked_hours"
    assert response.confidence == 0.95
    assert response.data == {"hours": 40}
    assert response.conversation_id == "conv-1"
    assert response.error is None
    
    # Valid response with minimal fields
    response = ChatResponse(
        message="Test",
        intent="other",
        confidence=0.5,
        conversation_id="conv-1"
    )
    assert response.data is None
    assert response.error is None


# ==============================================================================
# TESTS: Session ID Propagation
# ==============================================================================

@pytest.mark.asyncio
async def test_session_id_propagation(
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test that session_id is correctly propagated through all components."""
    # Arrange
    with patch('backend.api.v1.endpoints.chat.RouterAgent') as MockRouter, \
         patch('backend.api.v1.endpoints.chat.AnswerAgent') as MockAnswer:
        
        mock_router_instance = Mock()
        mock_router_instance.process_query.return_value = {
            "success": True,
            "intent": {"category": "worked_hours", "confidence": 0.9, "reasoning": "test"}
        }
        MockRouter.return_value = mock_router_instance
        
        mock_answer_instance = Mock()
        mock_answer_instance.generate_response.return_value = "Response"
        MockAnswer.return_value = mock_answer_instance
        
        request = ChatRequest(
            message="test",
            conversation_id="my-session-123"
        )
        
        # Act
        await chat(request)
        
        # Assert - RouterAgent initialized with session_id
        MockRouter.assert_called_once_with(session_id="my-session-123")
        
        # Assert - AnswerAgent initialized with session_id
        MockAnswer.assert_called_once_with(session_id="my-session-123")
        
        # Assert - Handler created with session_id
        mock_get_handler.assert_called_once_with("worked_hours", session_id="my-session-123")


# ==============================================================================
# TESTS: Edge Cases
# ==============================================================================

@pytest.mark.asyncio
async def test_chat_with_very_long_message(
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test chat with very long message."""
    # Arrange
    long_message = "A" * 10000  # 10k characters
    request = ChatRequest(message=long_message)
    
    # Act
    response = await chat(request)
    
    # Assert
    assert isinstance(response, ChatResponse)
    mock_router_agent.process_query.assert_called_once_with(long_message)


@pytest.mark.asyncio
async def test_chat_with_special_characters(
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test chat with special characters and emojis."""
    # Arrange
    special_message = "Olá! 😊 Como está o projeto? @#$%^&*()"
    request = ChatRequest(message=special_message)
    
    # Act
    response = await chat(request)
    
    # Assert
    assert isinstance(response, ChatResponse)
    mock_router_agent.process_query.assert_called_once_with(special_message)


@pytest.mark.asyncio
async def test_chat_confidence_edge_values(
    mock_router_agent,
    mock_answer_agent,
    mock_get_handler,
    mock_handler,
    mock_memory
):
    """Test chat with confidence at edge values (0.0 and 1.0)."""
    # Test with 0.0 confidence
    mock_router_agent.process_query.return_value = {
        "success": True,
        "intent": {
            "category": "other",
            "confidence": 0.0,
            "reasoning": "Uncertain"
        }
    }
    request = ChatRequest(message="unclear query")
    
    response = await chat(request)
    assert response.confidence == 0.0
    
    # Test with 1.0 confidence
    mock_router_agent.process_query.return_value = {
        "success": True,
        "intent": {
            "category": "worked_hours",
            "confidence": 1.0,
            "reasoning": "Very clear"
        }
    }
    request = ChatRequest(message="clear query")
    
    response = await chat(request)
    assert response.confidence == 1.0


# ==============================================================================
# TESTS: Integration with FastAPI TestClient (Optional)
# ==============================================================================

def test_router_includes_endpoints():
    """Test that router has all expected endpoints."""
    route_paths = [route.path for route in router.routes]
    
    assert "/chat" in route_paths
    assert "/conversation/{conversation_id}" in route_paths
    assert "/conversations" in route_paths


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

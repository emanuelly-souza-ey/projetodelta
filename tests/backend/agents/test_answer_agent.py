# -*- coding: utf-8 -*-
"""
Comprehensive tests for AnswerAgent.
Tests natural language response generation in Portuguese.

Run: python -m pytest tests/backend/agents/test_answer_agent.py -v
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import backend.intents first to resolve circular imports
import backend.intents

from backend.agents.answer_agent import AnswerAgent, AnswerResponse


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def mock_azure_config():
    """Mock Azure configuration to avoid real API calls."""
    with patch('backend.agents.answer_agent.get_azure_config') as mock_config:
        mock_instance = Mock()
        mock_config.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_answer_response():
    """Sample AnswerResponse for testing."""
    return AnswerResponse(
        answer="Juan trabalhou 40 horas esta semana no projeto Delta.",
        confidence=0.95
    )


@pytest.fixture
def answer_agent(mock_azure_config):
    """Create AnswerAgent instance with mocked config."""
    return AnswerAgent(session_id="test-session-456")


@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return {
        "user": "Juan",
        "hours": 40,
        "week": "2025-W01",
        "project": "Delta"
    }


# ==============================================================================
# INITIALIZATION TESTS
# ==============================================================================

class TestAnswerAgentInitialization:
    """Test AnswerAgent initialization and setup."""
    
    def test_init_without_session_id(self, mock_azure_config):
        """Test AnswerAgent can be initialized without session_id."""
        agent = AnswerAgent()
        assert agent.session_id is None
        assert agent.azure_config is not None
    
    def test_init_with_session_id(self, mock_azure_config):
        """Test AnswerAgent initializes with session_id."""
        agent = AnswerAgent(session_id="test-456")
        assert agent.session_id == "test-456"
        assert agent.azure_config is not None
    
    def test_uses_shared_azure_config(self, mock_azure_config):
        """Test that AnswerAgent uses shared Azure config singleton."""
        agent1 = AnswerAgent()
        agent2 = AnswerAgent()
        # Both should use the same config instance
        assert agent1.azure_config is agent2.azure_config
    
    def test_has_system_prompt(self):
        """Test that AnswerAgent has a system prompt defined."""
        assert hasattr(AnswerAgent, 'SYSTEM_PROMPT')
        assert "português brasileiro" in AnswerAgent.SYSTEM_PROMPT.lower()


# ==============================================================================
# GENERATE RESPONSE TESTS
# ==============================================================================

class TestGenerateResponse:
    """Test response generation functionality."""
    
    def test_generate_response_success(self, answer_agent, mock_azure_config, sample_answer_response, sample_data):
        """Test successful response generation."""
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        result = answer_agent.generate_response(
            query="¿Cuántas horas trabajó Juan?",
            intent="worked_hours",
            data=sample_data
        )
        
        # Verify result is a string
        assert isinstance(result, str)
        assert len(result) > 0
        assert result == sample_answer_response.answer
        
        # Verify Azure config was called
        mock_azure_config.create_chat_completion.assert_called_once()
        call_args = mock_azure_config.create_chat_completion.call_args
        assert call_args.kwargs['response_model'] == AnswerResponse
        assert call_args.kwargs['temperature'] == 0.7
        assert call_args.kwargs['max_tokens'] == 800
    
    def test_generate_response_includes_query_in_prompt(self, answer_agent, mock_azure_config, sample_answer_response, sample_data):
        """Test that the prompt includes the user query."""
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        query = "¿Cuántas horas trabajó Juan esta semana?"
        answer_agent.generate_response(query, "worked_hours", sample_data)
        
        # Get the prompt from the call
        call_args = mock_azure_config.create_chat_completion.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[1]['content']
        
        assert query in user_message
    
    def test_generate_response_includes_intent(self, answer_agent, mock_azure_config, sample_answer_response, sample_data):
        """Test that the prompt includes the intent."""
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        intent = "worked_hours"
        answer_agent.generate_response("test query", intent, sample_data)
        
        # Get the prompt from the call
        call_args = mock_azure_config.create_chat_completion.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[1]['content']
        
        assert intent in user_message
    
    def test_generate_response_includes_data(self, answer_agent, mock_azure_config, sample_answer_response, sample_data):
        """Test that the prompt includes the data."""
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        answer_agent.generate_response("test query", "worked_hours", sample_data)
        
        # Get the prompt from the call
        call_args = mock_azure_config.create_chat_completion.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[1]['content']
        
        # Should contain formatted data
        assert "Juan" in user_message
        assert "40" in user_message
    
    def test_generate_response_with_context(self, answer_agent, mock_azure_config, sample_answer_response, sample_data):
        """Test response generation with conversation context."""
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        context = {
            "last_query": "¿Qué proyectos tiene Juan?",
            "conversation_id": "conv-123"
        }
        
        answer_agent.generate_response("Y cuántas horas?", "worked_hours", sample_data, context)
        
        # Get the prompt from the call
        call_args = mock_azure_config.create_chat_completion.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[1]['content']
        
        # Should contain context
        assert context["last_query"] in user_message
    
    def test_generate_response_without_context(self, answer_agent, mock_azure_config, sample_answer_response, sample_data):
        """Test response generation without context."""
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        result = answer_agent.generate_response("test query", "worked_hours", sample_data)
        
        assert isinstance(result, str)
        mock_azure_config.create_chat_completion.assert_called_once()
    
    def test_generate_response_handles_error(self, answer_agent, mock_azure_config, sample_data):
        """Test error handling when generation fails."""
        mock_azure_config.create_chat_completion.side_effect = Exception("API Error")
        
        result = answer_agent.generate_response("test query", "worked_hours", sample_data)
        
        # Should return error message in Portuguese
        assert isinstance(result, str)
        assert "Desculpe" in result
        assert "API Error" in result
    
    def test_generate_response_uses_system_prompt(self, answer_agent, mock_azure_config, sample_answer_response, sample_data):
        """Test that system prompt is used in messages."""
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        answer_agent.generate_response("test query", "worked_hours", sample_data)
        
        # Get messages from the call
        call_args = mock_azure_config.create_chat_completion.call_args
        messages = call_args.kwargs['messages']
        
        # First message should be system prompt
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == AnswerAgent.SYSTEM_PROMPT


# ==============================================================================
# FORMAT DATA TESTS
# ==============================================================================

class TestFormatData:
    """Test data formatting functionality."""
    
    def test_format_data_simple_dict(self, answer_agent):
        """Test formatting simple dictionary."""
        data = {"user": "Juan", "hours": 40}
        result = answer_agent._format_data(data)
        
        assert isinstance(result, str)
        assert "user: Juan" in result
        assert "hours: 40" in result
    
    def test_format_data_empty_dict(self, answer_agent):
        """Test formatting empty dictionary."""
        result = answer_agent._format_data({})
        
        assert result == "Nenhum dado disponível"
    
    def test_format_data_none(self, answer_agent):
        """Test formatting None."""
        result = answer_agent._format_data(None)
        
        assert result == "Nenhum dado disponível"
    
    def test_format_data_with_list(self, answer_agent):
        """Test formatting data with list values."""
        data = {
            "user": "Juan",
            "tasks": ["Task 1", "Task 2", "Task 3"]
        }
        result = answer_agent._format_data(data)
        
        assert "user: Juan" in result
        assert "tasks: 3" in result  # Shows count, not full list
    
    def test_format_data_with_nested_dict(self, answer_agent):
        """Test formatting data with nested dictionary."""
        data = {
            "user": "Juan",
            "details": {"age": 30, "role": "Developer"}
        }
        result = answer_agent._format_data(data)
        
        assert "user: Juan" in result
        assert "details: objeto complexo" in result
    
    def test_format_data_mixed_types(self, answer_agent):
        """Test formatting data with mixed types."""
        data = {
            "string": "value",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "bool": True,
            "float": 3.14
        }
        result = answer_agent._format_data(data)
        
        assert "string: value" in result
        assert "number: 42" in result
        assert "list: 3" in result
        assert "dict: objeto complexo" in result
        assert "bool: True" in result
        assert "float: 3.14" in result


# ==============================================================================
# INTEGRATION TESTS
# ==============================================================================

class TestAnswerAgentIntegration:
    """Integration tests with different data types."""
    
    def test_generate_response_different_intents(self, answer_agent, mock_azure_config):
        """Test generating responses for different intent types."""
        test_cases = [
            ("worked_hours", {"hours": 40}, "Horas trabajadas"),
            ("project_progress", {"progress": "75%"}, "Progreso del proyecto"),
            ("delayed_tasks", {"count": 5}, "Tareas atrasadas"),
            ("other", {"result": "Success"}, "Consulta general")
        ]
        
        for intent, data, query in test_cases:
            mock_response = AnswerResponse(
                answer=f"Respuesta para {intent}",
                confidence=0.9
            )
            mock_azure_config.create_chat_completion.return_value = mock_response
            
            result = answer_agent.generate_response(query, intent, data)
            
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_generate_response_empty_data(self, answer_agent, mock_azure_config):
        """Test generating response with empty data."""
        mock_response = AnswerResponse(
            answer="Não há dados disponíveis para esta consulta.",
            confidence=0.5
        )
        mock_azure_config.create_chat_completion.return_value = mock_response
        
        result = answer_agent.generate_response("test query", "worked_hours", {})
        
        assert isinstance(result, str)
        # Prompt should contain "Nenhum dado disponível"
        call_args = mock_azure_config.create_chat_completion.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[1]['content']
        assert "Nenhum dado disponível" in user_message


# ==============================================================================
# EDGE CASES
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_large_data(self, answer_agent, mock_azure_config, sample_answer_response):
        """Test handling very large data dictionaries."""
        large_data = {f"key_{i}": f"value_{i}" for i in range(100)}
        
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        result = answer_agent.generate_response("test query", "worked_hours", large_data)
        
        assert isinstance(result, str)
    
    def test_special_characters_in_data(self, answer_agent, mock_azure_config, sample_answer_response):
        """Test handling special characters in data."""
        data = {
            "user": "João José ñáéíóú",
            "comment": "Test @#$%^&*()"
        }
        
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        result = answer_agent.generate_response("test query", "worked_hours", data)
        
        assert isinstance(result, str)
    
    def test_unicode_in_query(self, answer_agent, mock_azure_config, sample_answer_response):
        """Test handling unicode characters in query."""
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        query = "¿Cuántas horas trabajó João José? 中文 🎉"
        result = answer_agent.generate_response(query, "worked_hours", {})
        
        assert isinstance(result, str)
    
    def test_none_context(self, answer_agent, mock_azure_config, sample_answer_response):
        """Test with None context."""
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        result = answer_agent.generate_response("test query", "worked_hours", {}, context=None)
        
        assert isinstance(result, str)
    
    def test_empty_context(self, answer_agent, mock_azure_config, sample_answer_response):
        """Test with empty context dictionary."""
        mock_azure_config.create_chat_completion.return_value = sample_answer_response
        
        result = answer_agent.generate_response("test query", "worked_hours", {}, context={})
        
        assert isinstance(result, str)


# ==============================================================================
# ANSWER RESPONSE MODEL TESTS
# ==============================================================================

class TestAnswerResponseModel:
    """Test AnswerResponse Pydantic model."""
    
    def test_create_valid_answer_response(self):
        """Test creating valid AnswerResponse."""
        response = AnswerResponse(
            answer="Test answer",
            confidence=0.8
        )
        
        assert response.answer == "Test answer"
        assert response.confidence == 0.8
    
    def test_confidence_validation_min(self):
        """Test confidence minimum validation."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            AnswerResponse(answer="Test", confidence=-0.1)
    
    def test_confidence_validation_max(self):
        """Test confidence maximum validation."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            AnswerResponse(answer="Test", confidence=1.1)
    
    def test_confidence_edge_cases(self):
        """Test confidence at boundaries."""
        # Minimum boundary
        response_min = AnswerResponse(answer="Test", confidence=0.0)
        assert response_min.confidence == 0.0
        
        # Maximum boundary
        response_max = AnswerResponse(answer="Test", confidence=1.0)
        assert response_max.confidence == 1.0


# ==============================================================================
# RUN TESTS (for standalone execution)
# ==============================================================================

def run_all_tests():
    """Run all tests and print summary."""
    print("\n" + "="*80)
    print("🧪 RUNNING: AnswerAgent Tests")
    print("="*80 + "\n")
    
    # Run pytest
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "-ra",
        "--color=yes"
    ]
    
    exit_code = pytest.main(pytest_args)
    
    print("\n" + "="*80)
    if exit_code == 0:
        print("✅ ALL ANSWER AGENT TESTS PASSED")
    else:
        print("❌ SOME ANSWER AGENT TESTS FAILED")
    print("="*80 + "\n")
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

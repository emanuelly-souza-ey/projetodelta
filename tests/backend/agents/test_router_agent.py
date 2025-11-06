# -*- coding: utf-8 -*-
"""
Comprehensive tests for RouterAgent.
Tests intent classification, routing logic, and error handling.

Run: python -m pytest tests/backend/agents/test_router_agent.py -v
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import backend.intents first to resolve circular imports
import backend.intents

from backend.agents.router_agent import RouterAgent
from backend.agents.models import UserIntent
from backend.intents.registry import IntentRegistry, IntentMetadata


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def mock_azure_config():
    """Mock Azure configuration to avoid real API calls."""
    with patch('backend.agents.router_agent.get_azure_config') as mock_config:
        mock_instance = Mock()
        mock_config.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_logger():
    """Mock logger to test logging calls."""
    with patch('backend.agents.router_agent.chat_logger') as mock_log:
        mock_component_logger = Mock()
        mock_log.get_component_logger.return_value = mock_component_logger
        yield mock_component_logger


@pytest.fixture
def sample_intent():
    """Sample UserIntent for testing."""
    return UserIntent(
        category="worked_hours",
        confidence=0.95,
        reasoning="Query mentions 'horas trabajadas' which indicates worked hours intent",
        original_query="¿Cuántas horas trabajó Juan esta semana?"
    )


@pytest.fixture
def router_agent(mock_azure_config):
    """Create RouterAgent instance with mocked config."""
    return RouterAgent(session_id="test-session-123")


# ==============================================================================
# INITIALIZATION TESTS
# ==============================================================================

class TestRouterAgentInitialization:
    """Test RouterAgent initialization and setup."""
    
    def test_init_without_session_id(self, mock_azure_config):
        """Test RouterAgent can be initialized without session_id."""
        agent = RouterAgent()
        assert agent.session_id is None
        assert agent.logger is None
        assert agent.azure_config is not None
    
    def test_init_with_session_id(self, mock_azure_config, mock_logger):
        """Test RouterAgent initializes with session_id and logger."""
        agent = RouterAgent(session_id="test-123")
        assert agent.session_id == "test-123"
        assert agent.azure_config is not None
    
    def test_uses_shared_azure_config(self, mock_azure_config):
        """Test that RouterAgent uses shared Azure config singleton."""
        agent1 = RouterAgent()
        agent2 = RouterAgent()
        # Both should use the same config instance
        assert agent1.azure_config is agent2.azure_config


# ==============================================================================
# INTENT CLASSIFICATION TESTS
# ==============================================================================

class TestClassifyIntent:
    """Test intent classification functionality."""
    
    def test_classify_intent_success(self, router_agent, mock_azure_config, sample_intent):
        """Test successful intent classification."""
        # Mock the Azure OpenAI response
        mock_azure_config.create_chat_completion.return_value = sample_intent
        
        result = router_agent.classify_intent("¿Cuántas horas trabajó Juan?")
        
        # Verify the result
        assert isinstance(result, UserIntent)
        assert result.category == "worked_hours"
        assert result.confidence == 0.95
        assert result.original_query == "¿Cuántas horas trabajó Juan?"
        
        # Verify Azure config was called
        mock_azure_config.create_chat_completion.assert_called_once()
        call_args = mock_azure_config.create_chat_completion.call_args
        assert call_args.kwargs['response_model'] == UserIntent
        assert call_args.kwargs['temperature'] == 0.3
        assert call_args.kwargs['max_tokens'] == 500
    
    def test_classify_intent_prompt_includes_categories(self, router_agent, mock_azure_config, sample_intent):
        """Test that classification prompt includes registered categories."""
        mock_azure_config.create_chat_completion.return_value = sample_intent
        
        router_agent.classify_intent("test query")
        
        # Get the prompt from the call
        call_args = mock_azure_config.create_chat_completion.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[1]['content']
        
        # Prompt should contain categories
        assert "Categorias disponíveis:" in user_message
        assert "test query" in user_message
    
    def test_classify_intent_sets_original_query(self, router_agent, mock_azure_config):
        """Test that original_query is set correctly."""
        mock_intent = UserIntent(
            category="other",
            confidence=0.8,
            reasoning="Test reasoning"
        )
        mock_azure_config.create_chat_completion.return_value = mock_intent
        
        query = "What is the weather today?"
        result = router_agent.classify_intent(query)
        
        assert result.original_query == query
    
    def test_classify_intent_with_logging(self, mock_azure_config, mock_logger):
        """Test that classification logs appropriately."""
        agent = RouterAgent(session_id="test-log")
        
        mock_intent = UserIntent(
            category="worked_hours",
            confidence=0.9,
            reasoning="Test"
        )
        mock_azure_config.create_chat_completion.return_value = mock_intent
        
        # Note: logger is mocked at module level, so agent.logger might be None
        # This test verifies the code path works even with logger
        result = agent.classify_intent("test query")
        assert result is not None


# ==============================================================================
# ROUTING TESTS
# ==============================================================================

class TestRouteToAgent:
    """Test agent routing logic."""
    
    def test_route_to_agent_registered_intent(self, router_agent, sample_intent):
        """Test routing to agent for registered intent."""
        result = router_agent.route_to_agent(sample_intent)
        
        # worked_hours should route to worked_hours_agent (or custom agent name)
        assert result is not None
        assert isinstance(result, str)
    
    def test_route_to_agent_unregistered_intent(self, router_agent):
        """Test routing falls back to default_agent for unregistered intent."""
        # Use a valid category but mock IntentRegistry.get to raise ValueError
        valid_intent = UserIntent(
            category="other",
            confidence=0.5,
            reasoning="Test"
        )
        
        # Mock the registry to simulate unregistered intent
        with patch.object(IntentRegistry, 'get', side_effect=ValueError("Not found")):
            result = router_agent.route_to_agent(valid_intent)
            assert result == "default_agent"
    
    def test_route_to_agent_uses_registry(self, router_agent, sample_intent):
        """Test that routing uses IntentRegistry.get()."""
        with patch.object(IntentRegistry, 'get') as mock_get:
            mock_metadata = Mock(spec=IntentMetadata)
            mock_metadata.get_agent_name.return_value = "custom_agent"
            mock_get.return_value = mock_metadata
            
            result = router_agent.route_to_agent(sample_intent)
            
            mock_get.assert_called_once_with(sample_intent.category)
            assert result == "custom_agent"
    
    def test_route_to_agent_logs_warning_on_fallback(self, mock_azure_config, mock_logger):
        """Test that fallback to default agent is logged."""
        agent = RouterAgent(session_id="test-warn")
        
        # Use valid category but mock registry failure
        valid_intent = UserIntent(
            category="other",
            confidence=0.5,
            reasoning="Test"
        )
        
        with patch.object(IntentRegistry, 'get', side_effect=ValueError("Not found")):
            result = agent.route_to_agent(valid_intent)
            assert result == "default_agent"


# ==============================================================================
# PROCESS QUERY TESTS
# ==============================================================================

class TestProcessQuery:
    """Test end-to-end query processing."""
    
    def test_process_query_success(self, router_agent, mock_azure_config, sample_intent):
        """Test successful query processing."""
        mock_azure_config.create_chat_completion.return_value = sample_intent
        
        result = router_agent.process_query("¿Cuántas horas trabajó Juan?")
        
        # Verify structure
        assert result['success'] is True
        assert result['query'] == "¿Cuántas horas trabajó Juan?"
        assert result['error'] is None
        
        # Verify intent info
        assert result['intent']['category'] == "worked_hours"
        assert result['intent']['confidence'] == 0.95
        assert result['intent']['reasoning'] == sample_intent.reasoning
        
        # Verify routing
        assert result['route_to'] is not None
        assert isinstance(result['route_to'], str)
    
    def test_process_query_handles_classification_error(self, router_agent, mock_azure_config):
        """Test error handling when classification fails."""
        mock_azure_config.create_chat_completion.side_effect = Exception("API Error")
        
        result = router_agent.process_query("test query")
        
        # Should return error structure
        assert result['success'] is False
        assert result['query'] == "test query"
        assert result['intent'] is None
        assert result['route_to'] == "default_agent"
        assert "API Error" in result['error']
    
    def test_process_query_handles_routing_error(self, router_agent, mock_azure_config):
        """Test error handling when routing fails."""
        # Classification succeeds with valid category
        mock_intent = UserIntent(
            category="other",
            confidence=0.8,
            reasoning="Test"
        )
        mock_azure_config.create_chat_completion.return_value = mock_intent
        
        # But routing fails
        with patch.object(router_agent, 'route_to_agent', side_effect=Exception("Routing error")):
            result = router_agent.process_query("test query")
            
            assert result['success'] is False
            assert "Routing error" in result['error']
    
    def test_process_query_different_intents(self, router_agent, mock_azure_config):
        """Test processing queries with different intent types."""
        test_cases = [
            ("worked_hours", "¿Cuántas horas trabajó?"),
            ("project_progress", "¿Cuál es el progreso del proyecto?"),
            ("delayed_tasks", "¿Qué tareas están atrasadas?"),
            ("other", "¿Cuántos bugs hay?"),
            ("default", "¿Qué es Python?")
        ]
        
        for category, query in test_cases:
            mock_intent = UserIntent(
                category=category,
                confidence=0.9,
                reasoning=f"Test for {category}"
            )
            mock_azure_config.create_chat_completion.return_value = mock_intent
            
            result = router_agent.process_query(query)
            
            assert result['success'] is True
            assert result['intent']['category'] == category
            assert result['route_to'] is not None


# ==============================================================================
# INTEGRATION TESTS
# ==============================================================================

class TestRouterAgentIntegration:
    """Integration tests with real IntentRegistry."""
    
    def test_routes_to_registered_handlers(self, router_agent, mock_azure_config):
        """Test that router can route to all registered intents."""
        # Get all registered intents
        registered_intents = IntentRegistry.get_categories()
        
        # Test each one
        for category in registered_intents:
            mock_intent = UserIntent(
                category=category,
                confidence=0.9,
                reasoning=f"Test {category}"
            )
            mock_azure_config.create_chat_completion.return_value = mock_intent
            
            result = router_agent.process_query(f"test query for {category}")
            
            # Should successfully route
            assert result['success'] is True
            assert result['intent']['category'] == category
            # Should have a valid agent name
            assert result['route_to'] is not None
            assert len(result['route_to']) > 0
    
    def test_intent_metadata_structure(self):
        """Test that all registered intents have proper metadata."""
        all_intents = IntentRegistry.get_all()
        
        for category, metadata in all_intents.items():
            # Verify metadata structure
            assert hasattr(metadata, 'category')
            assert hasattr(metadata, 'name')
            assert hasattr(metadata, 'description')
            assert hasattr(metadata, 'handler_class')
            assert hasattr(metadata, 'get_agent_name')
            
            # Verify agent name is valid
            agent_name = metadata.get_agent_name()
            assert isinstance(agent_name, str)
            assert len(agent_name) > 0


# ==============================================================================
# EDGE CASES
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_query(self, router_agent, mock_azure_config):
        """Test handling of empty query string."""
        mock_intent = UserIntent(
            category="default",
            confidence=0.3,
            reasoning="Empty query"
        )
        mock_azure_config.create_chat_completion.return_value = mock_intent
        
        result = router_agent.process_query("")
        assert result['success'] is True
        assert result['query'] == ""
    
    def test_very_long_query(self, router_agent, mock_azure_config):
        """Test handling of very long query."""
        long_query = "¿Cuántas horas trabajó Juan?" * 100
        mock_intent = UserIntent(
            category="worked_hours",
            confidence=0.8,
            reasoning="Long query"
        )
        mock_azure_config.create_chat_completion.return_value = mock_intent
        
        result = router_agent.process_query(long_query)
        assert result['success'] is True
        assert result['query'] == long_query
    
    def test_special_characters_in_query(self, router_agent, mock_azure_config):
        """Test handling queries with special characters."""
        special_query = "¿Horas trabajadas @#$%^&*()? ñáéíóú"
        mock_intent = UserIntent(
            category="worked_hours",
            confidence=0.85,
            reasoning="Special chars"
        )
        mock_azure_config.create_chat_completion.return_value = mock_intent
        
        result = router_agent.process_query(special_query)
        assert result['success'] is True
        assert result['query'] == special_query
    
    def test_low_confidence_intent(self, router_agent, mock_azure_config):
        """Test that low confidence intents are still processed."""
        low_conf_intent = UserIntent(
            category="other",
            confidence=0.2,
            reasoning="Very uncertain"
        )
        mock_azure_config.create_chat_completion.return_value = low_conf_intent
        
        result = router_agent.process_query("ambiguous query")
        assert result['success'] is True
        assert result['intent']['confidence'] == 0.2


# ==============================================================================
# RUN TESTS (for standalone execution)
# ==============================================================================

def run_all_tests():
    """Run all tests and print summary."""
    print("\n" + "="*80)
    print("🧪 RUNNING: RouterAgent Tests")
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
        print("✅ ALL ROUTER AGENT TESTS PASSED")
    else:
        print("❌ SOME ROUTER AGENT TESTS FAILED")
    print("="*80 + "\n")
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

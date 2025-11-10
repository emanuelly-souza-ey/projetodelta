"""
Tests for intent examples system.
"""

import pytest
from backend.intents.intent_examples import IntentExamplesRegistry, ExamplePrompt, register_examples


class TestIntentExamplesRegistry:
    """Tests for IntentExamplesRegistry."""
    
    def setup_method(self):
        """Reset registry before each test."""
        IntentExamplesRegistry._examples = {}
    
    def test_register_examples(self):
        """Test registering examples for a category."""
        examples = ["Example 1", "Example 2"]
        register_examples("test_category", examples)
        
        assert "test_category" in IntentExamplesRegistry._examples
        assert IntentExamplesRegistry._examples["test_category"] == examples
    
    def test_get_category_examples(self):
        """Test getting examples for a specific category."""
        examples = ["Test prompt 1", "Test prompt 2"]
        register_examples("test_intent", examples)
        
        result = IntentExamplesRegistry.get("test_intent")
        assert result == examples
        
        # Test non-existent category
        empty_result = IntentExamplesRegistry.get("non_existent")
        assert empty_result == []
    
    def test_get_all_examples(self):
        """Test getting all examples."""
        register_examples("intent1", ["Prompt 1", "Prompt 2"])
        register_examples("intent2", ["Prompt 3"])
        
        all_examples = IntentExamplesRegistry.get_all()
        
        assert len(all_examples) == 3
        assert all(isinstance(ex, ExamplePrompt) for ex in all_examples)
        
        categories = [ex.category for ex in all_examples]
        assert "intent1" in categories
        assert "intent2" in categories
    
    def test_get_all_filtered_by_category(self):
        """Test getting examples filtered by category."""
        register_examples("intent1", ["Prompt 1", "Prompt 2"])
        register_examples("intent2", ["Prompt 3"])
        
        filtered = IntentExamplesRegistry.get_all("intent1")
        
        assert len(filtered) == 2
        assert all(ex.category == "intent1" for ex in filtered)
        assert filtered[0].prompt == "Prompt 1"
        assert filtered[1].prompt == "Prompt 2"
    
    def test_get_categories(self):
        """Test getting list of categories."""
        register_examples("category1", ["Prompt 1"])
        register_examples("category2", ["Prompt 2"])
        
        categories = IntentExamplesRegistry.get_categories()
        
        assert "category1" in categories
        assert "category2" in categories
        assert len(categories) == 2


class TestExamplePrompt:
    """Tests for ExamplePrompt model."""
    
    def test_example_prompt_creation(self):
        """Test creating ExamplePrompt."""
        prompt = ExamplePrompt(
            category="test_intent",
            prompt="Test prompt text"
        )
        
        assert prompt.category == "test_intent"
        assert prompt.prompt == "Test prompt text"
        assert prompt.expected_confidence is None
    
    def test_example_prompt_with_confidence(self):
        """Test creating ExamplePrompt with confidence."""
        prompt = ExamplePrompt(
            category="test_intent",
            prompt="Test prompt",
            expected_confidence=0.95
        )
        
        assert prompt.expected_confidence == 0.95


def test_real_intents_have_examples():
    """Integration test that real intents register their examples."""
    import importlib
    import sys
    
    # Reset registry for clean test
    IntentExamplesRegistry._examples = {}
    
    # Force reload modules if already cached to trigger registration
    modules_to_reload = [
        "backend.intents.worked_hours.examples",
        "backend.intents.project_selection.examples", 
        "backend.intents.project_search.examples"
    ]
    
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)
    
    categories = IntentExamplesRegistry.get_categories()
    
    # Check that our implemented intents have examples
    assert "worked_hours" in categories
    assert "project_selection" in categories  
    assert "project_search" in categories
    
    # Check example counts
    worked_examples = IntentExamplesRegistry.get("worked_hours")
    assert len(worked_examples) == 5
    
    selection_examples = IntentExamplesRegistry.get("project_selection")
    assert len(selection_examples) == 5
    
    search_examples = IntentExamplesRegistry.get("project_search")
    assert len(search_examples) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
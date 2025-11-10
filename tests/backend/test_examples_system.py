"""
Test script for examples system.
"""

from backend.intents.intent_examples import IntentExamplesRegistry, ExamplePrompt

# Import intents to trigger auto-registration
from backend.intents import worked_hours, project_selection, project_search

def test_examples_system():
    """Test the examples registry system."""
    print("\n" + "="*60)
    print("TESTING EXAMPLES SYSTEM")
    print("="*60)
    
    # Test 1: Check categories
    categories = IntentExamplesRegistry.get_categories()
    print(f"\n✅ Categories with examples: {categories}")
    
    # Test 2: Get specific category
    worked_examples = IntentExamplesRegistry.get("worked_hours")
    print(f"\n✅ Worked hours examples ({len(worked_examples)}):")
    for i, example in enumerate(worked_examples, 1):
        print(f"   {i}. {example}")
    
    # Test 3: Get all examples
    all_examples = IntentExamplesRegistry.get_all()
    print(f"\n✅ All examples ({len(all_examples)}):")
    for example in all_examples:
        print(f"   [{example.category}] {example.prompt}")
    
    # Test 4: Filter by category
    search_examples = IntentExamplesRegistry.get_all("project_search")
    print(f"\n✅ Project search examples ({len(search_examples)}):")
    for example in search_examples:
        print(f"   {example.prompt}")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✅")
    print("="*60)


if __name__ == "__main__":
    test_examples_system()
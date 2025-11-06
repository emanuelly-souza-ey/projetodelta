"""
Test runner with auto-registration of intent tests.
Discovers test.py files in each intent directory and runs them.

Run: python tests/backend/test_intents.py
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
import importlib

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Initialize backend.intents to resolve circular imports first
import backend.intents  # This completes the circular import chain


def discover_and_load_test_modules() -> None:
    """
    Discover and import all test.py modules in intent directories.
    Registers each test module with the TestRegistry.
    
    Note: backend.intents must be imported first to avoid circular imports.
    """
    from tests.backend.test_registry import register_test_suite
    
    intents_dir = project_root / "backend" / "intents"
    
    print("🔍 Discovering and loading intent test modules...\n")
    
    # Import base_intent first
    try:
        test_module = importlib.import_module("backend.intents.base_intent.test")
        if hasattr(test_module, "run_tests"):
            register_test_suite(
                "base_intent",
                test_module.run_tests,
                "Tests for base abstract components used by all intents"
            )
            print("   ✅ base_intent test module loaded and registered")
        else:
            print("   ⚠️  base_intent: test.py missing run_tests() function")
    except Exception as e:
        print(f"   ❌ base_intent: Error loading test.py - {str(e)}")
    
    # Iterate through intent directories
    for intent_dir in intents_dir.iterdir():
        if not intent_dir.is_dir():
            continue
        
        if intent_dir.name.startswith("__") or intent_dir.name == "base_intent":
            continue
        
        # Check if test.py exists
        test_file = intent_dir / "test.py"
        if test_file.exists():
            intent_name = intent_dir.name
            
            try:
                # Import the test module using importlib (after circular imports resolved)
                module_path = f"backend.intents.{intent_name}.test"
                test_module = importlib.import_module(module_path)
                
                if hasattr(test_module, "run_tests"):
                    # Register the test suite
                    register_test_suite(
                        intent_name,
                        test_module.run_tests,
                        f"Tests for {intent_name} intent"
                    )
                    print(f"   ✅ {intent_name} test module loaded and registered")
                else:
                    print(f"   ⚠️  {intent_name}: test.py missing run_tests() function")
            
            except Exception as e:
                print(f"   ❌ {intent_name}: Error loading test.py - {str(e)}")


async def run_all_tests():
    """Run all registered intent tests using TestRegistry."""
    print("\n" + "="*80)
    print("🧪 INTENT TEST SUITE - Auto-Registration Runner")
    print("="*80 + "\n")
    
    # Discover and load all test modules (triggers registration)
    discover_and_load_test_modules()
    
    # Import registry after modules are loaded
    from tests.backend.test_registry import TestRegistry
    
    # Get all registered test suites
    test_suites = TestRegistry.get_all()
    
    if not test_suites:
        print("\n❌ No test suites registered!\n")
        return
    
    print(f"\n📊 Found {len(test_suites)} registered test suites\n")
    
    # Run each test suite
    all_results = []
    
    for intent_name, suite_info in test_suites.items():
        try:
            print("="*80)
            result = await suite_info.run_tests()
            all_results.append(result)
        except Exception as e:
            print(f"\n❌ Error running {intent_name} tests: {str(e)}")
            all_results.append({
                "intent": intent_name,
                "total_tests": 0,
                "passed": 0,
                "failed": 1,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80 + "\n")
    
    total_tests = sum(r["total_tests"] for r in all_results)
    total_passed = sum(r["passed"] for r in all_results)
    total_failed = sum(r["failed"] for r in all_results)
    
    for result in all_results:
        status_icon = "✅" if result["failed"] == 0 else "❌"
        print(f"{status_icon} {result['intent']:20} - {result['passed']}/{result['total_tests']} passed")
    
    print("\n" + "-"*80)
    print(f"TOTAL: {total_passed}/{total_tests} tests passed")
    
    if total_failed == 0:
        print("="*80)
        print("🎉 ALL TESTS PASSED!")
        print("="*80 + "\n")
    else:
        print("="*80)
        print(f"⚠️  {total_failed} TESTS FAILED")
        print("="*80 + "\n")
    
    print("💡 Tips:")
    print("   - Check logs/ directory for detailed execution logs")
    print("   - Run individual intent tests: python backend/intents/<intent>/test.py")
    print("   - Use grep to search logs: grep 'ERROR' logs/test_*.log")
    print("\n🔧 Adding New Intent Tests:")
    print("   1. Create your intent folder: backend/intents/my_intent/")
    print("   2. Add test.py file with async def run_tests() -> Dict[str, Any]")
    print("   3. Tests auto-register when you run this file - no manual registration needed!")
    print("   4. run_tests() should return: {'intent': name, 'total_tests': n, 'passed': p, 'failed': f, 'results': [...]}\n")


def main():
    """Main entry point."""
    asyncio.run(run_all_tests())


if __name__ == "__main__":
    main()

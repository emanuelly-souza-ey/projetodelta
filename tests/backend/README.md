# Intent Test Auto-Registration System

This document explains the auto-registration system for intent tests, similar to the `IntentRegistry` pattern used for intent handlers.

## Overview

The test system automatically discovers and runs tests for all intents without requiring manual registration in the test runner. When you create a new intent with tests, they are automatically included when running the test suite.

## Architecture

### Components

1. **TestRegistry** (`tests/backend/test_registry.py`)
   - Centralized registry for test suites
   - Stores test metadata (intent name, description, run_tests function)
   - Provides methods to register and retrieve test suites

2. **Test Runner** (`tests/backend/test_intents.py`)
   - Discovers test files in intent directories
   - Loads and registers test modules dynamically
   - Executes all registered tests and reports results

3. **Individual Test Files** (`backend/intents/*/test.py`)
   - Contains test functions for each intent
   - Exports `run_tests()` async function
   - No manual registration code needed

## How It Works

### Auto-Discovery Process

1. Test runner starts and imports `backend.intents` to resolve circular dependencies
2. Scans `backend/intents/` directory for subdirectories
3. For each subdirectory, checks if `test.py` exists
4. Dynamically imports the test module
5. Registers the `run_tests()` function with TestRegistry
6. Executes all registered tests

### Avoiding Circular Imports

The system was designed to avoid circular import issues:
- `backend.intents` module is imported first to complete the import chain
- Test modules are loaded using `importlib` after main modules are initialized
- The `get_intent_descriptions()` import in `router_agent.py` was moved inside the function to break the circular dependency

## Creating Tests for a New Intent

When creating a new intent, follow this pattern:

### 1. Create Test File

Create `backend/intents/your_intent/test.py`:

```python
"""
Tests for your_intent.
"""

import asyncio
from typing import Dict, Any


async def test_your_feature():
    """Test: Description of what you're testing."""
    print("\n🔍 Testing your feature...")
    
    # Your test code here - use lazy imports to avoid circular dependencies
    from . import create_your_handler
    
    handler = create_your_handler(session_id="test_session")
    
    # Assertions
    assert handler is not None, "Handler should not be None"
    
    print("   ✅ Test passed")
    
    return {
        "test_name": "your_feature",
        "status": "passed",
        "message": "Description of result"
    }


# List all test functions
YOUR_INTENT_TESTS = [
    test_your_feature,
    # Add more test functions here
]


async def run_tests() -> Dict[str, Any]:
    """Run all tests for your_intent."""
    print("\n" + "="*80)
    print("🧪 YOUR INTENT - Tests")
    print("="*80)
    
    results = []
    
    for test_func in YOUR_INTENT_TESTS:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            results.append({
                "test_name": test_func.__name__,
                "status": "failed",
                "error": str(e)
            })
            print(f"   ❌ {test_func.__name__} failed: {str(e)}")
    
    return {
        "intent": "your_intent",
        "total_tests": len(results),
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results
    }


# NOTE: Registration happens automatically in test_intents.py
# No manual registration code needed here!


if __name__ == "__main__":
    """Run tests standalone."""
    result = asyncio.run(run_tests())
    
    print("\n" + "="*80)
    print(f"✅ Tests completed: {result['passed']}/{result['total_tests']} passed")
    print("="*80 + "\n")
```

### 2. Test Structure Requirements

Your test file MUST:
- ✅ Export an `async def run_tests() -> Dict[str, Any]` function
- ✅ Return a dictionary with: `intent`, `total_tests`, `passed`, `failed`, `results`
- ✅ Use lazy imports (inside functions) to avoid circular dependencies
- ✅ Include standalone execution support (`if __name__ == "__main__"`)

## Running Tests

### Run all tests
```bash
python tests/backend/test_intents.py
```

### Run individual intent tests
```bash
python backend/intents/your_intent/test.py
```

### Run base component tests
```bash
python backend/intents/base_intent/test.py
```

## Example Output

```
🔍 Discovering and loading intent test modules...

   ✅ base_intent test module loaded and registered
   ✅ worked_hours test module loaded and registered

📊 Found 2 registered test suites

================================================================================
🧪 BASE INTENT - Component Tests
================================================================================

 Testing base_intent components...
   ✅ All base components imported successfully

📝 Testing logging integration...
   ✅ Component loggers created successfully

================================================================================
🧪 WORKED HOURS INTENT - Tests
================================================================================

🔍 Testing worked_hours handler...
   ✅ Handler created successfully
      - Extractor: WorkedHoursExtractor
      - Service: WorkedHoursService

🚀 Testing worked_hours full flow...
   Query: quantas horas trabalhei essa semana?
   ⚠️  Flow returned error (expected if no Azure DevOps setup)

📝 Testing worked_hours logging...
   ✅ Component loggers working

================================================================================
📊 TEST SUMMARY
================================================================================

✅ base_intent          - 2/2 passed
✅ worked_hours         - 3/3 passed

--------------------------------------------------------------------------------
TOTAL: 5/5 tests passed
================================================================================
🎉 ALL TESTS PASSED!
================================================================================
```

## Template for New Intent Tests

Copy this template to `backend/intents/<your_intent>/test.py`:

```python
"""
Tests for <your_intent> intent.
Auto-discovered by the test system.
"""

import asyncio
from typing import Dict, Any


async def test_handler_creation():
    """Test: Verify handler creates correctly."""
    print(f"\n🔍 Testing <your_intent> handler...")
    
    from . import create_<your_intent>_handler
    
    session_id = "test_<your_intent>"
    
    try:
        handler = create_<your_intent>_handler(session_id=session_id)
        
        assert handler is not None, "Handler is None"
        print("   ✅ Handler created successfully")
        
        return {
            "test_name": "handler_creation",
            "status": "passed",
            "message": "Handler initialized correctly"
        }
    
    except Exception as e:
        return {
            "test_name": "handler_creation",
            "status": "failed",
            "error": str(e)
        }


async def test_full_flow():
    """Test: Full flow with test query."""
    print(f"\n🚀 Testing <your_intent> full flow...")
    
    from . import create_<your_intent>_handler
    
    session_id = "test_<your_intent>_flow"
    query = "your test query here"
    
    try:
        handler = create_<your_intent>_handler(session_id=session_id)
        result = await handler.handle(query=query, conversation_id=session_id)
        
        assert result is not None, "Result is None"
        assert "success" in result, "Missing 'success' key"
        
        print("   ✅ Flow completed")
        
        return {
            "test_name": "full_flow",
            "status": "passed",
            "message": "Flow executed successfully"
        }
    
    except Exception as e:
        return {
            "test_name": "full_flow",
            "status": "failed",
            "error": str(e)
        }


# Export test functions
YOUR_INTENT_TESTS = [
    test_handler_creation,
    test_full_flow,
]


async def run_tests() -> Dict[str, Any]:
    """Run all tests for <your_intent>."""
    print("\n" + "="*80)
    print("🧪 YOUR INTENT - Tests")
    print("="*80)
    
    results = []
    
    for test_func in YOUR_INTENT_TESTS:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            results.append({
                "test_name": test_func.__name__,
                "status": "failed",
                "error": str(e)
            })
            print(f"   ❌ {test_func.__name__} failed: {str(e)}")
    
    return {
        "intent": "<your_intent>",
        "total_tests": len(results),
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results
    }


# NOTE: Registration happens automatically in test_intents.py
# No manual registration code needed here!


if __name__ == "__main__":
    """Run tests standalone."""
    result = asyncio.run(run_tests())
    
    print("\n" + "="*80)
    print(f"✅ Tests completed: {result['passed']}/{result['total_tests']} passed")
    print("="*80 + "\n")
```

## Benefits

1. **Zero Configuration**: No need to modify test runner when adding new intents
2. **Consistent Pattern**: Same discovery pattern as IntentRegistry
3. **Type Safety**: TestRegistry provides type checking for test functions
4. **Isolated Tests**: Each intent can run its tests standalone
5. **Easy Debugging**: Clear error messages when tests fail to load
6. **Scalable**: Add unlimited intents without touching centralized code

## Troubleshooting

### Test not discovered?

1. Ensure `test.py` exists in `backend/intents/your_intent/`
2. Verify `run_tests()` function is defined and async
3. Check for syntax errors preventing module load
4. Look for error messages in test runner output

### Circular import errors?

1. Use lazy imports inside test functions
2. Don't import from `backend.intents` at module level in test files
3. Import specific components you need, not the entire module

### Test fails to run?

1. Check that `run_tests()` returns the correct dictionary structure
2. Ensure all test functions handle exceptions properly
3. Verify async/await is used correctly
4. Check logs directory for detailed error information
    """Run all tests for this intent."""
    print("\n" + "="*80)
    print(f"🧪 <TU_INTENT> INTENT - Tests")
    print("="*80)
    
    results = []
    
    for test_func in TU_INTENT_TESTS:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            results.append({
                "test_name": test_func.__name__,
                "status": "failed",
                "error": str(e)
            })
            print(f"   ❌ {test_func.__name__} failed: {str(e)}")
    
    return {
        "intent": "<tu_intent>",
        "total_tests": len(results),
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results
    }


if __name__ == "__main__":
    """Run tests standalone."""
    result = asyncio.run(run_tests())
    
    print("\n" + "="*80)
    print(f"✅ Tests completed: {result['passed']}/{result['total_tests']} passed")
    print("="*80 + "\n")
```

## ✅ Ventajas

1. **Auto-registro**: Como los intents, los tests se registran solos
2. **Modular**: Cada intent mantiene sus propios tests
3. **Ejecutable individual**: Puedes correr tests de un solo intent
4. **Ejecutable global**: O correr todos de una vez
5. **Fácil de extender**: Solo copia el template para nuevos intents
6. **Integrado con logging**: Los tests usan el mismo sistema de logging estructurado

## 🔍 Debugging

Si un test falla:

1. Revisa el output en consola
2. Chequea los logs: `logs/test_<intent>_*.log`
3. Ejecuta el test individual para más detalles
4. Usa grep para buscar errores: `grep "ERROR" logs/test_*.log`

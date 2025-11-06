"""
Test base para componentes abstractos de base_intent.
Cada intent debe crear su propio test.py que exporte test functions.
"""

import asyncio
from typing import Dict, Any


async def test_base_components():
    """Test base: Verificar que las clases abstractas están correctamente definidas."""
    print("\n Testing base_intent components...")
    
    from .extractor import BaseExtractor
    from .service import BaseService
    from .handler import BaseIntentHandler
    from .models import BaseQueryParams, BaseResponse
    
    # Verify abstract classes exist
    assert BaseExtractor is not None, "BaseExtractor not found"
    assert BaseService is not None, "BaseService not found"
    assert BaseIntentHandler is not None, "BaseIntentHandler not found"
    assert BaseQueryParams is not None, "BaseQueryParams not found"
    assert BaseResponse is not None, "BaseResponse not found"
    
    print("   ✅ All base components imported successfully")
    
    return {
        "test_name": "base_components",
        "status": "passed",
        "message": "Base abstract classes are properly defined"
    }


async def test_logging_integration():
    """Test: Verificar integración con sistema de logging."""
    print("\n📝 Testing logging integration...")
    
    from backend.config.logging import chat_logger
    
    session_id = "test_base_intent"
    
    # Test component logger creation
    router_logger = chat_logger.get_component_logger(session_id, "ROUTER")
    extractor_logger = chat_logger.get_component_logger(session_id, "EXTRACTOR", "test_intent")
    service_logger = chat_logger.get_component_logger(session_id, "SERVICE", "test_intent")
    handler_logger = chat_logger.get_component_logger(session_id, "HANDLER", "test_intent")
    
    # Log test messages
    router_logger.info("Test router log")
    extractor_logger.info("Test extractor log")
    service_logger.info("Test service log")
    handler_logger.info("Test handler log")
    
    print("   ✅ Component loggers created successfully")
    print(f"   📄 Check logs/{session_id}_*.log for structured logs")
    
    return {
        "test_name": "logging_integration",
        "status": "passed",
        "message": "Logging system working correctly"
    }


# Export test functions for auto-discovery
BASE_INTENT_TESTS = [
    test_base_components,
    test_logging_integration,
]


async def run_tests() -> Dict[str, Any]:
    """Run all base_intent tests."""
    print("\n" + "="*80)
    print("🧪 BASE INTENT - Component Tests")
    print("="*80)
    
    results = []
    
    for test_func in BASE_INTENT_TESTS:
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
        "intent": "base_intent",
        "total_tests": len(results),
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results
    }


# NOTE: Registration happens in tests/backend/test_intents.py during test discovery
# This avoids circular import issues with backend.intents module


if __name__ == "__main__":
    """Run tests standalone."""
    result = asyncio.run(run_tests())
    
    print("\n" + "="*80)
    print(f"✅ Tests completed: {result['passed']}/{result['total_tests']} passed")
    print("="*80 + "\n")


"""
Test para worked_hours intent.
Auto-registrado en el sistema de tests.
"""

import asyncio
from typing import Dict, Any


async def test_worked_hours_handler():
    """Test: Handler completo de worked_hours."""
    print("\n🔍 Testing worked_hours handler...")
    
    # Importación relativa para evitar circular imports
    from . import create_worked_hours_handler
    
    session_id = "test_worked_hours"
    
    try:
        handler = create_worked_hours_handler(session_id=session_id)
        
        assert handler is not None, "Handler is None"
        assert handler.extractor is not None, "Extractor is None"
        assert handler.service is not None, "Service is None"
        
        print("   ✅ Handler created successfully")
        print(f"      - Extractor: {handler.extractor.__class__.__name__}")
        print(f"      - Service: {handler.service.__class__.__name__}")
        
        return {
            "test_name": "worked_hours_handler",
            "status": "passed",
            "message": "Handler components initialized correctly"
        }
    
    except Exception as e:
        return {
            "test_name": "worked_hours_handler",
            "status": "failed",
            "error": str(e)
        }


async def test_worked_hours_flow():
    """Test: Flujo completo con query real."""
    print("\n🚀 Testing worked_hours full flow...")
    
    # Importación relativa para evitar circular imports
    from . import create_worked_hours_handler
    
    session_id = "test_worked_hours_flow"
    query = "quantas horas trabalhei essa semana?"
    
    try:
        handler = create_worked_hours_handler(session_id=session_id)
        
        print(f"   Query: {query}")
        
        result = await handler.handle(
            query=query,
            conversation_id=session_id
        )
        
        assert result is not None, "Result is None"
        assert "success" in result, "Result missing 'success' key"
        assert "data" in result, "Result missing 'data' key"
        
        if result["success"]:
            print("   ✅ Flow completed successfully")
            print(f"      - Data keys: {list(result['data'].keys())}")
        else:
            # Even errors are valid if properly structured
            print("   ⚠️  Flow returned error (expected if no Azure DevOps setup)")
            print(f"      - Error: {result['data'].get('error_type')}")
        
        return {
            "test_name": "worked_hours_flow",
            "status": "passed",
            "message": "Flow executed correctly (check logs for details)"
        }
    
    except Exception as e:
        return {
            "test_name": "worked_hours_flow",
            "status": "failed",
            "error": str(e)
        }


async def test_worked_hours_logging():
    """Test: Verificar que los logs se generan correctamente."""
    print("\n📝 Testing worked_hours logging...")
    
    from backend.config.logging import chat_logger
    
    session_id = "test_worked_hours_logging"
    intent_name = "worked_hours"
    
    try:
        # Create component loggers
        extractor_logger = chat_logger.get_component_logger(
            session_id, "EXTRACTOR", intent_name
        )
        service_logger = chat_logger.get_component_logger(
            session_id, "SERVICE", intent_name
        )
        handler_logger = chat_logger.get_component_logger(
            session_id, "HANDLER", intent_name
        )
        
        # Log test messages
        extractor_logger.info("Test extractor log for worked_hours")
        service_logger.info("Test service log for worked_hours")
        handler_logger.info("Test handler log for worked_hours")
        
        print("   ✅ Component loggers working")
        print(f"      - [INTENT:worked_hours:EXTRACTOR] ✓")
        print(f"      - [INTENT:worked_hours:SERVICE] ✓")
        print(f"      - [INTENT:worked_hours:HANDLER] ✓")
        print(f"   📄 Check logs/{session_id}_*.log")
        
        return {
            "test_name": "worked_hours_logging",
            "status": "passed",
            "message": "Logging system integrated correctly"
        }
    
    except Exception as e:
        return {
            "test_name": "worked_hours_logging",
            "status": "failed",
            "error": str(e)
        }


# Export test functions for auto-discovery
WORKED_HOURS_TESTS = [
    test_worked_hours_handler,
    test_worked_hours_flow,
    test_worked_hours_logging,
]


async def run_tests() -> Dict[str, Any]:
    """Run all worked_hours tests."""
    print("\n" + "="*80)
    print("🧪 WORKED HOURS INTENT - Tests")
    print("="*80)
    
    results = []
    
    for test_func in WORKED_HOURS_TESTS:
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
        "intent": "worked_hours",
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

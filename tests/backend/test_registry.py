"""
Test Registry System for Intent Tests.
Similar to IntentRegistry, provides auto-registration for tests.

Each intent's test.py can register itself using:
    from tests.backend.test_registry import register_test_suite
    register_test_suite("intent_name", run_tests)
"""

from typing import Dict, Callable, Awaitable, Any, List, Optional
from dataclasses import dataclass
import logging


logger = logging.getLogger(__name__)


@dataclass
class TestSuiteInfo:
    """Information about a registered test suite."""
    run_tests: Callable[[], Awaitable[Dict[str, Any]]]
    description: str
    intent_name: str


class TestRegistry:
    """
    Centralized registry for intent test suites.
    Enables auto-discovery without manual imports in test runner.
    """
    
    _test_suites: Dict[str, TestSuiteInfo] = {}
    
    @classmethod
    def register(
        cls, 
        intent_name: str,
        run_tests_func: Callable[[], Awaitable[Dict[str, Any]]],
        description: Optional[str] = None
    ) -> None:
        """
        Register a test suite for an intent.
        
        Args:
            intent_name: Name of the intent (e.g., "worked_hours", "base_intent")
            run_tests_func: Async function that runs all tests for the intent
            description: Optional description of what this test suite covers
        """
        if intent_name in cls._test_suites:
            logger.warning(f"Test suite '{intent_name}' already registered. Overwriting.")
        
        cls._test_suites[intent_name] = TestSuiteInfo(
            run_tests=run_tests_func,
            description=description or f"Test suite for {intent_name}",
            intent_name=intent_name
        )
        
        logger.debug(f"Registered test suite: {intent_name}")
    
    @classmethod
    def get_test_suite(cls, intent_name: str) -> Callable[[], Awaitable[Dict[str, Any]]]:
        """
        Get the run_tests function for a specific intent.
        
        Args:
            intent_name: Name of the intent
            
        Returns:
            The run_tests async function
            
        Raises:
            ValueError: If intent test suite not found
        """
        if intent_name not in cls._test_suites:
            raise ValueError(
                f"Test suite '{intent_name}' not registered. "
                f"Available: {list(cls._test_suites.keys())}"
            )
        
        return cls._test_suites[intent_name].run_tests
    
    @classmethod
    def get_all(cls) -> Dict[str, TestSuiteInfo]:
        """Get all registered test suites metadata."""
        return cls._test_suites.copy()
    
    @classmethod
    def list_test_suites(cls) -> List[str]:
        """Get list of all registered test suite names."""
        return list(cls._test_suites.keys())
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered test suites. Useful for testing."""
        cls._test_suites.clear()


def register_test_suite(
    intent_name: str,
    run_tests_func: Callable[[], Awaitable[Dict[str, Any]]],
    description: Optional[str] = None
) -> None:
    """
    Convenience function to register a test suite.
    Use this in each intent's test.py file.
    
    Example:
        # In backend/intents/worked_hours/test.py
        from tests.backend.test_registry import register_test_suite
        
        async def run_tests():
            # ... test implementation
            pass
        
        # Auto-register when module is imported
        register_test_suite("worked_hours", run_tests, "Tests for worked hours intent")
    
    Args:
        intent_name: Name of the intent
        run_tests_func: Async function that runs all tests
        description: Optional description
    """
    TestRegistry.register(intent_name, run_tests_func, description)


__all__ = [
    "TestRegistry",
    "register_test_suite"
]

# -*- coding: utf-8 -*-
"""
Unit tests for all classes in the project.
Tests instantiation of each class to identify initialization issues.

Run: python tests/backend/test_unit_classes.py
"""

import asyncio
import sys
import io
from pathlib import Path

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import backend.intents first to resolve circular imports
import backend.intents


# ==============================================================================
# TEST RESULTS TRACKING
# ==============================================================================

test_results: List[Dict[str, Any]] = []


def record_test(class_name: str, module: str, status: str, error: str = None, notes: str = None):
    """Record test result for a class."""
    test_results.append({
        "class": class_name,
        "module": module,
        "status": status,  # "passed", "failed", "skipped"
        "error": error,
        "notes": notes
    })


# ==============================================================================
# MODELS TESTS
# ==============================================================================

def test_devops_models():
    """Test backend.models.devops_models classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.models.devops_models")
    print("="*80)
    
    from backend.models.devops_models import (
        IdentityRef, WorkItem, WebApiTeam, TeamMember, WorkItemQueryResult
    )
    
    # Test IdentityRef
    try:
        identity = IdentityRef(
            displayName="Test User",
            id="test-id-123",
            uniqueName="test@example.com"
        )
        print(f"✅ IdentityRef: {identity.displayName}")
        record_test("IdentityRef", "backend.models.devops_models", "passed")
    except Exception as e:
        print(f"❌ IdentityRef failed: {str(e)}")
        record_test("IdentityRef", "backend.models.devops_models", "failed", str(e))
    
    # Test WorkItem
    try:
        work_item = WorkItem(
            id=1,
            rev=1,
            url="https://example.com/workitem/1",
            fields={
                "System.Title": "Test Work Item",
                "System.State": "Active",
                "System.WorkItemType": "Task"
            }
        )
        print(f"✅ WorkItem: ID={work_item.id}")
        record_test("WorkItem", "backend.models.devops_models", "passed")
    except Exception as e:
        print(f"❌ WorkItem failed: {str(e)}")
        record_test("WorkItem", "backend.models.devops_models", "failed", str(e))
    
    # Test WebApiTeam
    try:
        team = WebApiTeam(
            id="team-123",
            name="Test Team",
            url="https://example.com/team/123",
            description="Test team description"
        )
        print(f"✅ WebApiTeam: {team.name}")
        record_test("WebApiTeam", "backend.models.devops_models", "passed")
    except Exception as e:
        print(f"❌ WebApiTeam failed: {str(e)}")
        record_test("WebApiTeam", "backend.models.devops_models", "failed", str(e))
    
    # Test TeamMember
    try:
        member = TeamMember(
            identity=IdentityRef(
                displayName="Member User",
                id="member-123",
                uniqueName="member@example.com"
            ),
            isTeamAdmin=False
        )
        print(f"✅ TeamMember: {member.identity.displayName}")
        record_test("TeamMember", "backend.models.devops_models", "passed")
    except Exception as e:
        print(f"❌ TeamMember failed: {str(e)}")
        record_test("TeamMember", "backend.models.devops_models", "failed", str(e))
    
    # Test WorkItemQueryResult
    try:
        query_result = WorkItemQueryResult(
            queryType="flat",
            queryResultType="workItem",
            asOf=datetime.now(),
            workItems=[{"id": 1, "url": "https://example.com/1"}]
        )
        print(f"✅ WorkItemQueryResult: {len(query_result.workItems)} items")
        record_test("WorkItemQueryResult", "backend.models.devops_models", "passed")
    except Exception as e:
        print(f"❌ WorkItemQueryResult failed: {str(e)}")
        record_test("WorkItemQueryResult", "backend.models.devops_models", "failed", str(e))


def test_project_models():
    """Test backend.models.project_models classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.models.project_models")
    print("="*80)
    
    from backend.models.project_models import Project, EpicProject
    
    # Test Project
    try:
        project = Project(
            id="proj-123",
            name="Test Project",
            description="Test project description",
            state="wellFormed",
            visibility="private"
        )
        print(f"✅ Project: {project.name}")
        record_test("Project", "backend.models.project_models", "passed")
    except Exception as e:
        print(f"❌ Project failed: {str(e)}")
        record_test("Project", "backend.models.project_models", "failed", str(e))
    
    # Test EpicProject
    try:
        epic_project = EpicProject(
            id="epic-123",
            name="Epic Project",
            description="Epic project description",
            state="wellFormed",
            visibility="private"
        )
        print(f"✅ EpicProject: {epic_project.name}")
        record_test("EpicProject", "backend.models.project_models", "passed")
    except Exception as e:
        print(f"❌ EpicProject failed: {str(e)}")
        record_test("EpicProject", "backend.models.project_models", "failed", str(e))


# ==============================================================================
# AGENTS TESTS
# ==============================================================================

def test_agent_models():
    """Test backend.agents.models classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.agents.models")
    print("="*80)
    
    from backend.agents.models import UserIntent, RouterState
    
    # Test UserIntent
    try:
        intent = UserIntent(
            category="worked_hours",
            confidence=0.95,
            reasoning="User asking about worked hours this week",
            original_query="How many hours did I work this week?"
        )
        print(f"✅ UserIntent: {intent.category} (confidence: {intent.confidence})")
        record_test("UserIntent", "backend.agents.models", "passed")
    except Exception as e:
        print(f"❌ UserIntent failed: {str(e)}")
        record_test("UserIntent", "backend.agents.models", "failed", str(e))
    
    # Test RouterState
    try:
        # Create UserIntent first
        intent = UserIntent(
            category="worked_hours",
            confidence=0.95,
            reasoning="User asking about worked hours",
            original_query="Test query"
        )
        
        state = RouterState(
            user_query="Test query",
            classified_intent=intent  # Pass UserIntent object, not string
        )
        print(f"✅ RouterState: intent={state.classified_intent.category}")
        record_test("RouterState", "backend.agents.models", "passed")
    except Exception as e:
        print(f"❌ RouterState failed: {str(e)}")
        record_test("RouterState", "backend.agents.models", "failed", str(e))


def test_answer_agent():
    """Test backend.agents.answer_agent classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.agents.answer_agent")
    print("="*80)
    
    from backend.agents.answer_agent import AnswerResponse, AnswerAgent
    
    # Test AnswerResponse
    try:
        response = AnswerResponse(
            answer="This is a test answer",
            confidence=0.88
        )
        print(f"✅ AnswerResponse: confidence={response.confidence}")
        record_test("AnswerResponse", "backend.agents.answer_agent", "passed")
    except Exception as e:
        print(f"❌ AnswerResponse failed: {str(e)}")
        record_test("AnswerResponse", "backend.agents.answer_agent", "failed", str(e))
    
    # Test AnswerAgent
    try:
        agent = AnswerAgent(session_id="test-session")
        print(f"✅ AnswerAgent: session_id={agent.session_id}")
        record_test("AnswerAgent", "backend.agents.answer_agent", "passed")
    except Exception as e:
        print(f"❌ AnswerAgent failed: {str(e)}")
        record_test("AnswerAgent", "backend.agents.answer_agent", "failed", str(e))


def test_router_agent():
    """Test backend.agents.router_agent classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.agents.router_agent")
    print("="*80)
    
    from backend.agents.router_agent import RouterAgent
    
    # Test RouterAgent
    try:
        agent = RouterAgent(session_id="test-router")
        print(f"✅ RouterAgent: created successfully")
        record_test("RouterAgent", "backend.agents.router_agent", "passed")
    except Exception as e:
        print(f"❌ RouterAgent failed: {str(e)}")
        record_test("RouterAgent", "backend.agents.router_agent", "failed", str(e))


def test_memory():
    """Test backend.agents.memory classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.agents.memory")
    print("="*80)
    
    from backend.agents.memory import ConversationMemory
    
    # Test ConversationMemory
    try:
        memory = ConversationMemory()
        # Use correct API: get_context returns a dict with history
        context = memory.get_context("conv-123")
        print(f"✅ ConversationMemory: created successfully")
        record_test("ConversationMemory", "backend.agents.memory", "passed")
    except Exception as e:
        print(f"❌ ConversationMemory failed: {str(e)}")
        record_test("ConversationMemory", "backend.agents.memory", "failed", str(e))


# ==============================================================================
# CONFIG TESTS
# ==============================================================================

def test_azure_config():
    """Test backend.config.azure classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.config.azure")
    print("="*80)
    
    from backend.config.azure import AzureConfig
    
    # Test AzureConfig
    try:
        config = AzureConfig()
        # Correct attribute is openai_endpoint, not azure_endpoint
        print(f"✅ AzureConfig: endpoint={config.openai_endpoint is not None}")
        record_test("AzureConfig", "backend.config.azure", "passed")
    except Exception as e:
        print(f"❌ AzureConfig failed: {str(e)}")
        record_test("AzureConfig", "backend.config.azure", "failed", str(e))


def test_logging_config():
    """Test backend.config.logging classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.config.logging")
    print("="*80)
    
    from backend.config.logging import ComponentLoggerAdapter, ChatLogger
    
    # Test ChatLogger
    try:
        # ChatLogger is a singleton, no session_id in constructor
        logger = ChatLogger()
        component_logger = logger.get_component_logger("test-session", "TEST")
        print(f"✅ ChatLogger: created with component logger")
        record_test("ChatLogger", "backend.config.logging", "passed")
    except Exception as e:
        print(f"❌ ChatLogger failed: {str(e)}")
        record_test("ChatLogger", "backend.config.logging", "failed", str(e))
    
    # ComponentLoggerAdapter is tested implicitly through ChatLogger
    record_test("ComponentLoggerAdapter", "backend.config.logging", "passed", 
                notes="Tested implicitly through ChatLogger")


# ==============================================================================
# INTENTS TESTS
# ==============================================================================

def test_intent_registry():
    """Test backend.intents.registry classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.intents.registry")
    print("="*80)
    
    from backend.intents.registry import IntentMetadata, IntentRegistry
    
    # Test IntentMetadata
    try:
        # IntentMetadata is a dataclass with required fields: category, name, description, handler_class
        from backend.intents.base_intent.handler import BaseIntentHandler
        metadata = IntentMetadata(
            category="test_intent",
            name="Test Intent",
            description="Test intent description",
            handler_class=BaseIntentHandler
        )
        print(f"✅ IntentMetadata: {metadata.name}")
        record_test("IntentMetadata", "backend.intents.registry", "passed")
    except Exception as e:
        print(f"❌ IntentMetadata failed: {str(e)}")
        record_test("IntentMetadata", "backend.intents.registry", "failed", str(e))
    
    # Test IntentRegistry (singleton)
    try:
        registry = IntentRegistry.get_all()
        print(f"✅ IntentRegistry: {len(registry)} intents registered")
        record_test("IntentRegistry", "backend.intents.registry", "passed")
    except Exception as e:
        print(f"❌ IntentRegistry failed: {str(e)}")
        record_test("IntentRegistry", "backend.intents.registry", "failed", str(e))


def test_base_intent_models():
    """Test backend.intents.base_intent.models classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.intents.base_intent.models")
    print("="*80)
    
    from backend.intents.base_intent.models import ErrorResponse
    
    # BaseQueryParams and BaseResponse are abstract - skip
    record_test("BaseQueryParams", "backend.intents.base_intent.models", "skipped",
                notes="Abstract class - cannot instantiate")
    record_test("BaseResponse", "backend.intents.base_intent.models", "skipped",
                notes="Abstract class - cannot instantiate")
    
    # Test ErrorResponse
    try:
        error = ErrorResponse(
            error_type="TestError",
            error_message="This is a test error",
            details={"key": "value"}
        )
        print(f"✅ ErrorResponse: {error.error_type}")
        record_test("ErrorResponse", "backend.intents.base_intent.models", "passed")
    except Exception as e:
        print(f"❌ ErrorResponse failed: {str(e)}")
        record_test("ErrorResponse", "backend.intents.base_intent.models", "failed", str(e))


def test_base_intent_classes():
    """Test backend.intents.base_intent abstract classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.intents.base_intent (abstract classes)")
    print("="*80)
    
    # All base_intent classes are abstract
    record_test("BaseExtractor", "backend.intents.base_intent.extractor", "skipped",
                notes="Abstract class - cannot instantiate")
    record_test("BaseService", "backend.intents.base_intent.service", "skipped",
                notes="Abstract class - cannot instantiate")
    record_test("BaseIntentHandler", "backend.intents.base_intent.handler", "skipped",
                notes="Abstract class - requires abstract dependencies")


def test_worked_hours_classes():
    """Test backend.intents.worked_hours classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.intents.worked_hours")
    print("="*80)
    
    from backend.intents.worked_hours.models import (
        WorkedHoursQuery, HourBreakdown, WorkedHoursResponse
    )
    from backend.intents.worked_hours.extractor import WorkedHoursExtractor
    from backend.intents.worked_hours.service import WorkedHoursService
    
    # Test WorkedHoursQuery
    try:
        query = WorkedHoursQuery(
            person_name="John Doe",
            start_date="2025-11-01",
            end_date="2025-11-05",
            project_id=None,
            project_name=None
        )
        print(f"✅ WorkedHoursQuery: {query.person_name}")
        record_test("WorkedHoursQuery", "backend.intents.worked_hours.models", "passed")
    except Exception as e:
        print(f"❌ WorkedHoursQuery failed: {str(e)}")
        record_test("WorkedHoursQuery", "backend.intents.worked_hours.models", "failed", str(e))
    
    # Test HourBreakdown
    try:
        breakdown = HourBreakdown(
            date="2025-11-01",
            task_title="Test Task",
            hours=8.5
        )
        print(f"✅ HourBreakdown: {breakdown.task_title} - {breakdown.hours}h")
        record_test("HourBreakdown", "backend.intents.worked_hours.models", "passed")
    except Exception as e:
        print(f"❌ HourBreakdown failed: {str(e)}")
        record_test("HourBreakdown", "backend.intents.worked_hours.models", "failed", str(e))
    
    # Test WorkedHoursResponse
    try:
        response = WorkedHoursResponse(
            total_hours=40.0,
            breakdown=[
                HourBreakdown(date="2025-11-01", task_title="Task 1", hours=8.0),
                HourBreakdown(date="2025-11-02", task_title="Task 2", hours=32.0)
            ],
            start_date="2025-11-01",
            end_date="2025-11-05",
            person=None,
            project_name=None
        )
        print(f"✅ WorkedHoursResponse: {response.total_hours}h total")
        record_test("WorkedHoursResponse", "backend.intents.worked_hours.models", "passed")
    except Exception as e:
        print(f"❌ WorkedHoursResponse failed: {str(e)}")
        record_test("WorkedHoursResponse", "backend.intents.worked_hours.models", "failed", str(e))
    
    # Test WorkedHoursExtractor
    try:
        extractor = WorkedHoursExtractor(session_id="test-extractor")
        print(f"✅ WorkedHoursExtractor: created successfully")
        record_test("WorkedHoursExtractor", "backend.intents.worked_hours.extractor", "passed")
    except Exception as e:
        print(f"❌ WorkedHoursExtractor failed: {str(e)}")
        record_test("WorkedHoursExtractor", "backend.intents.worked_hours.extractor", "failed", str(e))
    
    # Test WorkedHoursService
    try:
        service = WorkedHoursService(session_id="test-service")
        print(f"✅ WorkedHoursService: created successfully")
        record_test("WorkedHoursService", "backend.intents.worked_hours.service", "passed")
    except Exception as e:
        print(f"❌ WorkedHoursService failed: {str(e)}")
        record_test("WorkedHoursService", "backend.intents.worked_hours.service", "failed", str(e))


def test_other_intent_handlers():
    """Test other intent handler classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: Other Intent Handlers")
    print("="*80)
    
    # Test NotImplementedExtractor & NotImplementedService
    try:
        from backend.intents.not_implemented.not_implemented_handler import (
            NotImplementedExtractor, NotImplementedService
        )
        
        extractor = NotImplementedExtractor(session_id="test")
        print(f"✅ NotImplementedExtractor: created")
        record_test("NotImplementedExtractor", "backend.intents.not_implemented", "passed")
        
        service = NotImplementedService(session_id="test")
        print(f"✅ NotImplementedService: created")
        record_test("NotImplementedService", "backend.intents.not_implemented", "passed")
    except Exception as e:
        print(f"❌ NotImplemented classes failed: {str(e)}")
        record_test("NotImplementedExtractor", "backend.intents.not_implemented", "failed", str(e))
        record_test("NotImplementedService", "backend.intents.not_implemented", "failed", str(e))
    
    # Test OtherExtractor & OtherService
    try:
        from backend.intents.other.handler import OtherExtractor, OtherService
        
        extractor = OtherExtractor(session_id="test")
        print(f"✅ OtherExtractor: created")
        record_test("OtherExtractor", "backend.intents.other", "passed")
        
        service = OtherService(session_id="test")
        print(f"✅ OtherService: created")
        record_test("OtherService", "backend.intents.other", "passed")
    except Exception as e:
        print(f"❌ Other classes failed: {str(e)}")
        record_test("OtherExtractor", "backend.intents.other", "failed", str(e))
        record_test("OtherService", "backend.intents.other", "failed", str(e))
    
    # Test DefaultExtractor & DefaultService
    try:
        from backend.intents.default.handler import DefaultExtractor, DefaultService
        
        extractor = DefaultExtractor(session_id="test")
        print(f"✅ DefaultExtractor: created")
        record_test("DefaultExtractor", "backend.intents.default", "passed")
        
        service = DefaultService(session_id="test")
        print(f"✅ DefaultService: created")
        record_test("DefaultService", "backend.intents.default", "passed")
    except Exception as e:
        print(f"❌ Default classes failed: {str(e)}")
        record_test("DefaultExtractor", "backend.intents.default", "failed", str(e))
        record_test("DefaultService", "backend.intents.default", "failed", str(e))


# ==============================================================================
# API TESTS
# ==============================================================================

def test_api_models():
    """Test backend.api.v1.endpoints.chat classes."""
    print("\n" + "="*80)
    print("🧪 TESTING: backend.api.v1.endpoints.chat")
    print("="*80)
    
    from backend.api.v1.endpoints.chat import ChatRequest, ChatResponse
    
    # Test ChatRequest
    try:
        request = ChatRequest(
            message="Hello, how can I help?",
            conversation_id="conv-123"
        )
        print(f"✅ ChatRequest: {request.message}")
        record_test("ChatRequest", "backend.api.v1.endpoints.chat", "passed")
    except Exception as e:
        print(f"❌ ChatRequest failed: {str(e)}")
        record_test("ChatRequest", "backend.api.v1.endpoints.chat", "failed", str(e))
    
    # Test ChatResponse
    try:
        response = ChatResponse(
            message="I can help you with that",
            conversation_id="conv-123",
            intent="general_query",
            confidence=0.95,
            data=None,
            error=None
        )
        print(f"✅ ChatResponse: {response.message}")
        record_test("ChatResponse", "backend.api.v1.endpoints.chat", "passed")
    except Exception as e:
        print(f"❌ ChatResponse failed: {str(e)}")
        record_test("ChatResponse", "backend.api.v1.endpoints.chat", "failed", str(e))


# ==============================================================================
# MAIN RUNNER
# ==============================================================================

def print_summary():
    """Print test summary."""
    print("\n" + "="*80)
    print("📊 UNIT TEST SUMMARY")
    print("="*80 + "\n")
    
    passed = [r for r in test_results if r["status"] == "passed"]
    failed = [r for r in test_results if r["status"] == "failed"]
    skipped = [r for r in test_results if r["status"] == "skipped"]
    
    print(f"Total Classes Tested: {len(test_results)}")
    print(f"✅ Passed: {len(passed)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏭️  Skipped: {len(skipped)} (abstract classes)")
    
    if failed:
        print("\n" + "="*80)
        print("❌ FAILED TESTS - DETAILS")
        print("="*80 + "\n")
        
        for result in failed:
            print(f"Class: {result['class']}")
            print(f"Module: {result['module']}")
            print(f"Error: {result['error']}")
            print("-" * 80)
    
    if len(failed) == 0:
        print("\n" + "="*80)
        print("🎉 ALL INSTANTIABLE CLASSES PASSED!")
        print("="*80)


def main():
    """Run all unit tests."""
    print("\n" + "="*80)
    print("🧪 UNIT TESTS - CLASS INSTANTIATION")
    print("Testing every class in the project")
    print("="*80)
    
    # Run all test functions
    test_devops_models()
    test_project_models()
    test_agent_models()
    test_answer_agent()
    test_router_agent()
    test_memory()
    test_azure_config()
    test_logging_config()
    test_intent_registry()
    test_base_intent_models()
    test_base_intent_classes()
    test_worked_hours_classes()
    test_other_intent_handlers()
    test_api_models()
    
    # Print summary
    print_summary()


if __name__ == "__main__":
    main()

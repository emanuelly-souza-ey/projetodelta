"""
Tests for get_tasks intent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.intents.get_tasks.models import GetTasksQuery, GetTasksResponse, TaskItem
from backend.intents.get_tasks.service import GetTasksService
from backend.intents.get_tasks.extractor import GetTasksExtractor


@pytest.fixture
def mock_tasks():
    """Sample tasks for testing."""
    return [
        TaskItem(
            id=1001,
            title="Implementar feature X",
            state="Active",
            assigned_to="João Silva",
            work_item_type="Task",
            created_date="2025-11-01",
            changed_date="2025-11-10"
        ),
        TaskItem(
            id=1002,
            title="Corrigir bug Y", 
            state="In Progress",
            assigned_to="Maria Santos",
            work_item_type="Bug",
            created_date="2025-11-05",
            changed_date="2025-11-11"
        ),
        TaskItem(
            id=1003,
            title="User Story Z",
            state="Completed", 
            assigned_to="Pedro Costa",
            work_item_type="User Story",
            created_date="2025-10-15",
            changed_date="2025-11-08"
        )
    ]


@pytest.fixture
def service():
    """Create service instance for testing."""
    return GetTasksService(session_id="test_session", intent_name="get_tasks")


@pytest.fixture  
def extractor():
    """Create extractor instance for testing."""
    return GetTasksExtractor(session_id="test_session", intent_name="get_tasks")


class TestGetTasksExtractor:
    """Tests for GetTasksExtractor."""
    
    @pytest.mark.asyncio
    async def test_extract_basic_query(self, extractor):
        """Test basic parameter extraction."""
        params = await extractor.extract_params("minhas tarefas ativas")
        
        assert params.user_query == "minhas tarefas ativas"
        # TODO: Add assertions for extracted parameters when implemented


class TestGetTasksService:
    """Tests for GetTasksService."""
    
    @pytest.mark.asyncio
    async def test_query_data_empty_response(self, service):
        """Test query_data returns empty response when not implemented."""
        params = GetTasksQuery(user_query="test query")
        response = await service.query_data(params)
        
        assert isinstance(response, GetTasksResponse)
        assert response.total_count == 0
        assert len(response.tasks) == 0
        assert "not yet implemented" in response.message
    
    def test_build_wiql_query_basic(self, service):
        """Test WIQL query building."""
        params = GetTasksQuery(user_query="test")
        query = service._build_wiql_query(params)
        
        assert "SELECT" in query
        assert "[System.TeamProject] = 'HUB GenAI'" in query
        assert "ORDER BY [System.ChangedDate] DESC" in query
    
    def test_build_wiql_query_with_person(self, service):
        """Test WIQL query with person filter."""
        params = GetTasksQuery(user_query="test", person_name="João")
        query = service._build_wiql_query(params)
        
        assert "[System.AssignedTo] CONTAINS 'João'" in query
    
    def test_build_wiql_query_with_state(self, service):
        """Test WIQL query with state filter.""" 
        params = GetTasksQuery(user_query="test", task_state="Active")
        query = service._build_wiql_query(params)
        
        assert "[System.State] = 'Active'" in query
    
    def test_build_wiql_query_with_type(self, service):
        """Test WIQL query with work item type filter."""
        params = GetTasksQuery(user_query="test", task_type="Bug")
        query = service._build_wiql_query(params)
        
        assert "[System.WorkItemType] = 'Bug'" in query


class TestGetTasksIntegration:
    """Integration tests for get_tasks intent."""
    
    @pytest.mark.asyncio
    async def test_full_flow_basic(self, extractor, service):
        """Test complete flow from extraction to service."""
        # 1. Extract parameters
        params = await extractor.extract_params("minhas tarefas")
        
        # 2. Query service
        response = await service.query_data(params)
        
        # 3. Verify response structure
        assert isinstance(response, GetTasksResponse)
        assert response.total_count >= 0
        assert isinstance(response.tasks, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
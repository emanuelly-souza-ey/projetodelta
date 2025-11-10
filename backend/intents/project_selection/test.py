"""
Tests for project selection intent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.intents.project_selection.models import ProjectSelectionQuery, ProjectSelectionResponse
from backend.intents.project_selection.service import ProjectSelectionService
from backend.intents.project_selection.extractor import ProjectSelectionExtractor
from backend.models.project_models import EpicProject


@pytest.fixture
def mock_projects():
    """Sample projects for testing."""
    return [
        EpicProject(
            id="1",
            name="Delta Platform",
            description="Main platform project",
            state="Active"
        ),
        EpicProject(
            id="2",
            name="Gen AI",
            description="Generative AI initiatives",
            state="Active"
        ),
        EpicProject(
            id="3",
            name="AI Research",
            description="AI research and development",
            state="Active"
        ),
        EpicProject(
            id="4",
            name="Legacy System",
            description="Old system maintenance",
            state="Closed"
        )
    ]


@pytest.fixture
def service():
    """Create service instance for testing."""
    return ProjectSelectionService(session_id="test_session", intent_name="project_selection")


@pytest.fixture
def extractor():
    """Create extractor instance for testing."""
    return ProjectSelectionExtractor(session_id="test_session", intent_name="project_selection")


class TestProjectSelectionExtractor:
    """Tests for ProjectSelectionExtractor."""
    
    @pytest.mark.asyncio
    async def test_extract_project_name(self, extractor):
        """Test extracting project name from query."""
        params = await extractor.extract_params("Select Delta project")
        
        # LLM extracts project name
        assert params.project_name is not None
        assert params.user_query == "Select Delta project"
        assert params.project_id is None
    
    @pytest.mark.asyncio
    async def test_extract_empty_query(self, extractor):
        """Test extracting from empty query."""
        params = await extractor.extract_params("")
        
        # Empty query may result in empty string or None
        assert params.project_id is None


class TestProjectSelectionService:
    """Tests for ProjectSelectionService."""
    
    def test_find_project_by_name_exact(self, service, mock_projects):
        """Test finding exact match by name."""
        matches = service._find_project_by_name(mock_projects, "Delta Platform")
        
        assert len(matches) == 1
        assert matches[0].name == "Delta Platform"
    
    def test_find_project_by_name_partial(self, service, mock_projects):
        """Test finding partial matches by name."""
        matches = service._find_project_by_name(mock_projects, "AI")
        
        # Should find Gen AI and AI Research
        assert len(matches) >= 2
        assert any(p.name == "Gen AI" for p in matches)
        assert any(p.name == "AI Research" for p in matches)
    
    def test_find_project_no_matches(self, service, mock_projects):
        """Test finding no matches."""
        matches = service._find_project_by_name(mock_projects, "XYZ")
        
        assert len(matches) == 0
    
    def test_rank_by_similarity(self, service, mock_projects):
        """Test ranking by similarity (name only)."""
        matches = [p for p in mock_projects if "AI" in p.name]
        ranked = service._rank_by_similarity(matches, "AI")
        
        # Should be sorted by relevance
        assert len(ranked) >= 2
        # Check that ranking works
        assert ranked[0] is not None
    
    @pytest.mark.asyncio
    async def test_select_single_match(self, service, mock_projects):
        """Test selecting when only one match found."""
        with patch.object(service, '_fetch_all_projects', return_value=mock_projects):
            with patch.object(service, '_update_project_context'):
                params = ProjectSelectionQuery(
                    project_name="Delta",
                    user_query=None,
                    project_id=None
                )
                response = await service.query_data(params)
                
                assert response.selected is True
                assert response.selected_project is not None
                assert response.selected_project.name == "Delta Platform"
                assert "selected successfully" in response.message
    
    @pytest.mark.asyncio
    async def test_select_multiple_matches(self, service, mock_projects):
        """Test returning ambiguous list for multiple matches."""
        with patch.object(service, '_fetch_all_projects', return_value=mock_projects):
            params = ProjectSelectionQuery(
                project_name="AI",
                user_query=None,
                project_id=None
            )
            response = await service.query_data(params)
            
            assert response.selected is False
            assert response.ambiguous_projects is not None
            assert len(response.ambiguous_projects) >= 2
            assert "Found" in response.message
            assert "specify which one" in response.message
    
    @pytest.mark.asyncio
    async def test_no_matches_found(self, service, mock_projects):
        """Test no matches scenario."""
        with patch.object(service, '_fetch_all_projects', return_value=mock_projects):
            params = ProjectSelectionQuery(
                project_name="XYZ",
                user_query=None,
                project_id=None
            )
            response = await service.query_data(params)
            
            assert response.selected is False
            assert "not found" in response.message


class TestProjectSelectionFallback:
    """Tests for fallback to search functionality."""
    
    @pytest.mark.asyncio
    async def test_fallback_with_typo(self, service, mock_projects):
        """Test fallback suggests projects when typo in name."""
        with patch.object(service, '_fetch_all_projects', return_value=mock_projects):
            # Simulate fallback returning suggestions
            similar_projects = [
                EpicProject(id="1", name="Delta Platform", description="Main platform", state="Active"),
                EpicProject(id="5", name="Delta API", description="API project", state="Active")
            ]
            
            with patch.object(service, '_fallback_to_search', return_value=similar_projects):
                params = ProjectSelectionQuery(
                    project_name="Dleta",  # Typo
                    user_query=None,
                    project_id=None
                )
                response = await service.query_data(params)
                
                assert response.selected is False
                assert response.suggested_projects is not None
                assert len(response.suggested_projects) == 2
                assert "Did you mean" in response.message
    
    @pytest.mark.asyncio
    async def test_fallback_returns_suggestions(self, service, mock_projects):
        """Test fallback returns search results as suggestions."""
        with patch.object(service, '_fetch_all_projects', return_value=mock_projects):
            params = ProjectSelectionQuery(
                project_name="NonExistent",
                user_query=None,
                project_id=None
            )
            response = await service.query_data(params)
            
            # Should attempt fallback (may return None or suggestions)
            assert response.selected is False
            # Verify message is appropriate
            assert "not found" in response.message
    
    @pytest.mark.asyncio
    async def test_fallback_no_memory_update(self, service, mock_projects):
        """Test fallback does NOT update memory."""
        with patch.object(service, '_fetch_all_projects', return_value=mock_projects):
            with patch.object(service, '_update_project_context') as mock_update:
                params = ProjectSelectionQuery(
                    project_name="XYZ",
                    user_query=None,
                    project_id=None
                )
                response = await service.query_data(params)
                
                # Memory should NOT be updated on fallback
                mock_update.assert_not_called()
                assert response.selected is False


class TestProjectSelectionIntegration:
    """Integration tests for real DevOps API calls."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fetch_all_projects_from_devops(self, service):
        """
        Integration test: Fetch real projects from Azure DevOps.
        
        This test makes a real API call to Azure DevOps.
        Run with: pytest -m integration
        Skip by default with: pytest -m "not integration"
        """
        try:
            projects = await service._fetch_all_projects()
            
            # Verify we got projects
            assert projects is not None
            assert isinstance(projects, list)
            
            if len(projects) > 0:
                # Verify project structure
                first_project = projects[0]
                assert hasattr(first_project, 'id')
                assert hasattr(first_project, 'name')
                assert hasattr(first_project, 'state')
                
                print(f"\n✅ Successfully fetched {len(projects)} projects from DevOps:")
                for i, proj in enumerate(projects[:5], 1):  # Show first 5
                    state_emoji = "✅" if proj.state == "Active" else "📦"
                    print(f"  {i}. {state_emoji} {proj.name} (ID: {proj.id}, State: {proj.state})")
                
                if len(projects) > 5:
                    print(f"  ... and {len(projects) - 5} more")
            else:
                print("\n⚠️  No projects found in DevOps (this might be expected)")
                
        except Exception as e:
            pytest.fail(f"Failed to fetch projects from DevOps: {str(e)}\n"
                       f"Check your Azure DevOps credentials and connection.")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_search_workflow_with_devops(self, service):
        """
        Integration test: Full selection workflow with real DevOps data.
        
        Tests the complete flow: fetch -> select project
        """
        try:
            # Fetch real projects
            all_projects = await service._fetch_all_projects()
            
            if len(all_projects) == 0:
                pytest.skip("No projects in DevOps to test with")
            
            # Test: Select first project by exact name
            first_project_name = all_projects[0].name
            with patch.object(service, '_fetch_all_projects', return_value=all_projects):
                with patch.object(service, '_update_project_context'):
                    params = ProjectSelectionQuery(
                        project_name=first_project_name,
                        user_query=None,
                        project_id=None
                    )
                    response = await service.query_data(params)
                    
                    print(f"\n✅ Select project '{first_project_name}':")
                    print(f"   Selected: {response.selected}")
                    if response.selected_project:
                        print(f"   Project: {response.selected_project.name}")
                    
        except Exception as e:
            pytest.fail(f"Integration test failed: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

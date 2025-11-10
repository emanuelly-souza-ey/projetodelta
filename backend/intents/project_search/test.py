"""
Tests for project search intent.
"""

import pytest
from unittest.mock import patch
from backend.intents.project_search.models import ProjectSearchQuery, ProjectSearchResponse
from backend.intents.project_search.service import ProjectSearchService
from backend.intents.project_search.extractor import ProjectSearchExtractor
from backend.models.project_models import EpicProject


@pytest.fixture
def mock_projects():
    """Sample projects for testing."""
    return [
        EpicProject(
            id="1",
            name="Delta Platform",
            description="Main platform project with Python and FastAPI",
            state="Active"
        ),
        EpicProject(
            id="2",
            name="Gen AI",
            description="Generative AI initiatives using ML models",
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
        ),
        EpicProject(
            id="5",
            name="Python Tools",
            description="Internal Python tooling",
            state="Active"
        )
    ]


@pytest.fixture
def service():
    """Create service instance for testing."""
    return ProjectSearchService(session_id="test_session", intent_name="project_search")


@pytest.fixture
def extractor():
    """Create extractor instance for testing."""
    return ProjectSearchExtractor(session_id="test_session", intent_name="project_search")


class TestProjectSearchExtractor:
    """Tests for ProjectSearchExtractor."""
    
    @pytest.mark.asyncio
    async def test_extract_search_terms(self, extractor):
        """Test extracting multiple search terms."""
        params = await extractor.extract_params("Show me AI projects")
        
        # LLM extracts search terms
        assert params.search_terms is not None
        assert params.user_query == "Show me AI projects"
        assert isinstance(params.search_terms, list)
    
    @pytest.mark.asyncio
    async def test_extract_with_filters(self, extractor):
        """Test extracting filters."""
        params = await extractor.extract_params("List active projects")
        
        # LLM may extract state filter
        assert params.user_query == "List active projects"
    
    @pytest.mark.asyncio
    async def test_extract_empty_query(self, extractor):
        """Test extracting from empty query."""
        params = await extractor.extract_params("")
        
        # Should return empty search terms
        assert isinstance(params.search_terms, list)


class TestProjectSearchService:
    """Tests for ProjectSearchService."""
    
    def test_search_by_terms_single(self, service, mock_projects):
        """Test searching by single keyword."""
        matches = service._search_by_terms(mock_projects, ["AI"])
        
        # Should find Gen AI and AI Research
        assert len(matches) >= 2
        assert any(p.name == "Gen AI" for p in matches)
        assert any(p.name == "AI Research" for p in matches)
    
    def test_search_by_terms_multiple(self, service, mock_projects):
        """Test searching by multiple keywords."""
        matches = service._search_by_terms(mock_projects, ["Python", "AI"])
        
        # Should find projects with Python or AI
        assert len(matches) >= 3
        assert any(p.name == "Python Tools" for p in matches)
        assert any(p.name == "Delta Platform" for p in matches)
        assert any(p.name == "Gen AI" for p in matches)
    
    def test_search_by_terms_in_description(self, service, mock_projects):
        """Test searching in description."""
        matches = service._search_by_terms(mock_projects, ["FastAPI"])
        
        # Should find Delta Platform which has FastAPI in description
        assert len(matches) >= 1
        assert any(p.name == "Delta Platform" for p in matches)
    
    def test_search_no_matches(self, service, mock_projects):
        """Test searching with no matches."""
        matches = service._search_by_terms(mock_projects, ["XYZ123"])
        
        assert len(matches) == 0
    
    def test_apply_filters_active(self, service, mock_projects):
        """Test filtering by active state."""
        filtered = service._apply_filters(mock_projects, {"state": "active"})
        
        # Should exclude closed projects
        assert len(filtered) < len(mock_projects)
        assert all(p.state == "Active" for p in filtered)
        assert not any(p.name == "Legacy System" for p in filtered)
    
    def test_apply_filters_closed(self, service, mock_projects):
        """Test filtering by closed state."""
        filtered = service._apply_filters(mock_projects, {"state": "closed"})
        
        # Should only include closed projects
        assert len(filtered) >= 1
        assert all(p.state == "Closed" for p in filtered)
        assert any(p.name == "Legacy System" for p in filtered)
    
    def test_apply_filters_none(self, service, mock_projects):
        """Test no filters returns all projects."""
        filtered = service._apply_filters(mock_projects, None)
        
        assert len(filtered) == len(mock_projects)
    
    def test_rank_by_similarity(self, service, mock_projects):
        """Test ranking by similarity."""
        matches = service._search_by_terms(mock_projects, ["AI"])
        ranked = service._rank_by_similarity(matches, ["AI"])
        
        # Should be sorted by relevance
        assert len(ranked) >= 2
        # Projects with AI in name should rank higher
        assert ranked[0] is not None
    
    def test_format_results_with_projects(self, service, mock_projects):
        """Test formatting results message."""
        message = service._format_results(mock_projects[:2], 2, "Searched for: AI")
        
        assert "Found 2 project(s)" in message
        assert "Delta Platform" in message
        assert "Gen AI" in message
        assert "Searched for: AI" in message
    
    def test_format_results_empty(self, service):
        """Test formatting empty results."""
        message = service._format_results([], 0, "Searched for: XYZ")
        
        assert "No projects found" in message
        assert "Searched for: XYZ" in message
    
    @pytest.mark.asyncio
    async def test_search_with_terms(self, service, mock_projects):
        """Test full search flow with terms."""
        with patch.object(service, '_fetch_all_projects', return_value=mock_projects):
            params = ProjectSearchQuery(
                user_query="Show AI projects",
                search_terms=["AI"],
                filters=None
            )
            response = await service.query_data(params)
            
            assert isinstance(response, ProjectSearchResponse)
            assert len(response.projects) >= 2
            assert response.total_found >= 2
            assert "AI" in response.search_summary
            assert response.message is not None
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, service, mock_projects):
        """Test search with state filter."""
        with patch.object(service, '_fetch_all_projects', return_value=mock_projects):
            params = ProjectSearchQuery(
                user_query="List active projects",
                search_terms=[],
                filters={"state": "active"}
            )
            response = await service.query_data(params)
            
            assert isinstance(response, ProjectSearchResponse)
            # Should exclude closed projects
            assert not any(p.name == "Legacy System" for p in response.projects)
    
    @pytest.mark.asyncio
    async def test_search_all_projects(self, service, mock_projects):
        """Test searching without terms (return all)."""
        with patch.object(service, '_fetch_all_projects', return_value=mock_projects):
            params = ProjectSearchQuery(
                user_query="What projects do we have?",
                search_terms=[],
                filters=None
            )
            response = await service.query_data(params)
            
            assert isinstance(response, ProjectSearchResponse)
            assert len(response.projects) >= 5
            assert "All projects" in response.search_summary
    
    @pytest.mark.asyncio
    async def test_search_no_matches(self, service, mock_projects):
        """Test search with no matching results."""
        with patch.object(service, '_fetch_all_projects', return_value=mock_projects):
            params = ProjectSearchQuery(
                user_query="Find XYZ projects",
                search_terms=["XYZ123"],
                filters=None
            )
            response = await service.query_data(params)
            
            assert isinstance(response, ProjectSearchResponse)
            assert len(response.projects) == 0
            assert response.total_found == 0
            assert "No projects found" in response.message


class TestProjectSearchIntegration:
    """Integration tests requiring real Azure DevOps."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_real_projects(self, service):
        """Test searching real projects from Azure DevOps."""
        params = ProjectSearchQuery(
            user_query="Show all projects",
            search_terms=[],
            filters=None
        )
        
        response = await service.query_data(params)
        
        assert isinstance(response, ProjectSearchResponse)
        assert response.total_found >= 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_extract_and_search(self, extractor, service):
        """Test full extraction and search flow."""
        # Extract parameters
        params = await extractor.extract_params("Show me AI projects")
        
        # Execute search
        response = await service.query_data(params)
        
        assert isinstance(response, ProjectSearchResponse)
        assert response.message is not None

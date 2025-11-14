"""
Service for project selection.
"""

from typing import List, Optional, Dict

from backend.intents.base_intent.service import BaseService
from backend.models.project_models import EpicProject
from backend.agents.memory import get_memory
from .models import ProjectSelectionQuery, ProjectSelectionResponse


class ProjectSelectionService(BaseService[ProjectSelectionQuery, ProjectSelectionResponse]):
    """Service to select specific Epic project from Azure DevOps."""
    
    async def query_data(self, params: ProjectSelectionQuery) -> ProjectSelectionResponse:
        """
        Select a specific project by name.
        
        Args:
            params: Query parameters with project_name
            
        Returns:
            ProjectSelectionResponse with selected project or alternatives
        """
        if not params.project_name:
            return ProjectSelectionResponse(
                selected=False,
                selected_project=None,
                ambiguous_projects=None,
                suggested_projects=None,
                message="Please specify a project name to select."
            )
        
        # Fetch all projects
        all_projects = await self._fetch_all_projects()
        
        # Find matches by name
        matches = self._find_project_by_name(all_projects, params.project_name)
        
        # CASE 1: Single match - auto-select
        if len(matches) == 1:
            selected = matches[0]
            self._update_project_context(selected)
            
            return ProjectSelectionResponse(
                selected=True,
                selected_project=selected,
                ambiguous_projects=None,
                suggested_projects=None,
                message=f"Project '{selected.name}' selected successfully."
            )
        
        # CASE 2: No matches - fallback to search
        if len(matches) == 0:
            suggestions = await self._fallback_to_search(params.project_name)
            
            if suggestions:
                return ProjectSelectionResponse(
                    selected=False,
                    selected_project=None,
                    ambiguous_projects=None,
                    suggested_projects=suggestions,
                    message=f"Project '{params.project_name}' not found. Did you mean one of these?"
                )
            else:
                return ProjectSelectionResponse(
                    selected=False,
                    selected_project=None,
                    ambiguous_projects=None,
                    suggested_projects=None,
                    message=f"Project '{params.project_name}' not found."
                )
        
        # CASE 3: Multiple matches - ask for clarification
        ranked = self._rank_by_similarity(matches, params.project_name)
        
        return ProjectSelectionResponse(
            selected=False,
            selected_project=None,
            ambiguous_projects=ranked,
            suggested_projects=None,
            message=f"Found {len(ranked)} projects matching '{params.project_name}'. Please specify which one."
        )
    
    def _update_project_context(self, project: EpicProject) -> None:
        """Update memory with selected project context."""
        if self.session_id:
            memory = get_memory()
            memory.update_project_context(
                self.session_id,
                project.id,
                project.name,
                epic_id=int(project.id) if project.id else None
            )
    
    async def _fallback_to_search(self, project_name: str) -> Optional[List[EpicProject]]:
        """
        Fallback to search when exact match not found.
        Returns suggested projects based on search.
        
        Args:
            project_name: The project name that wasn't found
            
        Returns:
            List of suggested projects or None
        """
        # Import at method level to avoid circular import
        from backend.intents.project_search.service import ProjectSearchService
        from backend.intents.project_search.models import ProjectSearchQuery
        
        try:
            # Create search service instance
            search_service = ProjectSearchService(
                session_id=self.session_id,
                intent_name="project_search"
            )
            
            # Create search query with project name as search term
            search_query = ProjectSearchQuery(
                user_query=f"Search for {project_name}",
                search_terms=[project_name],
                filters=None,
                project_id=None
            )
            
            # Execute search
            search_response = await search_service.query_data(search_query)
            
            # Return top 5 suggestions
            if search_response.projects:
                return search_response.projects[:5]
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Fallback search failed: {e}")
            return None
    
    async def _fetch_all_projects(self) -> List[EpicProject]:
        """Fetch all Epic work items (projects) from Azure DevOps."""
        project_id = self.azure_config.devops_project_id
        
        # WIQL query to get all Epic work items
        wiql_query = """
        SELECT [System.Id], [System.Title], [System.State], [System.Description]
        FROM workitems
        WHERE [System.WorkItemType] = 'Epic'
        AND [System.TeamProject] = 'HUB GenAI'
        AND [System.AreaPath] = 'HUB GenAI\\Projeto DELTA'
        ORDER BY [System.ChangedDate] DESC
        """
        
        url = self.azure_config.get_devops_url(project_id) + "/_apis/wit/wiql?api-version=7.1"
        
        try:
            response = self.make_request(
                method="POST",
                url=url,
                headers=self.azure_config.get_devops_headers(),
                json={"query": wiql_query}
            )
            
            data = response.json()
            work_item_ids = [item["id"] for item in data.get("workItems", [])]
            
            if not work_item_ids:
                return []
            
            # Get work item details
            work_items = await self._get_work_item_details(project_id, work_item_ids)
            
            # Convert to EpicProject models
            projects = []
            for item in work_items:
                try:
                    project = EpicProject.project_from_workitem(item)
                    projects.append(project)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Failed to parse project {item.get('id')}: {e}")
                    continue
            
            return projects
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to fetch projects: {e}", exc_info=True)
            raise
    
    async def _get_work_item_details(
        self,
        project_id: str,
        work_item_ids: List[int]
    ) -> List[Dict]:
        """Get detailed information for work items."""
        ids_str = ",".join(str(id) for id in work_item_ids[:200])
        url = self.azure_config.get_devops_url(project_id) + f"/_apis/wit/workitems?ids={ids_str}&api-version=7.1"
        
        response = self.make_request(
            method="GET",
            url=url,
            headers=self.azure_config.get_devops_headers()
        )
        
        return response.json().get("value", [])
    
    def _find_project_by_name(self, projects: List[EpicProject], project_name: str) -> List[EpicProject]:
        """
        Find projects matching the given name.
        Priority: exact match > starts with > contains
        """
        name_lower = project_name.lower()
        matches = []
        
        for project in projects:
            proj_name_lower = project.name.lower() if project.name else ""
            
            if name_lower in proj_name_lower:
                matches.append(project)
        
        return matches
    
    def _rank_by_similarity(
        self,
        projects: List[EpicProject],
        search_term: str
    ) -> List[EpicProject]:
        """
        Rank projects by relevance to search term (name matching only).
        
        Scoring:
        - 100: Exact match (case-insensitive)
        - 80: Name starts with search term
        - 60: Search term in name
        - 40: Name starts with any word from search term
        """
        term_lower = search_term.lower()
        search_words = term_lower.split()
        
        scored = []
        for project in projects:
            name_lower = project.name.lower() if project.name else ""
            score = 0
            
            # Exact match
            if name_lower == term_lower:
                score = 100
            # Name starts with search term
            elif name_lower.startswith(term_lower):
                score = 80
            # Search term anywhere in name
            elif term_lower in name_lower:
                score = 60
            # Name starts with any word from search term
            elif any(name_lower.startswith(word) for word in search_words if len(word) > 2):
                score = 40
            
            scored.append((project, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored]


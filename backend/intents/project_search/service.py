"""
Service for project search.
"""

from typing import List, Optional, Dict

from backend.intents.base_intent.service import BaseService
from backend.models.project_models import EpicProject
from .models import ProjectSearchQuery, ProjectSearchResponse


class ProjectSearchService(BaseService[ProjectSearchQuery, ProjectSearchResponse]):
    """Service to search and discover Epic projects from Azure DevOps."""
    
    def _build_wiql_query(self, params: ProjectSearchQuery) -> str:
        return f"""
        SELECT [System.Id], [System.Title], [System.State], [System.Description]
        FROM workitems
        WHERE [System.WorkItemType] = 'Epic'
        AND [System.TeamProject] = 'HUB GenAI'
        AND [System.AreaPath] = 'HUB GenAI\\Projeto DELTA'
        {f"AND [System.State] = '{params.state}'" if params.state is not None else ""}
        ORDER BY [System.ChangedDate] DESC
        """

    async def query_data(self, params: ProjectSearchQuery) -> ProjectSearchResponse:
        """
        Search for projects using keywords and filters.
        
        Args:
            params: Query parameters with search_terms and filters
            
        Returns:
            ProjectSearchResponse with matching projects
        """
        # Fetch all projects
        all_projects = await self._fetch_all_projects(params)
        
        # Apply filters if specified
        filtered_projects = self._apply_filters(all_projects, params.filters)
        
        # Search by terms if provided
        if params.search_terms:
            matches = self._search_by_terms(filtered_projects, params.search_terms)
            ranked = self._rank_by_similarity(matches, params.search_terms)
            search_summary = f"Searched for: {', '.join(params.search_terms)}"
        else:
            # No search terms - return all filtered projects
            ranked = filtered_projects
            search_summary = "All projects"
        
        # Limit to top results
        top_results = ranked[:10]
        
        # Format message
        message = self._format_results(top_results, len(ranked), search_summary)
        
        return ProjectSearchResponse(
            projects=top_results,
            total_found=len(ranked),
            search_summary=search_summary,
            message=message
        )
    
    async def _fetch_all_projects(self, params: ProjectSearchQuery) -> List[EpicProject]:
        """Fetch all Epic work items (projects) from Azure DevOps."""
        project_id = self.azure_config.devops_project_id
        
        # WIQL query to get all Epic work items
        wiql_query = self._build_wiql_query(params)
        
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
    
    def _apply_filters(
        self,
        projects: List[EpicProject],
        filters: Optional[Dict[str, str]]
    ) -> List[EpicProject]:
        """Apply state/status filters to project list."""
        if not filters:
            return projects
        
        filtered = projects
        
        # Filter by state if specified
        if "state" in filters:
            state_filter = filters["state"].lower()
            if state_filter in ["active", "closed"]:
                filtered = [
                    p for p in filtered
                    if p.state and p.state.lower() == state_filter
                ]
        
        return filtered
    
    def _search_by_terms(
        self,
        projects: List[EpicProject],
        search_terms: List[str]
    ) -> List[EpicProject]:
        """
        Search projects by keywords in name and description.
        Returns projects matching any search term.
        """
        if not search_terms:
            return projects
        
        terms_lower = [term.lower() for term in search_terms]
        matches = []
        
        for project in projects:
            name_lower = project.name.lower() if project.name else ""
            desc_lower = project.description.lower() if project.description else ""
            
            # Check if any search term appears in name or description
            for term in terms_lower:
                if term in name_lower or term in desc_lower:
                    matches.append(project)
                    break  # Only add once per project
        
        return matches
    
    def _rank_by_similarity(
        self,
        projects: List[EpicProject],
        search_terms: List[str]
    ) -> List[EpicProject]:
        """
        Rank projects by relevance to search terms.
        
        Scoring:
        - 100: Exact match in name
        - 80: Name starts with term
        - 60: Term in name
        - 40: Term in description
        - 20: Partial word match
        """
        if not search_terms:
            return projects
        
        terms_lower = [term.lower() for term in search_terms]
        scored = []
        
        for project in projects:
            name_lower = project.name.lower() if project.name else ""
            desc_lower = project.description.lower() if project.description else ""
            max_score = 0
            
            for term in terms_lower:
                score = 0
                
                # Name exact match
                if name_lower == term:
                    score = 100
                # Name starts with term
                elif name_lower.startswith(term):
                    score = 80
                # Term in name
                elif term in name_lower:
                    score = 60
                # Term in description
                elif term in desc_lower:
                    score = 40
                # Partial word match
                else:
                    words = name_lower.split()
                    if any(word.startswith(term) or term in word for word in words):
                        score = 20
                
                max_score = max(max_score, score)
            
            scored.append((project, max_score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored]
    
    def _format_results(
        self,
        projects: List[EpicProject],
        total_found: int,
        search_summary: str
    ) -> str:
        """Format search results for presentation."""
        if not projects:
            return f"No projects found matching your search.\n\n{search_summary}"
        
        lines = [f"Found {total_found} project(s). Showing top {len(projects)}:\n"]
        
        for idx, project in enumerate(projects, 1):
            state_emoji = "🟢" if project.state == "Active" else "🔴"
            lines.append(f"{idx}. {state_emoji} {project.name}")
            if project.description:
                # Truncate long descriptions
                desc = project.description[:100]
                if len(project.description) > 100:
                    desc += "..."
                lines.append(f"   {desc}")
        
        lines.append(f"\n{search_summary}")
        
        return "\n".join(lines)

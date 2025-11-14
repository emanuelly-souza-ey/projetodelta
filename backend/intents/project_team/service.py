"""
Service for querying project team members from Azure DevOps.
"""

from typing import List, Dict, Any

from backend.intents.base_intent import BaseService
from backend.intents.project_search.models import ProjectSearchQuery
from .models import ProjectTeamQuery, ProjectTeamResponse, TeamMember


class ProjectTeamService(BaseService[ProjectTeamQuery, ProjectTeamResponse]):
    """Service to query project team members from Azure DevOps API."""
    

    async def query_data(self, params: ProjectTeamQuery) -> ProjectTeamResponse:
        """
        Query team members from Azure DevOps.
        
        Args:
            params: Extracted query parameters
            
        Returns:
            ProjectTeamResponse with team members data
        """
        # Defensive: convert dict to model if needed
        if isinstance(params, dict):
            params = ProjectTeamQuery(**params)
        
        # Check if we have Epic context from session memory
        from backend.agents.memory import get_memory
        memory = get_memory()
        context = memory.get_context(self.session_id)
        project_context = context.get("project_context", {})
        
        epic_id = project_context.get("epic_id")
        
    
        # Import at method level to avoid circular import
        from backend.intents.get_tasks.service import GetTasksService
        from backend.intents.get_tasks.models import GetTasksQuery, GetTasksResponse
        
        try:
            # Create search service instance
            search_service = GetTasksService(
                session_id=self.session_id,
            )
            
            # Create search query - Epic context is automatically handled by GetTasksService
            # from session memory, so we don't need to pass epic_id here
            search_query = GetTasksQuery(
                user_query=None,
                person_name=None,
                task_state=None,
                task_type=None,
                start_date=None,
                end_date=None
            )
            
            # Execute search - will use Epic context if available in session
            search_response = await search_service.query_data(search_query)
            
            # Extract unique team members from tasks
            team_members_dict = {}
            if search_response and search_response.tasks:
                for task in search_response.tasks:
                    if task.assigned_to and task.assigned_to.strip():
                        # Use assigned_to as key to avoid duplicates
                        assigned_name = task.assigned_to.strip()
                        if assigned_name not in team_members_dict:
                            team_members_dict[assigned_name] = TeamMember(
                                id=None,  # Not available in task data
                                name=assigned_name,
                                email=None,  # Not available in task data
                                role=None     # Not available in task data
                            )
            
            members = list(team_members_dict.values())
            return ProjectTeamResponse(
                members=members,
                total_count=len(members),
                message="Os integrantes do projeto são: " + ", ".join([member.name for member in members])
            )
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to query team from epic tasks: {e}")
            return ProjectTeamResponse(
                members=[],
                total_count=0,
                message="Não foi possível recuperar os integrantes do projeto."
            )


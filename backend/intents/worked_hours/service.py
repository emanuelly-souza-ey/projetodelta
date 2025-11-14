"""
Service for querying worked hours from Azure DevOps.
"""

from typing import List, Dict, Any

from backend.intents.base_intent import BaseService
from .models import WorkedHoursQuery, WorkedHoursResponse, HourBreakdown


class WorkedHoursService(BaseService[WorkedHoursQuery, WorkedHoursResponse]):
    """Service to query worked hours from Azure DevOps API."""
    
    async def query_data(self, params: WorkedHoursQuery) -> WorkedHoursResponse:
        """
        Query worked hours from Azure DevOps.
        
        Args:
            params: Extracted query parameters
            
        Returns:
            WorkedHoursResponse with hours data
        """
        # Defensive: convert dict to model if needed
        if isinstance(params, dict):
            params = WorkedHoursQuery(**params)
        
        # Build WIQL query
        wiql_query = self._build_wiql_query(params)
        
        # Get project ID (use default if not provided)
        project_id = params.project_id or self.azure_config.devops_project_id
        
        # Execute query
        url = self.azure_config.get_devops_url(project_id) + "/_apis/wit/wiql?api-version=7.1"
        
        try:
            # Use base service method with timeout and retry
            response = self.make_request(
                method="POST",
                url=url,
                headers=self.azure_config.get_devops_headers(),
                json={"query": wiql_query}
            )
            
            data = response.json()
            work_item_ids = [item["id"] for item in data.get("workItems", [])]
            
            if not work_item_ids:
                return WorkedHoursResponse(
                    person=params.person_name,
                    total_hours=0.0,
                    start_date=params.start_date or "",
                    end_date=params.end_date or "",
                    breakdown=[]
                )
            
            # Get work item details
            work_items = await self._get_work_item_details(project_id, work_item_ids)
            
            # Calculate totals and create breakdown
            return self._process_work_items(work_items, params)
            
        except Exception as e:
            # Error already handled by base service with detailed message
            raise
    
    def _build_wiql_query(self, params: WorkedHoursQuery) -> str:
        """Build WIQL query based on parameters."""
        conditions = []
        
        # Always filter by project
        conditions.append("[System.TeamProject] = 'Generative AI'")
        
        # Filter by assigned person if specified
        if params.person_name:
            conditions.append(f"[System.AssignedTo] CONTAINS '{params.person_name}'")
        
        # Filter by date range if specified
        if params.start_date:
            conditions.append(f"[System.ChangedDate] >= '{params.start_date}'")
        
        if params.end_date:
            conditions.append(f"[System.ChangedDate] <= '{params.end_date}'")
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
        SELECT
            [System.Id],
            [System.Title],
            [System.State],
            [System.AssignedTo],
            [Microsoft.VSTS.Scheduling.CompletedWork],
            [System.ChangedDate]
        FROM workitems
        WHERE {where_clause}
        AND [System.AreaPath] = 'HUB GenAI\\Projeto DELTA'
        ORDER BY [System.ChangedDate] DESC
        """
        
        return query
    
    async def _get_work_item_details(
        self,
        project_id: str,
        work_item_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """Get detailed information for work items."""
        # Batch request for work items
        ids_str = ",".join(str(id) for id in work_item_ids[:200])  # Limit to 200
        url = self.azure_config.get_devops_url(project_id) + f"/_apis/wit/workitems?ids={ids_str}&api-version=7.1"
        
        # Use base service method with timeout and retry
        response = self.make_request(
            method="GET",
            url=url,
            headers=self.azure_config.get_devops_headers()
        )
        
        return response.json().get("value", [])
    
    def _process_work_items(
        self,
        work_items: List[Dict[str, Any]],
        params: WorkedHoursQuery
    ) -> WorkedHoursResponse:
        """Process work items to calculate hours and create breakdown."""
        total_hours = 0.0
        breakdown = []
        
        for item in work_items:
            fields = item.get("fields", {})
            
            # Get completed work hours
            hours = fields.get("Microsoft.VSTS.Scheduling.CompletedWork", 0.0) or 0.0
            total_hours += hours
            
            # Add to breakdown
            if hours > 0:
                breakdown.append(HourBreakdown(
                    date=fields.get("System.ChangedDate", "")[:10],  # Get date only
                    task_title=fields.get("System.Title", "Untitled"),
                    hours=hours,
                    state=fields.get("System.State")
                ))
        
        return WorkedHoursResponse(
            person=params.person_name,
            total_hours=total_hours,
            start_date=params.start_date or "",
            end_date=params.end_date or "",
            breakdown=breakdown
        )

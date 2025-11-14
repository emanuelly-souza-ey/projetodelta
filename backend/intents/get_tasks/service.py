"""
Service for querying tasks from Azure DevOps.
"""

from typing import List, Dict, Any

from backend.intents.base_intent import BaseService
from .models import GetTasksQuery, GetTasksResponse, TaskItem


class GetTasksService(BaseService[GetTasksQuery, GetTasksResponse]):
    """Service to query tasks from Azure DevOps API."""
    
    async def query_data(self, params: GetTasksQuery) -> GetTasksResponse:
        """
        Query tasks from Azure DevOps.
        
        Args:
            params: Extracted query parameters
            
        Returns:
            GetTasksResponse with tasks data
        """
        # Build WIQL query
        wiql_query = self._build_wiql_query(params)
        
        project_id = self.azure_config.devops_project_id
        
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
            
            # Handle both simple and hierarchical query responses
            work_item_ids = []
            relations = data.get("workItemRelations", [])
            
            if relations:
                # Hierarchical query response (Epic → Tasks structure)
                work_item_ids_set = set()
                for relation in relations:
                    source = relation.get("source")
                    target = relation.get("target") 
                    if source and source.get("id"):
                        work_item_ids_set.add(source.get("id"))
                    if target and target.get("id"):
                        work_item_ids_set.add(target.get("id"))
                work_item_ids = list(work_item_ids_set)
            else:
                # Simple query response (direct work items)
                work_item_ids = [item["id"] for item in data.get("workItems", [])]
            
            if not work_item_ids:
                return GetTasksResponse(
                    tasks=[],
                    total_count=0,
                    tasks_by_person={},
                    task_count_by_person={},
                    filtered_by=self._build_filter_summary(params),
                    message="Nenhuma tarefa encontrada com os critérios especificados.",
                    hierarchy=None,
                    scope="all"
                )
            
            # Get work item details
            work_items = await self._get_work_item_details(project_id, work_item_ids)
            
            # Process and filter work items
            return self._process_work_items(work_items, params)
            
        except Exception as e:
            # Error already handled by base service with detailed message
            raise
    
    def _build_wiql_query(self, params: GetTasksQuery) -> str:
        """
        Build WIQL query based on parameters.
        
        Two modes:
        1. No Epic selected: Query all tasks in DELTA area
        2. Epic selected: Query only tasks under that Epic (hierarchical)
        
        Args:
            params: Query parameters
            
        Returns:
            WIQL query string
        """
        # Check if we have Epic context from session memory
        from backend.agents.memory import get_memory
        memory = get_memory()
        context = memory.get_context(self.session_id)
        project_context = context.get("project_context", {})
        
        epic_id = project_context.get("epic_id")
        
        # Mode 1: No Epic selected - query all DELTA
        if not epic_id:
            return self._build_all_delta_query(params)
        
        # Mode 2: Epic selected - query specific Epic hierarchy
        return self._build_epic_hierarchy_query(params, epic_id)
    
    def _build_all_delta_query(self, params: GetTasksQuery) -> str:
        """
        Build query to get all tasks from Projeto DELTA area (no Epic filter).
        
        Args:
            params: Query parameters
            
        Returns:
            WIQL query string
        """
        # Build optional filters
        person_filter = f"AND [System.AssignedTo] CONTAINS '{params.person_name}'" if params.person_name else ""
        state_filter = f"AND [System.State] = '{params.task_state}'" if params.task_state else ""
        
        query = f"""SELECT
    [System.Id],
    [System.WorkItemType],
    [System.Title],
    [System.State],
    [System.AssignedTo],
    [Microsoft.VSTS.Scheduling.RemainingWork],
    [System.IterationPath],
    [System.AreaPath],
    [Microsoft.VSTS.Common.StackRank]
FROM WorkItems
WHERE
    [System.WorkItemType] = 'Task'
    AND [System.AreaPath] = 'HUB GenAI\\\\Projeto DELTA'
    {person_filter}
    {state_filter}
ORDER BY [Microsoft.VSTS.Common.StackRank] ASC, [System.Id] ASC"""
        
        return query
    
    def _build_epic_hierarchy_query(self, params: GetTasksQuery, epic_id: int) -> str:
        """
        Build hierarchical query to get tasks under specific Epic.
        Uses workitemLinks to traverse Epic → Feature → User Story → Task hierarchy.
        
        Args:
            params: Query parameters
            epic_id: Epic work item ID
            
        Returns:
            Hierarchical WIQL query string
        """
        # Build optional filters
        person_filter = ""
        if params.person_name:
            person_filter = f"AND [Target].[System.AssignedTo] CONTAINS '{params.person_name}'"
        
        state_filter = ""
        if params.task_state:
            state_filter = f"AND [Target].[System.State] = '{params.task_state}'"
        
        query = f"""SELECT
    [System.Id],
    [System.WorkItemType],
    [System.Title],
    [System.State],
    [System.AssignedTo],
    [Microsoft.VSTS.Scheduling.RemainingWork],
    [System.AreaPath],
    [System.IterationPath]
FROM workitemLinks
WHERE
    [Source].[System.Id] = {epic_id}
    AND [System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward'
    AND [Target].[System.WorkItemType] IN ('Task', 'Bug', 'User Story', 'Feature')
    AND [Target].[System.AreaPath] = 'HUB GenAI\\\\Projeto DELTA'
    {person_filter}
    {state_filter}
ORDER BY [System.Id] ASC
MODE (Recursive)"""
        
        return query
    
    def _build_filter_summary(self, params: GetTasksQuery) -> dict:
        """
        Build summary of applied filters.
        
        Args:
            params: Query parameters
            
        Returns:
            Dictionary with filter summary
        """
        return {
            "person": params.person_name,
            "state": params.task_state,
            "type": params.task_type,
            "date_range": None  # Dates not implemented yet
        }
    
    async def _get_work_item_details(
        self,
        project_id: str,
        work_item_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Get detailed information for work items.
        
        Args:
            project_id: Azure DevOps project ID
            work_item_ids: List of work item IDs
            
        Returns:
            List of work item details
        """
        # Batch request for work items (limit to 200 for API constraints)
        ids_str = ",".join(str(id) for id in work_item_ids[:200])
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
        params: GetTasksQuery
    ) -> GetTasksResponse:
        """
        Process work items using existing WorkItem model and filter to return only Tasks.
        Builds hierarchy structure when Epic is selected.
        
        Args:
            work_items: Raw work item data from Azure DevOps
            params: Original query parameters
            
        Returns:
            Processed GetTasksResponse with flat list and optional hierarchy
        """
        from backend.models.devops_models import WorkItem
        from backend.agents.memory import get_memory
        from .models import EpicHierarchy
        
        memory = get_memory()
        context = memory.get_context(self.session_id or "")
        project_context = context.get("project_context", {})
        epic_id = project_context.get("epic_id")
        
        # Determine scope
        scope = "epic" if epic_id else "all"
        
        tasks = []
        epic_info = None
        
        for item in work_items:
            # Use existing WorkItem model for data transformation
            work_item = WorkItem.from_json(item)
            
            fields = item.get("fields", {})
            work_item_type = fields.get("System.WorkItemType")
            
            # Store Epic info when in epic mode
            if work_item_type == "Epic" and epic_id and work_item.id == epic_id:
                epic_info = {
                    "id": work_item.id or 0,
                    "title": work_item.title or "Untitled",
                    "state": work_item.state or "Unknown"
                }
            
            # Collect only Tasks
            if work_item_type == "Task":
                # Convert WorkItem to TaskItem for response
                assigned_to_display = None
                if work_item.assignedTo:
                    assigned_to_display = work_item.assignedTo.displayName
                
                task = TaskItem(
                    id=work_item.id or 0,
                    title=work_item.title or "Untitled",
                    state=work_item.state or "Unknown", 
                    assigned_to=assigned_to_display,
                    work_item_type=work_item_type,
                    created_date=fields.get("System.CreatedDate", "")[:10] if fields.get("System.CreatedDate") else "",
                    changed_date=fields.get("System.ChangedDate", "")[:10] if fields.get("System.ChangedDate") else "",
                    description=fields.get("System.Description", "")
                )
                tasks.append(task)
        
        # Generate Portuguese message
        if len(tasks) == 0:
            message = "Nenhuma tarefa encontrada com os critérios especificados."
        elif len(tasks) == 1:
            message = "Encontrada 1 tarefa"
        else:
            message = f"Encontradas {len(tasks)} tarefas"
            
        # Add scope context
        if scope == "all":
            message += " em todos os projetos do DELTA."
        else:
            epic_name = project_context.get("project_name", "projeto")
            message += f" do {epic_name}."
        
        # Add filter info to message if filters were applied
        if params.person_name:
            message += f" Filtrado por pessoa: {params.person_name}."
        if params.task_state:
            message += f" Estado: {params.task_state}."
        
        # Group tasks by person (person_name: [task_titles])
        tasks_by_person = {}
        task_count_by_person = {}
        
        for task in tasks:
            person = task.assigned_to or "Não atribuído"
            if person not in tasks_by_person:
                tasks_by_person[person] = []
                task_count_by_person[person] = 0
            tasks_by_person[person].append(task.title)
            task_count_by_person[person] += 1
        
        # Build hierarchy if Epic selected
        hierarchy = None
        if scope == "epic" and epic_info:
            hierarchy = [EpicHierarchy(
                epic_id=epic_info["id"],
                epic_title=epic_info["title"],
                epic_state=epic_info["state"],
                tasks=tasks
            )]
        
        return GetTasksResponse(
            tasks=tasks,
            total_count=len(tasks),
            tasks_by_person=tasks_by_person,
            task_count_by_person=task_count_by_person,
            filtered_by=self._build_filter_summary(params),
            message=message,
            hierarchy=hierarchy,
            scope=scope
        )
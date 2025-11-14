"""
Parameter extractor for get_tasks intent.
Uses LLM to extract task query parameters from user input.
"""

from typing import Optional, Dict

from backend.intents.base_intent.extractor import BaseExtractor
from .models import GetTasksQuery


class GetTasksExtractor(BaseExtractor[GetTasksQuery]):
    """Extracts parameters for task queries."""
    
    EXTRACTION_PROMPT = """You are a parameter extraction assistant for Azure DevOps task queries.
        Extract relevant parameters from the user's request for getting tasks/work items.

        Context from previous conversation:
        {context}

        Rules:
        1. user_query: Preserve the exact user input
        2. person_name: Extract person name if mentioned (can be partial name) if there is only one mentioned person
        3. task_state: Extract state filter (Active, Completed, In Progress, New, etc.)
        4. task_type: Extract work item type (Task, Bug, User Story, Feature, Epic, etc.)
        5. start_date/end_date: Extract date ranges if mentioned (format: YYYY-MM-DD)
        6. tags: Extract tags if mentioned (comma-separated, e.g., "urgent,backend")

        Examples:
        - "minhas tarefas ativas" → person_name: null, task_state: "Active"
        - "tasks do João em progresso" → person_name: "João", task_state: "In Progress"
        - "bugs atribuídos para Maria" → person_name: "Maria", task_type: "Bug"
        - "user stories completadas esta semana" → task_type: "User Story", task_state: "Completed"
        - "tarefas com tag urgent" → tags: "urgent"
        - "tasks tagged com backend e frontend" → tags: "backend,frontend"

        User query: {query}
        """

    async def extract_params(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> GetTasksQuery:
        """
        Extract task query parameters from user input.
        
        Args:
            query: User query string
            context: Optional conversation context
            
        Returns:
            GetTasksQuery with extracted parameters
        """
        if self.logger:
            self.logger.info(f"Extracting task parameters from query: {query}")
        
        # Format context for LLM
        context_str = "No previous context"
        if context and context.get("last_params"):
            context_str = f"Previous query parameters: {context['last_params']}"
            if self.logger:
                self.logger.info(f"Using conversation context: {context.get('last_query', 'N/A')}"[:150])
        
        # Create extraction prompt
        prompt = self.EXTRACTION_PROMPT.format(
            context=context_str,
            query=query
        )
        
        if self.logger:
            self.logger.info("Calling LLM for parameter extraction...")
        
        try:
            # Use instructor to extract structured parameters
            from typing import cast
            params = cast(
                GetTasksQuery,
                self.azure_config.create_chat_completion(
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a parameter extraction assistant for Azure DevOps task queries. Extract information accurately."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_model=GetTasksQuery,
                    temperature=0.1,  # Low temperature for consistent extraction
                    max_tokens=500
                )
            )
            
            if self.logger:
                self.logger.info(f"Parameters extracted successfully: {params.model_dump()}")
            
            return params
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in parameter extraction: {str(e)}")
            
            # Fallback to basic extraction
            return GetTasksQuery(
                user_query=query,
                person_name=None,
                task_state=None,
                task_type=None,
                start_date=None,
                end_date=None,
                project_id=None
            )
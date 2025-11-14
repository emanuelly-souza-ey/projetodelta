"""
Parameter extractor for project selection intent.
Uses LLM to extract specific project name from user query.
"""

from typing import Optional, Dict, cast

from backend.intents.base_intent.extractor import BaseExtractor
from .models import ProjectSelectionQuery


class ProjectSelectionExtractor(BaseExtractor[ProjectSelectionQuery]):
    """Extracts specific project name for selection."""
    
    EXTRACTION_PROMPT = """You are a parameter extraction assistant for project selection.
        Extract the specific project name the user wants to select.

        Context from previous conversation:
        {context}

        Rules:
        1. user_query: Preserve the exact user input
        2. project_name: Extract the specific project name mentioned
           - Can be partial (e.g., "Delta" from "Delta Platform")
           - Can be exact name
           - Focus on the project identifier the user mentions

        Examples:
        - "Select Delta project" → project_name: "Delta"
        - "I want to work on Gen AI" → project_name: "Gen AI"
        - "Choose project number 3" → project_name: "3"

        User query: {query}
        """

    async def extract_params(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> ProjectSelectionQuery:
        """
        Extract project name from query using LLM.
        
        Args:
            query: User query
            context: Optional conversation context
            
        Returns:
            ProjectSelectionQuery with user_query and project_name
        """
        if self.logger:
            self.logger.info(f"Extracting project name from query: {query}")
        
        # Format context
        context_str = "No previous context"
        if context:
            context_str = f"Previous conversation context: {context}"
            if self.logger:
                self.logger.info(f"Using conversation context: {context}"[:150])
        
        prompt = self.EXTRACTION_PROMPT.format(
            context=context_str,
            query=query
        )
        
        if self.logger:
            self.logger.info("Calling LLM for parameter extraction...")
        
        # Use instructor to extract structured parameters
        params = cast(
            ProjectSelectionQuery,
            self.azure_config.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a parameter extraction assistant. Extract information accurately."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_model=ProjectSelectionQuery,
                temperature=0.1,
                max_tokens=500
            )
        )
        
        if self.logger:
            self.logger.info(f"Parameters extracted successfully: {params.model_dump()}")
        
        return params

"""
Parameter extractor for project search intent.
Uses LLM to extract search terms and filters from user query.
"""

from typing import Optional, Dict, cast

from backend.intents.base_intent.extractor import BaseExtractor
from .models import ProjectSearchQuery


class ProjectSearchExtractor(BaseExtractor[ProjectSearchQuery]):
    """Extracts search terms and filters for project discovery."""
    
    EXTRACTION_PROMPT = """You are a parameter extraction assistant for project search.
        Extract search terms and filters from the user's exploratory query.

        Context from previous conversation:
        {context}

        Rules:
        1. user_query: Preserve the exact user input
        2. search_terms: Extract ONLY meaningful business/technical keywords
           - Include: technology names, domains, business terms, project identifiers
           - EXCLUDE: generic words like "projects", "projetos", "show", "list", "find"
           - Extract only terms that help filter/identify specific projects
           - Return empty list [] if no specific search terms are found
        3. filters: Extract any state/status filters if mentioned
           - Example: {{"state": "active"}} or {{"state": "closed"}}
           - Only include if explicitly mentioned

        Examples:
        - "Show me AI projects" → search_terms: ["AI"]
        - "What projects use Python and ML?" → search_terms: ["Python", "ML"]
        - "List active projects" → search_terms: [], filters: {{"state": "active"}}
        - "Find closed Delta projects" → search_terms: ["Delta"], filters: {{"state": "closed"}}
        - "Mostre os projetos" → search_terms: []
        - "Listar projetos ativos" → search_terms: [], filters: {{"state": "active"}}
        - "Projetos com IA" → search_terms: ["IA"]

        User query: {query}
        """

    async def extract_params(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> ProjectSearchQuery:
        """
        Extract search parameters from query using LLM.
        
        Args:
            query: User query
            context: Optional conversation context
            
        Returns:
            ProjectSearchQuery with user_query, search_terms, and filters
        """
        if self.logger:
            self.logger.info(f"Extracting search parameters from query: {query}")
        
        # Format context
        context_str = "No previous context"
        if context:
            context_str = f"Previous conversation context: {context}"
            if self.logger:
                self.logger.info(f"Using conversation context: {context}")
        
        prompt = self.EXTRACTION_PROMPT.format(
            context=context_str,
            query=query
        )
        
        if self.logger:
            self.logger.info("Calling LLM for parameter extraction...")
        
        # Use instructor to extract structured parameters
        params = cast(
            ProjectSearchQuery,
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
                response_model=ProjectSearchQuery
            )
        )
        
        if self.logger:
            self.logger.info(f"Extracted parameters: {params.model_dump()}")
        
        return params

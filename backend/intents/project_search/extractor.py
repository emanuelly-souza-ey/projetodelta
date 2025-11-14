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
           - EXCLUDE classifying word like epic or epics, is a synonimous for project 
           - Extract only terms that help filter/identify specific projects
           - Return empty list [] if no specific search terms are found
        3. state: OPTIONAL - Project state mapping (extract ONLY if explicitly mentioned):
           - "Active": projetos ativos, em andamento, ativos, em execução
           - "Closed": projetos concluídos, finalizados, fechados, terminados
           - "New": backlog, novos, planejados, em planejamento
           - If NO state is mentioned, return null/None
        4. filters: Extract any additional filters (tags, etc.) if mentioned

        Examples:
        - "Show me AI projects" → search_terms: ["AI"], state: null
        - "What projects use Python and ML?" → search_terms: ["Python", "ML"], state: null
        - "List active projects" → search_terms: [], state: "Active"
        - "Find closed Delta projects" → search_terms: ["Delta"], state: "Closed"
        - "Mostre os projetos" → search_terms: [], state: null
        - "Listar projetos ativos" → search_terms: [], state: "Active"
        - "Projetos concluídos" → search_terms: [], state: "Closed"
        - "Projetos no backlog" → search_terms: [], state: "New"
        - "Projetos com IA" → search_terms: ["IA"], state: null

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
                self.logger.info(f"Using conversation context: {context}"[:150])
        
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

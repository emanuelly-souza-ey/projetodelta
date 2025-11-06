"""
Parameter extractor for worked hours intent.
Uses LLM to extract structured parameters from natural language.
"""

from typing import Optional, Dict, cast
from datetime import datetime

from backend.intents.base_intent import BaseExtractor
from .models import WorkedHoursQuery


class WorkedHoursExtractor(BaseExtractor[WorkedHoursQuery]):
    """Extracts parameters for worked hours queries using LLM."""
    
    EXTRACTION_PROMPT = """You are a parameter extraction assistant for Azure DevOps queries.
        Extract the following information from the user's query:
        - person_name: Name of the person/team member (if mentioned)
        - start_date: Start date (convert relative dates like "this week", "last month" to ISO format)
        - end_date: End date (convert relative dates to ISO format)

        Current date for reference: {current_date}

        Context from previous conversation:
        {context}

        Rules:
        1. If dates are relative (e.g., "this week", "last month"), calculate actual dates
        2. If only a period is mentioned (e.g., "this week"), infer both start and end dates
        3. If person was mentioned in previous context and not in current query, reuse it
        4. Return None for fields that cannot be determined
        5. DO NOT extract project information - it comes from conversation context

        User query: {query}
        """

    async def extract_params(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> WorkedHoursQuery:
        """
        Extract parameters from query using context.
        
        Args:
            query: User query
            context: Previous conversation context
            
        Returns:
            WorkedHoursQuery with extracted parameters
        """
        if self.logger:
            self.logger.info(f"Extracting worked hours parameters from query: {query}")
        
        # Format context
        context_str = "No previous context"
        if context and context.get("last_params"):
            context_str = f"Previous query parameters: {context['last_params']}"
            if self.logger:
                self.logger.info(f"Using conversation context: {context.get('last_query', 'N/A')}")
        
        # Current date for relative date calculation
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        prompt = self.EXTRACTION_PROMPT.format(
            current_date=current_date,
            context=context_str,
            query=query
        )
        
        if self.logger:
            self.logger.info("Calling LLM for parameter extraction...")
        
        # Use instructor to extract structured parameters
        # When response_model is provided, instructor returns the model instance
        params = cast(
            WorkedHoursQuery,
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
                response_model=WorkedHoursQuery,
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=500
            )
        )
        
        if self.logger:
            self.logger.info(f"Parameters extracted successfully: {params.model_dump()}")
        
        return params

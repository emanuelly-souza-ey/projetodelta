"""
Default Intent Handler.
Handles queries that are NOT related to Azure DevOps.
"""

from typing import Dict, Optional

from backend.intents.base_intent import BaseExtractor, BaseService, BaseIntentHandler


class DefaultExtractor(BaseExtractor):
    """Placeholder extractor for non-DevOps queries."""
    
    async def extract_params(self, query: str, context: Optional[Dict] = None) -> Dict:
        """No parameter extraction needed."""
        return {"query": query}


class DefaultService(BaseService):
    """Service that returns specialized message for non-DevOps queries."""
    
    async def query_data(self, params: Dict) -> Dict:
        """Return specialized message for non-DevOps queries."""
        return {
            "message": "Desculpe, sou um assistente especializado em Azure DevOps. " 
                      "Não estou treinado para responder perguntas sobre outros assuntos. "
                      "Como posso ajudá-lo com suas consultas do Azure DevOps?"
        }


def create_default_handler():
    """Factory function to create default intent handler."""
    return BaseIntentHandler(
        extractor=DefaultExtractor(),
        service=DefaultService()
    )

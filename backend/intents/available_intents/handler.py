"""
Default Intent Handler.
Handles queries that are NOT related to Azure DevOps.
"""

from typing import Dict, Optional

from backend.intents.base_intent import BaseExtractor, BaseService, BaseIntentHandler

class AvailableActionsExtractor(BaseExtractor):
    """Extractor for queries about available actions."""

    async def extract_params(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Extract parameters from user query.
        Args:
            query: User's input text
            context: Optional conversation context
        Returns:
            Dict with extracted parameters (if any)
        """
        return {"query": query}


class AvailableActionsService(BaseService):
    """Service that provides a list of available actions."""

    async def query_data(self, params: Dict) -> Dict:
        """
        Return dynamic list of implemented intents.
        Args:
            params: Parameters from extractor
        Returns:
            Dict with response data including direct message
        """
        from backend.intents.registry import IntentRegistry
        from backend.intents.not_implemented import create_not_implemented_handler
        
        all_intents = IntentRegistry.get_all()
        
        implemented_intents = {
            category: metadata 
            for category, metadata in all_intents.items()
            if metadata.handler_class != create_not_implemented_handler
        }
        
        intent_list = "\n".join([
            f"📌 **{metadata.name}**: {metadata.description}"
            for metadata in implemented_intents.values()
        ])
        
        return {
            "message": (
                f"🎯 Aqui está o que posso fazer por você:\n\n"
                f"{intent_list}\n\n"
            )
        }

def create_available_actions_handler(session_id: Optional[str] = None, intent_name: Optional[str] = None):
    """Factory function to create handler for available actions intent.
    
    Args:
        session_id: Optional chat session ID for logging
        intent_name: Optional intent name for structured logging
    """
    return BaseIntentHandler(
        extractor=AvailableActionsExtractor(),
        service=AvailableActionsService(),
        session_id=session_id,
        intent_name=intent_name or "available_actions"
    )

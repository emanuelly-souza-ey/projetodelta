"""
Project Deselection Intent Handler.
Clears the currently selected project from the session.
"""

from typing import Dict, Optional

from backend.intents.base_intent import BaseExtractor, BaseService, BaseIntentHandler
from backend.agents.memory import get_memory


class ProjectDeselectionExtractor(BaseExtractor):
    """Extractor for project deselection - no parameters needed."""
    
    async def extract_params(self, query: str, context: Optional[Dict] = None) -> Dict:
        """No parameter extraction needed for deselection."""
        return {}


class ProjectDeselectionService(BaseService):
    """Service that clears the selected project."""
    
    def __init__(self, session_id: Optional[str] = None, intent_name: Optional[str] = None):
        """Initialize service with memory access."""
        self.memory = get_memory()
        self.session_id = session_id
        self.intent_name = intent_name
    
    async def query_data(self, params: Dict) -> Dict:
        """Clear project context and return confirmation message."""
        conversation_id = params.get("conversation_id")
        
        if conversation_id:
            # Clear project context by setting scope to 'all'
            self.memory.update_project_context(
                conversation_id=conversation_id,
                project_id=None,
                project_name=None,
                epic_id=None,
                scope="all"
            )
        
        return {
            "message": "Projeto deselecionado com sucesso. Você agora pode ver informações de todos os projetos ou selecionar um novo projeto.",
            "deselected": True
        }


def create_project_deselection_handler(session_id: Optional[str] = None, intent_name: Optional[str] = None):
    """Factory function to create project deselection intent handler.
    
    Args:
        session_id: Optional chat session ID for logging
        intent_name: Optional intent name for structured logging
    """
    intent_name = intent_name or "project_deselection"
    
    return BaseIntentHandler(
        extractor=ProjectDeselectionExtractor(session_id=session_id, intent_name=intent_name),
        service=ProjectDeselectionService(session_id=session_id, intent_name=intent_name),
        session_id=session_id,
        intent_name=intent_name
    )

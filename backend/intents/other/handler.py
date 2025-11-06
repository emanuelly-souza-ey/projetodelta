"""
Other DevOps Intent Handler.
Handles valid DevOps queries that are not yet implemented.
"""

from typing import Dict, Optional

from backend.intents.base_intent import BaseExtractor, BaseService, BaseIntentHandler


class OtherExtractor(BaseExtractor):
    """Placeholder extractor for not-yet-implemented DevOps queries."""
    
    async def extract_params(self, query: str, context: Optional[Dict] = None) -> Dict:
        """No parameter extraction needed."""
        return {"query": query}


class OtherService(BaseService):
    """Service that returns message for not-yet-implemented DevOps features."""
    
    async def query_data(self, params: Dict) -> Dict:
        """Return message for not-yet-implemented DevOps features."""
        return {
            "message": "Entendo que você está perguntando sobre Azure DevOps, "
                      "mas essa funcionalidade específica ainda não está implementada. "
                      "No momento, posso ajudá-lo com:\n"
                      "- Horas trabalhadas\n"
                      "- Progresso de projetos\n"
                      "- Tarefas atrasadas\n"
                      "- Informações da equipe\n"
                      "- Atividades diárias\n\n"
                      "Essa funcionalidade será adicionada em breve!"
        }


def create_other_handler():
    """Factory function to create other DevOps intent handler."""
    return BaseIntentHandler(
        extractor=OtherExtractor(),
        service=OtherService()
    )

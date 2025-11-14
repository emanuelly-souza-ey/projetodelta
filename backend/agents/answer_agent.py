"""
Answer Agent for generating natural language responses.
Responds in Portuguese based on structured data.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.config import get_azure_config


class AnswerResponse(BaseModel):
    """Structured answer response."""
    answer: str = Field(..., description="Natural language answer in Portuguese")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the answer")


class AnswerAgent:
    """
    Generates natural language responses in Portuguese.
    Takes structured data and creates user-friendly answers.
    """
    
    SYSTEM_PROMPT = """Você é um assistente que gera respostas naturais em português brasileiro.
    
    Suas responsabilidades:
    1. Receber dados estruturados sobre consultas do Azure DevOps, mas não mencione o Azure DevOps
    2. Gerar respostas claras, concisas e naturais em português
    3. Manter um tom profissional mas amigável
    4. Incluir números e detalhes relevantes
    5. Se os dados estiverem vazios ou incompletos, informar educadamente
    6. Responder APENAS a pergunta feita, sem oferecer ajuda adicional ou sugerir outras ações
    
    Sempre responda em português brasileiro, mesmo que a pergunta seja em inglês.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the answer agent using shared Azure config.
        
        Args:
            session_id: Optional session ID for logging and tracking
        """
        self.session_id = session_id
        self.azure_config = get_azure_config()
    
    def generate_response(
        self,
        query: str,
        intent: str,
        data: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate natural language response in Portuguese.
        
        Args:
            query: Original user query
            intent: Classified intent category
            data: Structured data from the handler
            context: Optional conversation context
            
        Returns:
            Natural language answer in Portuguese
        """
        # Build context string if available
        context_str = ""
        if context and context.get("last_query"):
            context_str = f"\nContexto da conversa anterior:\n- Última pergunta: {context['last_query']}\n"
        
        prompt = f"""
        Pergunta do usuário: {query}
        
        Tipo de consulta: {intent}
        {context_str}
        Dados obtidos:
        {self._format_data(data)}
        
        Gere uma resposta natural em português brasileiro para o usuário.
        Se não houver dados ou estiverem vazios, explique isso educadamente.
        """
        
        try:
            # When response_model is provided, instructor returns the Pydantic model directly
            response = self.azure_config.create_chat_completion(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_model=AnswerResponse,
                temperature=0.5,
                max_tokens=1200
            )
            
            # response is AnswerResponse when response_model is provided
            return response.answer  # type: ignore[attr-defined]
            
        except Exception as e:
            # If generation fails, return error message
            return f"Desculpe, não consegui gerar uma resposta adequada. Erro: {str(e)}"
    
    def _format_data(self, data: Dict[str, Any]) -> str:
        """Format data dictionary for prompt."""
        if not data:
            return "Nenhum dado disponível"
        
        lines = []
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                lines.append(f"- {key}: {len(value) if isinstance(value, list) else 'objeto complexo'}")
            else:
                lines.append(f"- {key}: {value}")
        
        return "\n".join(lines)

"""
Router Agent implementation using instructor and langgraph.
Classifies user intents and routes to appropriate specialized agents.
Uses dynamic intent registry and maintains project context.
"""

from typing import Optional
from backend.config import get_azure_config
from backend.config.logging import chat_logger
from backend.agents.memory import get_memory
# Moved import inside functions to avoid circular dependency
from backend.intents.registry import IntentRegistry
from .models import UserIntent, RouterState


class RouterAgent:
    """
    Router agent that classifies user queries and routes them to specialized agents.
    Uses instructor for structured outputs and is designed to work with langgraph.
    Maintains project context awareness for better intent classification.
    """
    
    CLASSIFICATION_PROMPT = """Você é um assistente de classificação de intenções. 
        Analise a consulta do usuário e determine qual categoria melhor representa sua intenção.

        CONTEXTO ATUAL DO PROJETO:
        {project_context}

        MENSAGENS RECENTES DA CONVERSA:
        {recent_messages}

        PRIORIDADE MÁXIMA - Detecção de Mudança de Projeto:
        Se o usuário mencionar explicitamente mudar, selecionar ou trocar de projeto,
        classifique SEMPRE como "project_selection", mesmo que haja outras intenções na consulta.
        
        CONTEXTO DE SELEÇÃO:
        Se o bot acabou de listar projetos e o usuário responde com apenas um número (ex: "1", "2"),
        classifique como "project_selection" pois está selecionando da lista anterior.

        Categorias disponíveis:
        {categories}

        Instruções:
        1. PRIMEIRO: Verifique se é uma mudança explícita de projeto → "project_selection"
        2. SEGUNDO: Verifique contexto recente - se bot listou projetos e usuário diz número → "project_selection"
        3. Se NÃO for mudança de projeto, analise cuidadosamente a consulta
        4. Identifique palavras-chave e o contexto da pergunta
        5. Selecione a categoria que melhor representa a intenção
        6. Se não houver correspondência clara, escolha a categoria mais próxima
        7. Em caso de dúvida, use a categoria "other"
        8. Forneça uma pontuação de confiança honesta (0.0 a 1.0)
        9. Explique brevemente seu raciocínio

        Consulta do usuário: {query}
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the router agent using shared Azure config.
        
        Args:
            session_id: Optional chat session ID for logging
        """
        self.azure_config = get_azure_config()
        self.memory = get_memory()
        self.session_id = session_id
        
        # Use structured component logger for ROUTER
        if session_id:
            self.logger = chat_logger.get_component_logger(
                session_id=session_id,
                component='ROUTER'
            )
        else:
            self.logger = None
        
    def _get_project_context_description(self, conversation_id: Optional[str]) -> str:
        """
        Get current project context as a formatted string for the classification prompt.
        
        Args:
            conversation_id: Conversation ID to retrieve context from
            
        Returns:
            Formatted string describing current project context
        """
        if not conversation_id:
            return "Projeto atual: Nenhum projeto selecionado (usando padrão)"
        
        context = self.memory.get_context(conversation_id)
        project_context = context.get("project_context", {})
        
        if not project_context:
            return "Projeto atual: Nenhum projeto selecionado (usando padrão)"
        
        scope = project_context.get("scope", "default")
        project_name = project_context.get("project_name")
        
        if scope == "specific" and project_name:
            return f"Projeto atual: {project_name}"
        elif scope == "all":
            return "Projeto atual: Consultando TODOS os projetos"
        else:
            return "Projeto atual: Projeto padrão"
    
    def _format_recent_messages(self, conversation_id: Optional[str]) -> str:
        """
        Format recent messages for context.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Formatted string with recent messages
        """
        if not conversation_id:
            return "Nenhuma conversa anterior"
        
        recent_messages = self.memory.get_recent_messages(conversation_id, limit=3)
        
        if not recent_messages:
            return "Nenhuma conversa anterior"
        
        lines = []
        for msg in recent_messages:
            query = msg.get("query", "")
            intent = msg.get("intent", "unknown")
            
            # Show last message content (simplified)
            if query:
                lines.append(f"User: {query}")
                lines.append(f"Intent: {intent}")
        
        return "\n".join(lines) if lines else "Nenhuma conversa anterior"
    
    def classify_intent(self, query: str, conversation_id: Optional[str] = None) -> UserIntent:
        """
        Classify user intent using dynamically registered intents.
        Takes into account current project context for better classification.
        
        Args:
            query: User query to classify
            conversation_id: Optional conversation ID for context retrieval
            
        Returns:
            Classified UserIntent
        """
        if self.logger:
            self.logger.info(f"Classifying intent for query: {query}")
        
        # Get current project context
        project_context_desc = self._get_project_context_description(conversation_id)
        recent_messages_desc = self._format_recent_messages(conversation_id)
        
        if self.logger:
            self.logger.info(f"Current project context: {project_context_desc}")
            self.logger.info(f"Recent messages: {recent_messages_desc}")
        
        # Import here to avoid circular dependency
        from backend.intents import get_intent_descriptions
        categories_text = get_intent_descriptions()
        
        '''if self.logger:
            self.logger.info(f"Available categories for classification: {categories_text}")
        '''        
        prompt = self.CLASSIFICATION_PROMPT.format(
            project_context=project_context_desc,
            recent_messages=recent_messages_desc,
            categories=categories_text,
            query=query
        )
        
        # When response_model is provided, instructor returns the Pydantic model directly
        intent = self.azure_config.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are an intent classification assistant."},
                {"role": "user", "content": prompt}
            ],
            response_model=UserIntent,
            temperature=0.3,
            max_tokens=500
        )
        
        # intent is UserIntent when response_model is provided
        intent.original_query = query  # type: ignore[attr-defined]
        
        if self.logger:
            self.logger.info(
                f"Intent classified: {intent.category} (confidence: {intent.confidence:.2f}) - {intent.reasoning}"  # type: ignore[attr-defined]
            )
        
        return intent  # type: ignore[return-value]
    
    def route_to_agent(self, intent: UserIntent) -> str:
        """Determine which agent should handle the intent using dynamic registry."""
        try:
            intent_metadata = IntentRegistry.get(intent.category)
            return intent_metadata.get_agent_name()
        except ValueError:
            # Fallback to default agent if intent not found in registry
            if self.logger:
                self.logger.warning(
                    f"Intent '{intent.category}' not found in registry, using default handler"
                )
            return "default_agent"
    
    def process_query(self, query: str, conversation_id: Optional[str] = None) -> dict:
        """
        Process a user query: classify and route.
        
        Args:
            query: User query to process
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dictionary with processing results
        """
        try:
            intent = self.classify_intent(query, conversation_id)
            target_agent = self.route_to_agent(intent)
            
            return {
                "success": True,
                "query": query,
                "intent": {
                    "category": intent.category,
                    "confidence": intent.confidence,
                    "reasoning": intent.reasoning
                },
                "route_to": target_agent,
                "error": None
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "query": query,
                "intent": None,
                "route_to": "default_agent",
                "error": str(e)
            }


__all__ = ["RouterAgent"]

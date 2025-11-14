"""
Chat endpoint for conversational AI assistant.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from backend.agents.router_agent import RouterAgent
from backend.agents.answer_agent import AnswerAgent
from backend.agents.memory import get_memory
from backend.intents import get_handler, IntentRegistry


router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message/query")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str = Field(..., description="Natural language response in Portuguese")
    intent: str = Field(..., description="Classified intent category")
    confidence: float = Field(..., description="Classification confidence")
    data: Optional[Dict[str, Any]] = Field(None, description="Structured data for frontend rendering")
    conversation_id: str = Field(..., description="Conversation ID for follow-up queries")
    selected_project: Optional[str] = Field(None, description="Name of currently selected project")
    error: Optional[str] = Field(None, description="Error message if any")


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    
    Process user queries through:
    1. Router Agent - Classify intent
    2. Intent Handler - Extract parameters & query data
    3. Answer Agent - Generate natural language response
    
    Args:
        request: ChatRequest with message and optional conversation_id
        
    Returns:
        ChatResponse with answer, data, and conversation_id
    """
    try:
        session_id = request.conversation_id or "anonymous"
        
        # 1. Classify intent
        router_agent = RouterAgent(session_id=session_id)
        route_result = router_agent.process_query(request.message)
        
        if not route_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Router error: {route_result.get('error', 'Unknown error')}"
            )
        
        intent_category = route_result["intent"]["category"]
        confidence = route_result["intent"]["confidence"]
        
        # 2. Get intent handler
        handler = get_handler(intent_category, session_id=session_id)
        
        # 3. Process query
        handler_result = await handler.handle(
            query=request.message,
            conversation_id=request.conversation_id
        )
        
        if not handler_result.get("data"):
            handler_result["data"] = {}
        
        # 4. Check if intent requires LLM processing
        intent_metadata = IntentRegistry.get(intent_category)
        
        if intent_metadata.requires_llm:
            # 5a. Get conversation context
            memory = get_memory()
            context = memory.get_context(handler_result["conversation_id"])
            
            # 5b. Generate natural language response using Answer Agent
            answer_agent = AnswerAgent(session_id=session_id)
            natural_response = answer_agent.generate_response(
                query=request.message,
                intent=intent_category,
                data=handler_result["data"],
                context=context
            )
        else:
            # 5c. Use direct message from handler (no LLM, saves tokens!)
            natural_response = handler_result["data"].get("message", "No response available.")
        
        # Get current selected project from memory
        memory = get_memory()
        context = memory.get_context(handler_result["conversation_id"])
        project_context = context.get("project_context", {})
        selected_project_name = project_context.get("project_name") if project_context.get("scope") == "specific" else None
        
        return ChatResponse(
            message=natural_response,
            intent=intent_category,
            confidence=confidence,
            data=handler_result["data"],
            conversation_id=handler_result["conversation_id"],
            selected_project=selected_project_name,
            error=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@router.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    Clear conversation history.
    
    Args:
        conversation_id: ID of conversation to clear
        
    Returns:
        Success status
    """
    memory = get_memory()
    success = memory.clear(conversation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"status": "success", "message": "Conversation cleared"}


@router.get("/conversations")
async def list_conversations():
    """
    List all active conversations.
    
    Returns:
        List of conversation IDs
    """
    memory = get_memory()
    conversations = memory.get_all_conversations()
    
    return {
        "conversations": conversations,
        "count": len(conversations)
    }


@router.get("/session/{conversation_id}/project")
async def get_session_project(conversation_id: str):
    """
    Get project ID from chat session.
    
    Args:
        conversation_id: ID of conversation
        
    Returns:
        Project information from session
    """
    memory = get_memory()
    context = memory.get_context(conversation_id)
    project_context = context.get("project_context", {})
    
    if not project_context or not project_context.get("project_id"):
        return {
            "conversation_id": conversation_id,
            "project_id": None,
            "project_name": None,
            "message": "Nenhum projeto selecionado nesta sessão"
        }
    
    return {
        "conversation_id": conversation_id,
        "project_id": project_context.get("project_id"),
        "project_name": project_context.get("project_name"),
        "scope": project_context.get("scope"),
        "message": "Projeto encontrado"
    }

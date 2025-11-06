"""
Conversation memory for maintaining context across multiple queries.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4


class ConversationMemory:
    """
    Simple in-memory conversation storage.
    For production, consider using Redis or a database.
    """
    
    def __init__(self, ttl_hours: int = 24):
        """
        Initialize conversation memory.
        
        Args:
            ttl_hours: Time-to-live for conversations in hours
        """
        self._storage: Dict[str, List[dict]] = defaultdict(list)
        self.ttl = timedelta(hours=ttl_hours)
    
    def get_context(self, conversation_id: str) -> Dict:
        """
        Get conversation context.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Dictionary with conversation context
        """
        if not conversation_id or conversation_id not in self._storage:
            return {
                "last_query": None,
                "last_params": {},
                "last_intent": None,
                "history": []
            }
        
        messages = self._storage[conversation_id]
        
        # Filter out expired messages
        cutoff_time = datetime.now() - self.ttl
        messages = [m for m in messages if m["timestamp"] > cutoff_time]
        self._storage[conversation_id] = messages
        
        if not messages:
            return {
                "last_query": None,
                "last_params": {},
                "last_intent": None,
                "history": []
            }
        
        last_message = messages[-1]
        
        return {
            "last_query": last_message.get("query"),
            "last_params": last_message.get("params", {}),
            "last_intent": last_message.get("intent"),
            "history": messages[-5:]  # Last 5 messages
        }
    
    def save(
        self,
        conversation_id: Optional[str],
        query: str,
        intent: str,
        params: dict,
        result: dict
    ) -> str:
        """
        Save interaction to memory.
        
        Args:
            conversation_id: Existing conversation ID or None for new
            query: User query
            intent: Classified intent
            params: Extracted parameters
            result: Handler result
            
        Returns:
            Conversation ID (existing or newly created)
        """
        if not conversation_id:
            conversation_id = str(uuid4())
        
        self._storage[conversation_id].append({
            "timestamp": datetime.now(),
            "query": query,
            "intent": intent,
            "params": params,
            "result": result
        })
        
        return conversation_id
    
    def clear(self, conversation_id: str) -> bool:
        """
        Clear conversation history.
        
        Args:
            conversation_id: Conversation to clear
            
        Returns:
            True if conversation existed and was cleared
        """
        if conversation_id in self._storage:
            del self._storage[conversation_id]
            return True
        return False
    
    def get_all_conversations(self) -> List[str]:
        """Get list of all active conversation IDs."""
        return list(self._storage.keys())


# Singleton instance
_memory_instance = None


def get_memory() -> ConversationMemory:
    """Get or create the global memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ConversationMemory()
    return _memory_instance

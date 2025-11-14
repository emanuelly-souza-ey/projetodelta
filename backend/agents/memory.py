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
                "history": [],
                "project_context": {}
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
                "history": [],
                "project_context": {}
            }
        
        last_message = messages[-1]
        
        # Get project context from latest message or use default
        project_context = last_message.get("project_context", {})
        
        return {
            "last_query": last_message.get("query"),
            "last_params": last_message.get("params", {}),
            "last_intent": last_message.get("intent"),
            "history": messages[-5:],
            "project_context": project_context
        }
    
    def save(
        self,
        conversation_id: Optional[str],
        query: str,
        intent: str,
        params: dict,
        result: dict,
        project_context: Optional[Dict] = None
    ) -> str:
        """
        Save interaction to memory.
        
        Args:
            conversation_id: Existing conversation ID or None for new
            query: User query
            intent: Classified intent
            params: Extracted parameters
            result: Handler result
            project_context: Optional project context to maintain
            
        Returns:
            Conversation ID (existing or newly created)
        """
        if not conversation_id:
            conversation_id = str(uuid4())
        
        # Preserve existing project context if not provided
        if project_context is None and conversation_id in self._storage:
            existing_messages = self._storage[conversation_id]
            if existing_messages:
                project_context = existing_messages[-1].get("project_context", {})
        
        self._storage[conversation_id].append({
            "timestamp": datetime.now(),
            "query": query,
            "intent": intent,
            "params": params,
            "result": result,
            "project_context": project_context or {}
        })
        
        return conversation_id
    
    def update_project_context(
        self,
        conversation_id: str,
        project_id: Optional[str] = None,
        project_name: Optional[str] = None,
        epic_id: Optional[int] = None,
        scope: str = "specific"
    ) -> None:
        """
        Update project context for a conversation.
        
        Args:
            conversation_id: Conversation ID
            project_id: Project ID
            project_name: Project name (Epic name)
            epic_id: Epic work item ID
            scope: Project scope ('specific', 'all', 'default')
        """
        if conversation_id not in self._storage:
            self._storage[conversation_id] = []
        
        project_context = {
            "project_id": project_id,
            "project_name": project_name,
            "epic_id": epic_id,
            "scope": scope,
            "updated_at": datetime.now().isoformat()
        }
        
        # If there are existing messages, update the last one
        if self._storage[conversation_id]:
            self._storage[conversation_id][-1]["project_context"] = project_context
        else:
            # Create initial message with project context
            self._storage[conversation_id].append({
                "timestamp": datetime.now(),
                "query": "",
                "intent": "project_context_init",
                "params": {},
                "result": {},
                "project_context": project_context
            })
    
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
    
    def get_last_response(self, conversation_id: str) -> Optional[Dict]:
        """
        Get the last assistant response data from history.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Last assistant response result dict, or None if not found
        """
        if conversation_id not in self._storage:
            return None
        
        messages = self._storage[conversation_id]
        
        # Search backwards for last message with result data
        for message in reversed(messages):
            if message.get("result"):
                return message["result"]
        
        return None
    
    def get_recent_messages(self, conversation_id: str, limit: int = 5) -> List[Dict]:
        """
        Get last N messages from conversation.
        
        Args:
            conversation_id: Conversation ID
            limit: Number of messages to retrieve
            
        Returns:
            List of recent messages
        """
        if conversation_id not in self._storage:
            return []
        
        messages = self._storage[conversation_id]
        return messages[-limit:] if messages else []


# Singleton instance
_memory_instance = None


def get_memory() -> ConversationMemory:
    """Get or create the global memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ConversationMemory()
    return _memory_instance

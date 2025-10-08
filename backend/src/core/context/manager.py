"""
Context Manager
Manages conversation context for multi-turn interactions
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class ContextManager:
    """
    Manages conversation context and state for multi-turn interactions
    """
    
    def __init__(self, max_history: int = 10, ttl_minutes: int = 30):
        """
        Initialize context manager
        
        Args:
            max_history: Maximum conversation history to maintain
            ttl_minutes: Time to live for conversations in minutes
        """
        self.conversations = {}
        self.max_history = max_history
        self.ttl_minutes = ttl_minutes
        
    async def get_context(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get context for a conversation
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Conversation context dictionary
        """
        # Clean expired conversations
        self._cleanup_expired()
        
        if conversation_id not in self.conversations:
            # Create new conversation context
            self.conversations[conversation_id] = {
                "id": conversation_id,
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
                "history": [],
                "entities": {},
                "filters": {},
                "state": {}
            }
        
        return self.conversations[conversation_id]
    
    async def update_context(
        self,
        conversation_id: str,
        query: str,
        response: Dict[str, Any]
    ) -> None:
        """
        Update conversation context with new interaction
        
        Args:
            conversation_id: Conversation ID
            query: User query
            response: System response
        """
        context = await self.get_context(conversation_id)
        
        # Add to history
        context["history"].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "intent": response.get("intent"),
            "entities": response.get("entities", []),
            "results_count": response.get("results_count", 0),
            "siem_query": response.get("siem_query")
        })
        
        # Maintain max history
        if len(context["history"]) > self.max_history:
            context["history"] = context["history"][-self.max_history:]
        
        # Update entities (merge with existing)
        for entity in response.get("entities", []):
            entity_type = entity.get("type")
            entity_value = entity.get("value")
            
            if entity_type and entity_value:
                if entity_type not in context["entities"]:
                    context["entities"][entity_type] = []
                if entity_value not in context["entities"][entity_type]:
                    context["entities"][entity_type].append(entity_value)
        
        # Update filters if any
        if "filters" in response:
            context["filters"].update(response["filters"])
        
        # Update last activity
        context["last_updated"] = datetime.now()
        
        logger.debug(f"Updated context for conversation {conversation_id}")
    
    async def get_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of history items to return
            
        Returns:
            List of history items
        """
        context = await self.get_context(conversation_id)
        history = context.get("history", [])
        
        if limit and limit > 0:
            return history[-limit:]
        return history
    
    async def get_last_query(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the last query from conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Last query dictionary or None
        """
        history = await self.get_history(conversation_id, limit=1)
        return history[0] if history else None
    
    async def get_entities(self, conversation_id: str) -> Dict[str, List[str]]:
        """
        Get all entities from conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dictionary of entity types to values
        """
        context = await self.get_context(conversation_id)
        return context.get("entities", {})
    
    async def get_filters(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get active filters for conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Active filters dictionary
        """
        context = await self.get_context(conversation_id)
        return context.get("filters", {})
    
    async def apply_context_to_query(
        self,
        conversation_id: str,
        new_query: str,
        new_entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Apply conversation context to a new query
        
        Args:
            conversation_id: Conversation ID
            new_query: New user query
            new_entities: Entities extracted from new query
            
        Returns:
            Enhanced query with context
        """
        context = await self.get_context(conversation_id)
        last_query = await self.get_last_query(conversation_id)
        
        # Check if this is a follow-up query
        is_follow_up = self._is_follow_up_query(new_query, last_query)
        
        enhanced_query = {
            "query": new_query,
            "entities": new_entities,
            "context_entities": context.get("entities", {}),
            "filters": context.get("filters", {}),
            "is_follow_up": is_follow_up,
            "previous_intent": last_query.get("intent") if last_query else None
        }
        
        # If it's a follow-up, merge entities
        if is_follow_up and last_query:
            # Preserve entities from last query if not overridden
            for entity_type, values in context.get("entities", {}).items():
                # Check if new query has this entity type
                new_has_type = any(e.get("type") == entity_type for e in new_entities)
                if not new_has_type:
                    # Add from context
                    for value in values[-1:]:  # Take last value
                        enhanced_query["entities"].append({
                            "type": entity_type,
                            "value": value,
                            "from_context": True
                        })
        
        return enhanced_query
    
    def _is_follow_up_query(self, new_query: str, last_query: Optional[Dict]) -> bool:
        """
        Determine if new query is a follow-up to previous
        
        Args:
            new_query: New query string
            last_query: Previous query data
            
        Returns:
            True if it's a follow-up query
        """
        if not last_query:
            return False
        
        # Check for follow-up indicators
        follow_up_phrases = [
            "filter", "only", "just", "also", "and", "but",
            "show me more", "what about", "how about", "then",
            "those", "these", "that", "this"
        ]
        
        query_lower = new_query.lower()
        for phrase in follow_up_phrases:
            if phrase in query_lower:
                return True
        
        # Check if query is very short (likely referencing context)
        if len(new_query.split()) <= 3:
            return True
        
        return False
    
    async def clear_context(self, conversation_id: str) -> None:
        """
        Clear context for a conversation
        
        Args:
            conversation_id: Conversation ID
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared context for conversation {conversation_id}")
    
    def _cleanup_expired(self) -> None:
        """Remove expired conversations"""
        now = datetime.now()
        expired = []
        
        for conv_id, context in self.conversations.items():
            last_updated = context.get("last_updated", context.get("created_at"))
            if isinstance(last_updated, datetime):
                age = now - last_updated
                if age > timedelta(minutes=self.ttl_minutes):
                    expired.append(conv_id)
        
        for conv_id in expired:
            del self.conversations[conv_id]
            logger.debug(f"Expired conversation {conv_id}")
    
    async def export_context(self, conversation_id: str) -> str:
        """
        Export conversation context as JSON
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            JSON string of context
        """
        context = await self.get_context(conversation_id)
        
        # Convert datetime objects to strings
        export_data = {
            "id": context["id"],
            "created_at": context["created_at"].isoformat() if isinstance(context["created_at"], datetime) else context["created_at"],
            "last_updated": context["last_updated"].isoformat() if isinstance(context["last_updated"], datetime) else context["last_updated"],
            "history": context["history"],
            "entities": context["entities"],
            "filters": context["filters"],
            "state": context["state"]
        }
        
        return json.dumps(export_data, indent=2)
    
    async def import_context(self, conversation_id: str, context_json: str) -> None:
        """
        Import conversation context from JSON
        
        Args:
            conversation_id: Conversation ID
            context_json: JSON string of context
        """
        try:
            context_data = json.loads(context_json)
            
            # Convert string dates back to datetime
            if "created_at" in context_data:
                context_data["created_at"] = datetime.fromisoformat(context_data["created_at"])
            if "last_updated" in context_data:
                context_data["last_updated"] = datetime.fromisoformat(context_data["last_updated"])
            
            self.conversations[conversation_id] = context_data
            logger.info(f"Imported context for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to import context: {e}")
            raise

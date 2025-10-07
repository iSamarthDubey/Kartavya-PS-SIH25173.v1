"""
Simple Context Manager for conversation state.
Stores conversation history and user context in memory.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class ContextManager:
    """Manages conversation context and history."""
    
    def __init__(self):
        """Initialize the context manager."""
        self.conversations: Dict[str, List[Dict]] = {}
        self.user_contexts: Dict[str, Dict] = {}
    
    async def get_context(self, conversation_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve conversation context.
        
        Args:
            conversation_id: Unique conversation identifier
            user_id: Optional user identifier
            
        Returns:
            Dictionary containing conversation history and context
        """
        history = self.conversations.get(conversation_id, [])
        user_context = self.user_contexts.get(user_id or conversation_id, {})
        
        return {
            'conversation_id': conversation_id,
            'history': history,
            'user_context': user_context,
            'message_count': len(history)
        }
    
    async def save_context(
        self, 
        conversation_id: str, 
        query: str, 
        response: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> None:
        """
        Save conversation turn to context.
        
        Args:
            conversation_id: Unique conversation identifier
            query: User query
            response: System response
            user_id: Optional user identifier
        """
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        turn = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': {
                'intent': response.get('intent'),
                'entities': response.get('entities', []),
                'result_count': response.get('data', {}).get('total', 0),
                'summary': response.get('summary', '')
            }
        }
        
        self.conversations[conversation_id].append(turn)
        
        # Limit history to last 50 turns
        if len(self.conversations[conversation_id]) > 50:
            self.conversations[conversation_id] = self.conversations[conversation_id][-50:]
    
    async def clear_context(self, conversation_id: str) -> None:
        """Clear conversation history."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    async def update_user_context(
        self, 
        user_id: str, 
        context_updates: Dict[str, Any]
    ) -> None:
        """
        Update user-specific context.
        
        Args:
            user_id: User identifier
            context_updates: Dictionary of context updates
        """
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {}
        
        self.user_contexts[user_id].update(context_updates)
    
    def get_recent_queries(self, conversation_id: str, count: int = 5) -> List[str]:
        """Get recent queries from conversation."""
        history = self.conversations.get(conversation_id, [])
        return [turn['query'] for turn in history[-count:]]
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get summary statistics for a conversation."""
        history = self.conversations.get(conversation_id, [])
        
        if not history:
            return {'exists': False}
        
        intents = [turn['response'].get('intent') for turn in history]
        total_results = sum(turn['response'].get('result_count', 0) for turn in history)
        
        return {
            'exists': True,
            'turn_count': len(history),
            'start_time': history[0]['timestamp'] if history else None,
            'last_time': history[-1]['timestamp'] if history else None,
            'total_results_retrieved': total_results,
            'unique_intents': len(set(intents)),
            'most_common_intent': max(set(intents), key=intents.count) if intents else None
        }

"""
Text formatting utilities for SIEM responses.
"""

from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class TextFormatter:
    """Format SIEM query results into human-readable text."""
    
    def __init__(self):
        """Initialize the text formatter."""
        pass
    
    def format_search_results(self, results: List[Dict[str, Any]], 
                            query: str = "") -> str:
        """Format search results into readable text."""
        if not results:
            return "No results found for your query."
        
        formatted_text = f"Found {len(results)} results"
        if query:
            formatted_text += f" for query: '{query}'"
        formatted_text += "\n\n"
        
        for i, result in enumerate(results[:10], 1):  # Limit to top 10
            formatted_text += f"Result {i}:\n"
            
            # Format timestamp
            if '@timestamp' in result:
                formatted_text += f"  Time: {result['@timestamp']}\n"
            
            # Format source
            if 'source' in result:
                formatted_text += f"  Source: {result['source']}\n"
            
            # Format message
            if 'message' in result:
                message = result['message']
                if len(message) > 200:
                    message = message[:200] + "..."
                formatted_text += f"  Message: {message}\n"
            
            # Format other fields
            for key, value in result.items():
                if key not in ['@timestamp', 'source', 'message', '_id', '_index']:
                    if isinstance(value, (str, int, float)):
                        formatted_text += f"  {key.title()}: {value}\n"
            
            formatted_text += "\n"
        
        if len(results) > 10:
            formatted_text += f"... and {len(results) - 10} more results\n"
        
        return formatted_text
    
    def format_summary(self, data: Dict[str, Any]) -> str:
        """Format summary statistics."""
        summary = "Summary:\n"
        
        for key, value in data.items():
            if isinstance(value, (int, float)):
                summary += f"  {key.title()}: {value:,}\n"
            elif isinstance(value, str):
                summary += f"  {key.title()}: {value}\n"
            elif isinstance(value, list):
                summary += f"  {key.title()}: {len(value)} items\n"
        
        return summary
    
    def format_error(self, error: str, context: str = "") -> str:
        """Format error messages."""
        error_text = "Error occurred"
        if context:
            error_text += f" while {context}"
        error_text += f": {error}"
        return error_text
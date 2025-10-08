"""
FREE Gemini AI Query Enhancement Layer
Enhances rule-based queries with AI intelligence - 100% FREE
"""

import os
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiEnhancer:
    """FREE Gemini AI for query enhancement and validation."""
    
    def __init__(self):
        """Initialize Gemini with FREE API key."""
        # Get free API key from: https://makersuite.google.com/app/apikey
        api_key = os.getenv('GEMINI_API_KEY', 'demo-mode')
        
        if api_key and api_key != 'demo-mode':
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')  # FREE model
                self.enabled = True
                logger.info("✅ Gemini AI enabled (FREE tier: 15 req/min)")
            except Exception as e:
                logger.warning(f"Gemini AI disabled: {e}")
                self.enabled = False
        else:
            logger.info("Gemini AI in demo mode - add GEMINI_API_KEY to enable")
            self.enabled = False
    
    def enhance_query(self, base_query: Dict[str, Any], user_intent: str, 
                     entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance rule-based query with AI intelligence.
        Falls back to base_query if AI fails.
        """
        if not self.enabled:
            return base_query
        
        try:
            prompt = self._build_enhancement_prompt(base_query, user_intent, entities)
            
            # FREE Gemini request (15/minute limit)
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Parse and validate AI response
                enhanced = self._parse_ai_response(response.text, base_query)
                logger.info("✅ Query enhanced by Gemini AI")
                return enhanced
            
        except Exception as e:
            logger.warning(f"Gemini enhancement failed: {e}")
        
        # Always return base_query if AI fails
        return base_query
    
    def _build_enhancement_prompt(self, base_query: Dict[str, Any], 
                                user_intent: str, entities: Dict[str, Any]) -> str:
        """Build prompt for query enhancement."""
        return f"""
You are a SIEM query expert. Enhance this Elasticsearch query to be more precise and efficient.

USER INTENT: {user_intent}
ENTITIES FOUND: {entities}
BASE QUERY: {base_query}

Rules:
1. Keep the same structure
2. Add relevant filters for security analysis
3. Optimize for performance
4. Return ONLY the enhanced JSON query
5. No explanation needed

Enhanced query:"""
    
    def _parse_ai_response(self, ai_response: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response, return fallback if parsing fails."""
        try:
            import json
            # Extract JSON from response
            if '{' in ai_response and '}' in ai_response:
                start = ai_response.find('{')
                end = ai_response.rfind('}') + 1
                json_str = ai_response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        return fallback  # Always safe fallback
    
    def validate_query_safety(self, query: Dict[str, Any]) -> bool:
        """Validate that AI-enhanced query is safe to execute."""
        if not self.enabled:
            return True  # Rule-based queries are always safe
        
        try:
            # Check for dangerous operations
            dangerous_patterns = ['delete', 'drop', 'truncate', '_delete_by_query']
            query_str = str(query).lower()
            
            for pattern in dangerous_patterns:
                if pattern in query_str:
                    logger.warning(f"Unsafe query detected: {pattern}")
                    return False
            
            return True
        except:
            return False  # Fail safe
    
    def get_explanation(self, query: str, results_count: int) -> str:
        """Get natural language explanation of query results."""
        if not self.enabled:
            return f"Found {results_count} matching records."
        
        try:
            prompt = f"""
Explain these SIEM query results in simple terms:

QUERY: {query}
RESULTS: {results_count} records found

Provide a brief, clear explanation for security analysts:"""
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except:
            pass
        
        return f"Found {results_count} matching records."


# Global instance
gemini_enhancer = GeminiEnhancer()

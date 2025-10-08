"""
🤖 Hybrid AI System - Toggleable LLM Support
Routes between Gemini (free) and OpenAI (premium) based on configuration and complexity
"""

import logging
from typing import Dict, Any, Optional, Union
from enum import Enum
import json
from ..config import settings, get_ai_config

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """AI provider types"""
    GEMINI = "gemini"
    OPENAI = "openai"
    NONE = "none"


class QueryComplexity(str, Enum):
    """Query complexity levels"""
    SIMPLE = "simple"      # Basic queries, pattern matching
    MEDIUM = "medium"      # Multi-step analysis 
    COMPLEX = "complex"    # Advanced reasoning, reports


class HybridAI:
    """
    Hybrid AI system that intelligently routes between different AI providers
    Falls back gracefully if AI is disabled or unavailable
    """
    
    def __init__(self):
        """Initialize hybrid AI system"""
        self.config = get_ai_config()
        self.gemini_client = None
        self.openai_client = None
        
        # Initialize available clients
        self._initialize_clients()
        
        # Log availability
        self._log_availability()
    
    def _initialize_clients(self):
        """Initialize AI clients based on configuration"""
        if not self.config.get("enabled", False):
            logger.info("🤖 AI disabled by configuration")
            return
        
        # Initialize Gemini (Primary, free)
        if self.config["gemini"]["available"]:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.config["gemini"]["api_key"])
                self.gemini_client = genai.GenerativeModel(self.config["gemini"]["model"])
                logger.info("✅ Gemini AI initialized (Free tier)")
            except Exception as e:
                logger.warning(f"❌ Failed to initialize Gemini: {e}")
        
        # Initialize OpenAI (Backup, premium)
        if self.config["openai"]["available"]:
            try:
                import openai
                openai.api_key = self.config["openai"]["api_key"]
                self.openai_client = openai
                logger.info("✅ OpenAI initialized (Premium tier)")
            except Exception as e:
                logger.warning(f"❌ Failed to initialize OpenAI: {e}")
    
    def _log_availability(self):
        """Log AI system availability"""
        if not self.is_enabled:
            logger.info("🚫 AI system disabled")
            return
        
        providers = []
        if self.gemini_client:
            providers.append("Gemini (Free)")
        if self.openai_client:
            providers.append("OpenAI (Premium)")
        
        if providers:
            logger.info(f"🤖 AI providers available: {', '.join(providers)}")
        else:
            logger.warning("⚠️ No AI providers available")
    
    @property
    def is_enabled(self) -> bool:
        """Check if AI system is enabled and has providers"""
        return self.config.get("enabled", False) and (
            self.gemini_client is not None or self.openai_client is not None
        )
    
    def _determine_complexity(self, query: str, context: Dict[str, Any]) -> QueryComplexity:
        """Determine query complexity for AI routing"""
        query_lower = query.lower()
        
        # Complex indicators
        complex_keywords = [
            "report", "analyze", "investigate", "correlate", "summarize",
            "explain why", "what happened", "root cause", "timeline",
            "attack chain", "threat actor", "campaign"
        ]
        
        # Medium indicators  
        medium_keywords = [
            "compare", "trend", "pattern", "anomaly", "behavior",
            "multiple", "related", "similar", "across"
        ]
        
        # Check for complexity indicators
        if any(keyword in query_lower for keyword in complex_keywords):
            return QueryComplexity.COMPLEX
        elif any(keyword in query_lower for keyword in medium_keywords):
            return QueryComplexity.MEDIUM
        else:
            return QueryComplexity.SIMPLE
    
    def _choose_provider(self, complexity: QueryComplexity) -> AIProvider:
        """Choose best AI provider based on complexity and availability"""
        if not self.is_enabled:
            return AIProvider.NONE
        
        # For complex queries, prefer OpenAI if available
        if complexity == QueryComplexity.COMPLEX and self.openai_client:
            return AIProvider.OPENAI
        
        # For medium/simple queries, prefer Gemini (free)
        if self.gemini_client:
            return AIProvider.GEMINI
        
        # Fallback to OpenAI if available
        if self.openai_client:
            return AIProvider.OPENAI
        
        return AIProvider.NONE
    
    def enhance_query(self, base_query: Dict[str, Any], user_intent: str, 
                     entities: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance SIEM query with AI intelligence
        Falls back to base query if AI is disabled or fails
        """
        if not self.is_enabled:
            logger.debug("AI disabled, returning base query")
            return base_query
        
        try:
            complexity = self._determine_complexity(user_intent, context or {})
            provider = self._choose_provider(complexity)
            
            if provider == AIProvider.NONE:
                return base_query
            
            # Generate enhancement prompt
            prompt = self._build_enhancement_prompt(base_query, user_intent, entities, context)
            
            # Route to appropriate provider
            if provider == AIProvider.GEMINI:
                enhanced = self._enhance_with_gemini(prompt, base_query)
            elif provider == AIProvider.OPENAI:
                enhanced = self._enhance_with_openai(prompt, base_query)
            else:
                return base_query
            
            logger.info(f"🤖 Query enhanced using {provider.value}")
            return enhanced
        
        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return base_query
    
    def _build_enhancement_prompt(self, base_query: Dict[str, Any], user_intent: str,
                                entities: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build enhancement prompt for AI"""
        return f"""You are a SIEM query optimization expert. Enhance this query for better security analysis.

USER INTENT: {user_intent}
EXTRACTED ENTITIES: {json.dumps(entities, indent=2)}
BASE QUERY: {json.dumps(base_query, indent=2)}
CONTEXT: {json.dumps(context or {}, indent=2)}

Rules:
1. Keep the same query structure and syntax
2. Add relevant security filters and conditions
3. Optimize for performance and accuracy
4. Include time-based filters if not present
5. Add aggregations for better insights
6. Return ONLY the enhanced JSON query
7. No explanation or markdown formatting

Enhanced query:"""
    
    def _enhance_with_gemini(self, prompt: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance query using Gemini API"""
        try:
            response = self.gemini_client.generate_content(prompt)
            if response and response.text:
                return self._parse_ai_response(response.text, fallback)
        except Exception as e:
            logger.error(f"Gemini enhancement failed: {e}")
        
        return fallback
    
    def _enhance_with_openai(self, prompt: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance query using OpenAI API"""
        try:
            response = self.openai_client.ChatCompletion.create(
                model=self.config["openai"]["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            
            if response and response.choices:
                content = response.choices[0].message.content
                return self._parse_ai_response(content, fallback)
        except Exception as e:
            logger.error(f"OpenAI enhancement failed: {e}")
        
        return fallback
    
    def _parse_ai_response(self, ai_response: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response, return fallback if parsing fails"""
        try:
            # Extract JSON from response
            if '{' in ai_response and '}' in ai_response:
                start = ai_response.find('{')
                end = ai_response.rfind('}') + 1
                json_str = ai_response[start:end]
                
                # Validate JSON
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    return parsed
        except Exception as e:
            logger.debug(f"Failed to parse AI response: {e}")
        
        return fallback
    
    def generate_explanation(self, query: str, results: Dict[str, Any]) -> str:
        """Generate natural language explanation of query results"""
        if not self.is_enabled:
            return f"Query executed successfully. Found {results.get('total', 0)} matching records."
        
        try:
            complexity = QueryComplexity.MEDIUM  # Explanations are medium complexity
            provider = self._choose_provider(complexity)
            
            if provider == AIProvider.NONE:
                return f"Found {results.get('total', 0)} matching records."
            
            prompt = f"""Explain these SIEM query results in clear, professional terms for security analysts:

QUERY: {query}
RESULTS: {json.dumps(results, indent=2)}

Provide a concise explanation covering:
1. What was searched for
2. Key findings and numbers
3. Security implications if any
4. Recommended next steps if relevant

Keep it professional and actionable:"""
            
            if provider == AIProvider.GEMINI:
                response = self.gemini_client.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            
            elif provider == AIProvider.OPENAI:
                response = self.openai_client.ChatCompletion.create(
                    model=self.config["openai"]["model"],
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.3
                )
                if response and response.choices:
                    return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
        
        # Fallback explanation
        return f"Analysis complete. Found {results.get('total', 0)} records matching your query."
    
    def get_status(self) -> Dict[str, Any]:
        """Get AI system status"""
        return {
            "enabled": self.is_enabled,
            "providers": {
                "gemini": {
                    "available": self.gemini_client is not None,
                    "model": self.config["gemini"]["model"] if self.gemini_client else None
                },
                "openai": {
                    "available": self.openai_client is not None, 
                    "model": self.config["openai"]["model"] if self.openai_client else None
                }
            },
            "environment": settings.environment,
            "demo_mode": settings.is_demo
        }


# Global AI instance
hybrid_ai = HybridAI()

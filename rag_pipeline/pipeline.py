"""
RAG Pipeline for generating SIEM queries from natural language.
"""

import json
import os
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for SIEM query generation."""
    
    def __init__(self):
        """Initialize the RAG pipeline."""
        self.query_templates = self._load_query_templates()
        self.vector_store = None  # Will be initialized when needed
        self.retriever = None
    
    def _load_query_templates(self) -> Dict[str, Any]:
        """Load query templates for different SIEM platforms."""
        templates = {
            "elasticsearch": {
                "search_logs": {
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"message": "{search_term}"}}
                            ],
                            "filter": [
                                {"range": {"@timestamp": {"gte": "{start_time}", "lte": "{end_time}"}}}
                            ]
                        }
                    }
                },
                "count_events": {
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"event.type": "{event_type}"}}
                            ],
                            "filter": [
                                {"range": {"@timestamp": {"gte": "{start_time}", "lte": "{end_time}"}}}
                            ]
                        }
                    }
                },
                "ip_search": {
                    "query": {
                        "bool": {
                            "should": [
                                {"match": {"source.ip": "{ip_address}"}},
                                {"match": {"destination.ip": "{ip_address}"}}
                            ],
                            "filter": [
                                {"range": {"@timestamp": {"gte": "{start_time}", "lte": "{end_time}"}}}
                            ]
                        }
                    }
                },
                "user_activity": {
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"user.name": "{username}"}}
                            ],
                            "filter": [
                                {"range": {"@timestamp": {"gte": "{start_time}", "lte": "{end_time}"}}}
                            ]
                        }
                    }
                },
                "severity_filter": {
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"log.level": "{severity}"}}
                            ],
                            "filter": [
                                {"range": {"@timestamp": {"gte": "{start_time}", "lte": "{end_time}"}}}
                            ]
                        }
                    }
                }
            },
            "wazuh": {
                "search_logs": {
                    "q": "rule.description:*{search_term}*",
                    "timestamp": "{start_time} TO {end_time}"
                },
                "ip_search": {
                    "q": "data.srcip:{ip_address} OR data.dstip:{ip_address}",
                    "timestamp": "{start_time} TO {end_time}"
                },
                "user_activity": {
                    "q": "data.srcuser:{username}",
                    "timestamp": "{start_time} TO {end_time}"
                },
                "severity_filter": {
                    "q": "rule.level:{severity}",
                    "timestamp": "{start_time} TO {end_time}"
                }
            }
        }
        return templates
    
    def generate_query(self, parsed_query: Dict[str, Any], platform: str = "elasticsearch") -> Dict[str, Any]:
        """Generate SIEM query from parsed natural language query."""
        intent = parsed_query.get('intent', 'search_logs')
        entities = parsed_query.get('entities', {})
        temporal = parsed_query.get('temporal')
        filters = parsed_query.get('filters', {})
        
        # Get base template
        template = self._get_template(intent, platform, entities)
        
        # Fill template with extracted information
        query = self._fill_template(template, entities, temporal, filters)
        
        return query
    
    def _get_template(self, intent: str, platform: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Get appropriate query template based on intent and entities."""
        platform_templates = self.query_templates.get(platform, {})
        
        # Choose template based on entities present
        if 'ip_address' in entities:
            return platform_templates.get('ip_search', platform_templates.get('search_logs', {}))
        elif 'user' in entities:
            return platform_templates.get('user_activity', platform_templates.get('search_logs', {}))
        elif 'severity' in entities:
            return platform_templates.get('severity_filter', platform_templates.get('search_logs', {}))
        else:
            return platform_templates.get(intent, platform_templates.get('search_logs', {}))
    
    def _fill_template(self, template: Dict[str, Any], entities: Dict[str, Any], 
                      temporal: Optional[Dict[str, Any]], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Fill query template with extracted values."""
        # Convert template to string for replacement
        template_str = json.dumps(template)
        
        # Replace entity placeholders
        replacements = {
            '{search_term}': self._get_search_term(entities, filters),
            '{ip_address}': entities.get('ip_address', [''])[0],
            '{username}': entities.get('user', [''])[0],
            '{severity}': entities.get('severity', ['medium'])[0],
            '{event_type}': filters.get('event_type', 'security'),
            '{start_time}': self._get_start_time(temporal),
            '{end_time}': self._get_end_time(temporal)
        }
        
        for placeholder, value in replacements.items():
            template_str = template_str.replace(placeholder, str(value))
        
        try:
            return json.loads(template_str)
        except json.JSONDecodeError:
            logger.error("Failed to parse filled template")
            return template
    
    def _get_search_term(self, entities: Dict[str, Any], filters: Dict[str, Any]) -> str:
        """Extract search term from entities and filters."""
        # Combine relevant entities into search term
        terms = []
        
        if 'domain' in entities:
            terms.extend(entities['domain'])
        
        if 'process' in entities:
            terms.extend(entities['process'])
        
        if filters:
            terms.extend([str(v) for v in filters.values() if v])
        
        return ' '.join(terms) if terms else '*'
    
    def _get_start_time(self, temporal: Optional[Dict[str, Any]]) -> str:
        """Get start time for query."""
        if temporal:
            # Parse temporal information and return appropriate start time
            if temporal['type'] == 'relative':
                # Handle relative time (e.g., "last 1 hour")
                return "now-1h"  # Simplified
            elif temporal['type'] == 'absolute':
                return temporal['groups'][0]
        
        return "now-1h"  # Default to last hour
    
    def _get_end_time(self, temporal: Optional[Dict[str, Any]]) -> str:
        """Get end time for query."""
        if temporal and temporal['type'] == 'range':
            return temporal['groups'][1]
        
        return "now"  # Default to current time
    
    def retrieve_context(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant context for query generation."""
        # This would use vector similarity search in a real implementation
        # For now, return empty list
        return []
    
    def enhance_query(self, base_query: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance query with retrieved context."""
        # In a real implementation, this would use context to improve the query
        return base_query
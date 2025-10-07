"""
Kartavya Query Processing Pipeline - Complete Implementation
Handles the full query lifecycle from NLP to SIEM to response
"""

from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime


# --- From assistant/pipeline.py ---
"""
Conversational Assistant Pipeline
Orchestrates the complete NLP → SIEM → Response workflow for chat-based queries.

This module integrates:
1. NLP Parser (Intent Classification + Entity Extraction)
2. Query Generation (Natural Language to SIEM Query)
3. SIEM Connector (Multi-platform query execution)
4. Response Processing (Normalization + Summarization)
5. Context Management (Conversation history)
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# Import our existing components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.nlp.intent_classifier import IntentClassifier
from backend.nlp.entity_extractor import EntityExtractor
from backend.query_builder import QueryBuilder
from siem_connector.elastic_connector import ElasticConnector
from siem_connector.wazuh_connector import WazuhConnector
from backend.response_formatter.formatter import ResponseFormatter
from assistant.context_manager import ContextManager
from assistant.mock_data import generate_mock_logs

logger = logging.getLogger(__name__)

# Clarification thresholds and caps
_DEFAULT_INTENT_CONFIDENCE_THRESHOLD = 0.3
_MAX_RESULTS_CAP = int(os.environ.get("ASSISTANT_MAX_RESULTS", "200"))
_DEFAULT_TIME_WINDOW = os.environ.get("ASSISTANT_DEFAULT_TIME_WINDOW", "now-1d")

class ConversationalPipeline:
    """
    Core orchestrator for the conversational SIEM assistant.
    Handles end-to-end processing from natural language input to formatted response.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the conversational pipeline with all components."""
        self.config = config or {}
        
        # Initialize core components
        self.intent_classifier = None
        self.entity_extractor = None
        self.query_builder = None
        self.elastic_connector = None
        self.wazuh_connector = None
        self.response_formatter = None
        self.context_manager = None
        
        # Pipeline state
        self.is_initialized = False
        self.conversation_id = None
        
        logger.info("Conversational Pipeline initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize all pipeline components.
        Returns True if successful, False otherwise.
        """
        try:
            logger.info("Initializing ConversationalPipeline components...")
            
            # 1. Initialize NLP Components
            self.intent_classifier = IntentClassifier()
            await self._safe_component_init(
                lambda: None,  # IntentClassifier doesn't need async init
                "Intent Classifier"
            )
            
            self.entity_extractor = EntityExtractor()
            await self._safe_component_init(
                lambda: None,  # EntityExtractor doesn't need async init
                "Entity Extractor"
            )
            
            # 2. Initialize Query Builder
            self.query_builder = QueryBuilder()
            await self._safe_component_init(
                lambda: None,  # QueryBuilder doesn't have initialize() method
                "Query Builder"
            )
            
            # 3. Initialize SIEM Connectors
            self.elastic_connector = ElasticConnector()
            await self._safe_component_init(
                lambda: None,  # ElasticConnector doesn't have initialize() method
                "Elastic Connector"
            )
            if hasattr(self.elastic_connector, "is_available") and not self.elastic_connector.is_available():
                logger.warning("Elastic connector unavailable - operating in mock-data mode")
            
            self.wazuh_connector = WazuhConnector()
            await self._safe_component_init(
                lambda: None,  # WazuhConnector doesn't have initialize() method
                "Wazuh Connector"
            )
            if hasattr(self.wazuh_connector, "is_available") and not self.wazuh_connector.is_available():
                logger.warning("Wazuh connector unavailable - skipping Wazuh-backed searches")
            
            # 4. Initialize Response Formatter
            self.response_formatter = ResponseFormatter()
            await self._safe_component_init(
                lambda: None,  # ResponseFormatter doesn't have initialize() method
                "Response Formatter"
            )
            
            # 5. Initialize Context Manager
            self.context_manager = ContextManager()
            await self._safe_component_init(
                lambda: None,  # ContextManager doesn't have initialize() method
                "Context Manager"
            )
            
            self.is_initialized = True
            logger.info("ConversationalPipeline initialization complete!")
            return True
            
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            return False
    
    async def _safe_component_init(self, init_func, component_name: str):
        """Safely initialize a component with error handling."""
        try:
            if asyncio.iscoroutinefunction(init_func):
                await init_func()
            else:
                init_func()
            logger.info(f"✅ {component_name} initialized")
        except Exception as e:
            logger.warning(f"⚠️ {component_name} initialization failed: {e}")
            # Continue with other components even if one fails
    
    async def process_query(self, 
                          user_input: str, 
                          conversation_id: Optional[str] = None,
                          user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a natural language query through the complete pipeline.
        
        Args:
            user_input: Natural language query from user
            conversation_id: Optional conversation ID for context
            user_context: Optional additional context (user preferences, etc.)
            
        Returns:
            Dict containing the complete response with data, visualizations, and metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Start pipeline timing
            start_time = datetime.now()
            
            # Create conversation ID if not provided
            if not conversation_id:
                conversation_id = f"conv_{int(start_time.timestamp())}"
            
            logger.info(f"Processing query: '{user_input}' (conversation: {conversation_id})")
            
            # Step 1: NLP Analysis (Intent + Entities)
            nlp_result = await self._process_nlp(user_input, conversation_id)
            
            # Step 2: Query Generation
            query_result = await self._generate_query(nlp_result, user_input, user_context)

            # Enforce safer defaults and caps
            # Cap results
            try:
                if isinstance(query_result, dict):
                    limit = int(query_result.get('limit', 100))
                    query_result['limit'] = min(limit, _MAX_RESULTS_CAP)
            except Exception:
                query_result['limit'] = min(100, _MAX_RESULTS_CAP)

            # Step 3: SIEM Query Execution
            siem_result = await self._execute_siem_query(query_result)
            
            # Step 4: Response Formatting
            formatted_response = await self._format_response(siem_result, nlp_result)
            
            # Step 5: Context Management
            await self._update_context(conversation_id, user_input, formatted_response)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Convert Entity objects to dictionaries for API response
            entities = nlp_result.get('entities', [])
            entities_dict = []
            if entities:
                for entity in entities:
                    if hasattr(entity, '__dict__'):
                        # Convert dataclass/object to dict
                        entities_dict.append({
                            'type': entity.type,
                            'value': entity.value,
                            'confidence': entity.confidence,
                            'start_pos': entity.start_pos,
                            'end_pos': entity.end_pos
                        })
                    elif isinstance(entity, dict):
                        # Already a dict
                        entities_dict.append(entity)
            
            # Build final response
            data_sources = siem_result.get('sources', [])

            final_response = {
                'conversation_id': conversation_id,
                'user_query': user_input,
                'intent': nlp_result.get('intent', 'unknown'),
                'entities': entities_dict,
                'query_type': query_result.get('query_type', 'search'),
                'siem_query': query_result.get('query', ''),
                'results': formatted_response.get('data', []),
                'visualizations': formatted_response.get('visualizations', []),
                'summary': formatted_response.get('summary', ''),
                'metadata': {
                    'processing_time_seconds': processing_time,
                    'timestamp': start_time.isoformat(),
                    'results_count': len(formatted_response.get('data', [])),
                    'data_sources': data_sources,
                    'confidence_score': nlp_result.get('confidence', 0.0),
                    'needs_clarification': nlp_result.get('needs_clarification', False),
                    'suggestions': nlp_result.get('suggestions', []),
                    'mock_data': 'mock-data' in data_sources,
                },
                'status': 'success'
            }
            
            logger.info(f"Query processed successfully in {processing_time:.2f}s")
            return final_response
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            return {
                'conversation_id': conversation_id or 'error',
                'user_query': user_input,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _process_nlp(self, user_input: str, conversation_id: str) -> Dict[str, Any]:
        """Step 1: Process natural language input for intent and entities."""
        try:
            if self.intent_classifier and self.entity_extractor:
                # Classify intent
                intent, confidence = self.intent_classifier.classify_intent(user_input)
                intent_str = intent.value if hasattr(intent, 'value') else str(intent)
                
                # Extract entities
                entities = self.entity_extractor.extract_entities(user_input)

                # Clarification: propose alternatives when low confidence or sparse entities
                needs_clarification = False
                suggestions = []
                if confidence < _DEFAULT_INTENT_CONFIDENCE_THRESHOLD or len(entities) == 0:
                    try:
                        raw_suggestions = self.intent_classifier.get_intent_suggestions(user_input)
                        # top-3 intent strings with scores
                        suggestions = [
                            {
                                'intent': s[0].value if hasattr(s[0], 'value') else str(s[0]),
                                'score': float(s[1])
                            } for s in raw_suggestions[:3]
                        ]
                        needs_clarification = len(suggestions) > 0
                    except Exception:
                        pass
                
                logger.info(f"NLP Analysis - Intent: {intent_str}, Entities: {len(entities)}, Confidence: {confidence:.2f}")
                
                return {
                    'intent': intent_str,
                    'entities': entities,
                    'confidence': confidence,
                    'raw_intent': intent,
                    'needs_clarification': needs_clarification,
                    'suggestions': suggestions
                }
            else:
                # Fallback if NLP components not available
                return {
                    'intent': 'search_logs',
                    'entities': {},
                    'confidence': 0.5,
                    'fallback': True
                }
        except Exception as e:
            logger.warning(f"NLP processing failed: {e}")
            return {'intent': 'search_logs', 'entities': {}, 'confidence': 0.0}
    
    async def _generate_query(self, nlp_result: Dict, user_input: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Step 2: Generate SIEM query from NLP analysis."""
        try:
            if self.query_builder:
                # Allow overrides from user_context
                force_intent = None
                limit = None
                offset = None
                if user_context and isinstance(user_context, dict):
                    force_intent = user_context.get('force_intent')
                    limit = user_context.get('limit')
                    offset = user_context.get('offset')
                query_params = {
                    'intent': force_intent or nlp_result.get('intent'),
                    'entities': nlp_result.get('entities', []),
                    'raw_text': user_input,
                    'filters': (user_context.get('filters') if user_context and isinstance(user_context.get('filters'), dict) else None),
                }
                if limit is not None:
                    query_params['limit'] = limit
                if offset is not None:
                    query_params['offset'] = offset
                result = await self.query_builder.build_query(query_params)
                result.setdefault('intent', query_params['intent'])
                result.setdefault('entities', query_params['entities'])
                result.setdefault('limit', query_params.get('limit', 100))
                logger.info(f"Query Generated - Type: {result.get('query_type')}")
                return result
            else:
                # Fallback query
                return {
                    'query_type': 'search',
                    'query': f'message:"{user_input}"',
                    'timeframe': '24h',
                    'limit': 100,
                    'intent': nlp_result.get('intent'),
                    'entities': nlp_result.get('entities', {}),
                }
        except Exception as e:
            logger.warning(f"Query generation failed: {e}")
            return {
                'query_type': 'search',
                'query': '*',
                'limit': 10,
                'intent': nlp_result.get('intent'),
                'entities': nlp_result.get('entities', {}),
            }
    
    async def _execute_siem_query(self, query_result: Dict) -> Dict[str, Any]:
        """Step 3: Execute query against available SIEM platforms."""
        try:
            results = []
            sources = []
            
            # Try Elasticsearch first
            if self.elastic_connector and getattr(self.elastic_connector, "is_available", lambda: True)():
                try:
                    elastic_results = await self.elastic_connector.search(
                        query=query_result.get('query', '*'),
                        limit=query_result.get('limit', 100)
                    )
                    if elastic_results and elastic_results.get('hits'):
                        results.extend(elastic_results['hits'])
                        sources.append('elasticsearch')
                        logger.info(f"Elasticsearch: {len(elastic_results['hits'])} results")
                except Exception as e:
                    logger.warning(f"Elasticsearch query failed: {e}")
            elif self.elastic_connector:
                logger.info("Elasticsearch connector unavailable - skipping live search")
            
            # Try Wazuh as backup/supplement
            if (
                self.wazuh_connector
                and len(results) < 50
                and getattr(self.wazuh_connector, "is_available", lambda: True)()
            ):  # Only if we need more data
                try:
                    wazuh_results = await self.wazuh_connector.search(
                        query=query_result.get('query', '*'),
                        limit=max(50 - len(results), 10)
                    )
                    if wazuh_results and wazuh_results.get('hits'):
                        results.extend(wazuh_results['hits'])
                        sources.append('wazuh')
                        logger.info(f"Wazuh: {len(wazuh_results['hits'])} results")
                except Exception as e:
                    logger.warning(f"Wazuh query failed: {e}")
            elif self.wazuh_connector:
                logger.info("Wazuh connector unavailable - skipping live search")
            
            if not results:
                entity_map = self._normalize_entities_for_mock(query_result.get('entities'))
                mock_records = generate_mock_logs(
                    query_result.get('intent', 'search_events'),
                    entity_map,
                    limit=query_result.get('limit', 10),
                )
                if mock_records:
                    results.extend(mock_records)
                    sources.append('mock-data')
                    logger.info(f"Mock data generator produced {len(mock_records)} records")

            return {
                'hits': results,
                'total': len(results),
                'sources': sources,
                'query_type': query_result.get('query_type')
            }
            
        except Exception as e:
            logger.error(f"SIEM query execution failed: {e}")
            return {'hits': [], 'total': 0, 'sources': []}
    
    async def _format_response(self, siem_result: Dict, nlp_result: Dict) -> Dict[str, Any]:
        """Step 4: Format raw SIEM data into user-friendly response."""
        try:
            if self.response_formatter:
                format_params = {
                    'data': siem_result.get('hits', []),
                    'intent': nlp_result.get('intent'),
                    'query_type': siem_result.get('query_type', 'search')
                }
                result = await self.response_formatter.format_response(format_params)
                logger.info(f"Response formatted with {len(result.get('visualizations', []))} visualizations")
                return result
            else:
                # Basic fallback formatting
                return {
                    'data': siem_result.get('hits', [])[:10],  # Limit to 10 for fallback
                    'summary': f"Found {siem_result.get('total', 0)} results",
                    'visualizations': []
                }
        except Exception as e:
            logger.warning(f"Response formatting failed: {e}")
            return {'data': [], 'summary': 'No results available', 'visualizations': []}
    
    async def _update_context(self, conversation_id: str, user_input: str, response: Dict):
        """Step 5: Update conversation context for future queries."""
        try:
            if self.context_manager:
                context_data = {
                    'user_input': user_input,
                    'response_summary': response.get('summary', ''),
                    'intent': response.get('intent'),
                    'timestamp': datetime.now().isoformat()
                }
                await self.context_manager.update_conversation(conversation_id, context_data)
                logger.info(f"Context updated for conversation: {conversation_id}")
        except Exception as e:
            logger.warning(f"Context update failed: {e}")

    def _normalize_entities_for_mock(self, entities: Any) -> Dict[str, List[str]]:
        """Convert mixed entity formats into the structure expected by the mock generator."""
        if not entities:
            return {}

        normalized: Dict[str, List[str]] = {}

        # Helper to add a value under a canonical key
        def _add_value(key: str, value: Any) -> None:
            if not key or value in (None, ""):
                return

            canonical_map = {
                'username': 'user',
                'user.name': 'user',
                'user_id': 'user',
                'account': 'user',
                'ip': 'ip_address',
                'src_ip': 'ip_address',
                'source_ip': 'ip_address',
                'destination_ip': 'ip_address',
            }

            canonical_key = canonical_map.get(key.lower(), key)

            normalized.setdefault(canonical_key, []).append(str(value))

        if isinstance(entities, dict):
            for key, value in entities.items():
                if isinstance(value, (list, tuple, set)):
                    for item in value:
                        _add_value(str(key), item)
                else:
                    _add_value(str(key), value)
            return normalized

        for entity in entities:
            if not entity:
                continue

            if isinstance(entity, dict):
                entity_type = entity.get('type') or entity.get('entity_type') or entity.get('label')
                entity_value = entity.get('value') or entity.get('text') or entity.get('content')
            else:
                entity_type = getattr(entity, 'type', None) or getattr(entity, 'entity_type', None) or getattr(entity, 'label', None)
                entity_value = getattr(entity, 'value', None) or getattr(entity, 'text', None) or getattr(entity, 'content', None)

            _add_value(str(entity_type) if entity_type else '', entity_value)

        return normalized
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Retrieve conversation history for a given conversation ID."""
        try:
            if self.context_manager:
                history = await self.context_manager.get_conversation_history(conversation_id)
                return history or []
            return []
        except Exception as e:
            logger.warning(f"Failed to retrieve conversation history: {e}")
            return []
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all pipeline components."""
        components = {
            'intent_classifier': self.intent_classifier is not None,
            'entity_extractor': self.entity_extractor is not None,
            'query_builder': self.query_builder is not None,
            'elastic_connector': self.elastic_connector is not None,
            'wazuh_connector': self.wazuh_connector is not None,
            'response_formatter': self.response_formatter is not None,
            'context_manager': self.context_manager is not None
        }
        
        healthy_count = sum(1 for status in components.values() if status)
        total_count = len(components)
        
        return {
            'is_initialized': self.is_initialized,
            'components': components,
            'health_score': f"{healthy_count}/{total_count}",
            'status': 'healthy' if healthy_count >= total_count * 0.8 else 'degraded'
        }

# Convenience function for quick pipeline access
async def create_pipeline(config: Optional[Dict] = None) -> ConversationalPipeline:
    """Create and initialize a new ConversationalPipeline instance."""
    pipeline = ConversationalPipeline(config)
    await pipeline.initialize()
    return pipeline
# --- From siem_connector/query_processor.py ---
"""
SIEM Query Processor
Integrates Query Builder with SIEM Connectors for complete query processing pipeline.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import time

# Import project components
from .elastic_connector import ElasticConnector
from .wazuh_connector import WazuhConnector  
from .utils import (
    normalize_log_entry, extract_common_fields, sanitize_query_response,
    validate_query_dsl, build_error_response, convert_to_dataframe
)

logger = logging.getLogger(__name__)


class SIEMQueryProcessor:
    """Main processor that orchestrates query building and execution."""
    
    def __init__(self, siem_platform: str = "elasticsearch"):
        """
        Initialize SIEM Query Processor.
        
        Args:
            siem_platform: Target SIEM platform (elasticsearch, wazuh)
        """
        self.platform = siem_platform.lower()
        self.connector = None
        
        # Initialize appropriate connector
        if self.platform == "elasticsearch":
            try:
                self.connector = ElasticConnector()
                logger.info("Elasticsearch connector initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Elasticsearch connector: {e}")
                
        elif self.platform == "wazuh":
            try:
                self.connector = WazuhConnector()
                logger.info("Wazuh connector initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Wazuh connector: {e}")
        
        else:
            raise ValueError(f"Unsupported SIEM platform: {siem_platform}")
    
    def process_query(self, query_dsl: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process a query through the SIEM connector.
        
        Args:
            query_dsl: Elasticsearch DSL or platform-specific query
            **kwargs: Additional parameters (size, index, etc.)
            
        Returns:
            Processed and normalized response
        """
        start_time = time.time()
        
        try:
            # Validate query structure
            is_valid, validation_message = validate_query_dsl(query_dsl)
            if not is_valid:
                logger.error(f"Invalid query: {validation_message}")
                return build_error_response(f"Invalid query: {validation_message}")
            
            if not self.connector:
                raise ConnectionError(f"No connector available for platform: {self.platform}")
            
            # Execute query based on platform
            if self.platform == "elasticsearch":
                response = self._process_elasticsearch_query(query_dsl, **kwargs)
            elif self.platform == "wazuh":
                response = self._process_wazuh_query(query_dsl, **kwargs)
            else:
                raise ValueError(f"Unsupported platform: {self.platform}")
            
            # Add execution metadata
            execution_time = time.time() - start_time
            response['metadata']['execution_time'] = execution_time
            response['metadata']['platform'] = self.platform
            response['metadata']['processed_at'] = datetime.now().isoformat()
            
            # Sanitize response
            response = sanitize_query_response(response)
            
            logger.info(f"Query processed successfully in {execution_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return build_error_response(str(e), str(query_dsl))
    
    def _process_elasticsearch_query(self, query_dsl: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process query through Elasticsearch connector."""
        size = kwargs.get('size', 100)
        index = kwargs.get('index')
        
        # Use enhanced send_query_to_elastic method
        response = self.connector.send_query_to_elastic(query_dsl, index=index, size=size)
        
        # Extract and normalize hits
        normalized_hits = []
        for hit in response['hits']:
            normalized_hit = normalize_log_entry(hit, 'elasticsearch')
            normalized_hits.append(normalized_hit)
        
        # Add summary statistics
        summary = extract_common_fields(normalized_hits)
        response['summary'] = summary
        
        return response
    
    def _process_wazuh_query(self, query_dsl: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process query through Wazuh connector."""
        # Convert Elasticsearch DSL to Wazuh API format if needed
        # This is a simplified implementation
        size = kwargs.get('size', 100)
        
        try:
            # For now, use a basic search endpoint
            # In practice, you'd convert the DSL to appropriate Wazuh API calls
            response = self.connector.search_alerts(
                limit=size,
                sort="-timestamp"
            )
            
            # Normalize response to match Elasticsearch format
            normalized_response = {
                'hits': [],
                'aggregations': {},
                'metadata': {
                    'total_hits': len(response.get('data', [])),
                    'platform': 'wazuh'
                }
            }
            
            # Process Wazuh alerts
            for alert in response.get('data', []):
                normalized_hit = normalize_log_entry(alert, 'wazuh')
                normalized_response['hits'].append({
                    'id': alert.get('id'),
                    'source': normalized_hit,
                    'score': 1.0  # Wazuh doesn't have scoring like Elasticsearch
                })
            
            return normalized_response
            
        except Exception as e:
            logger.error(f"Wazuh query processing failed: {e}")
            raise
    
    def fetch_alerts(self, severity: Optional[str] = None, 
                    time_range: Optional[str] = "last_hour", **kwargs) -> Dict[str, Any]:
        """Fetch security alerts from SIEM platform."""
        try:
            if self.platform == "elasticsearch":
                return self.connector.fetch_alerts(severity=severity, time_range=time_range, **kwargs)
            elif self.platform == "wazuh":
                return self._fetch_wazuh_alerts(severity=severity, time_range=time_range, **kwargs)
            else:
                raise ValueError(f"Alert fetching not supported for platform: {self.platform}")
                
        except Exception as e:
            logger.error(f"Failed to fetch alerts: {e}")
            return build_error_response(f"Failed to fetch alerts: {e}")
    
    def fetch_logs(self, log_type: Optional[str] = None, 
                  time_range: Optional[str] = "last_hour", **kwargs) -> Dict[str, Any]:
        """Fetch logs from SIEM platform."""
        try:
            if self.platform == "elasticsearch":
                return self.connector.fetch_logs(log_type=log_type, time_range=time_range, **kwargs)
            elif self.platform == "wazuh":
                return self._fetch_wazuh_logs(log_type=log_type, time_range=time_range, **kwargs)
            else:
                raise ValueError(f"Log fetching not supported for platform: {self.platform}")
                
        except Exception as e:
            logger.error(f"Failed to fetch logs: {e}")
            return build_error_response(f"Failed to fetch logs: {e}")
    
    def _fetch_wazuh_alerts(self, severity: Optional[str] = None, 
                           time_range: Optional[str] = "last_hour", **kwargs) -> Dict[str, Any]:
        """Fetch alerts from Wazuh."""
        # Implementation would depend on Wazuh API capabilities
        # This is a placeholder for the actual implementation
        try:
            params = {
                'limit': kwargs.get('size', 100),
                'sort': '-timestamp'
            }
            
            if severity:
                severity_map = {'low': '1-3', 'medium': '4-6', 'high': '7-9', 'critical': '10-15'}
                if severity.lower() in severity_map:
                    params['rule.level'] = severity_map[severity.lower()]
            
            response = self.connector.get_alerts(**params)
            
            # Normalize to standard format
            normalized_response = {
                'hits': [],
                'aggregations': {},
                'metadata': {
                    'total_hits': len(response.get('data', [])),
                    'platform': 'wazuh',
                    'query_type': 'alerts'
                }
            }
            
            for alert in response.get('data', []):
                normalized_response['hits'].append({
                    'id': alert.get('id'),
                    'source': normalize_log_entry(alert, 'wazuh'),
                    'score': alert.get('rule', {}).get('level', 1)
                })
            
            return normalized_response
            
        except Exception as e:
            logger.error(f"Wazuh alert fetching failed: {e}")
            raise
    
    def _fetch_wazuh_logs(self, log_type: Optional[str] = None, 
                         time_range: Optional[str] = "last_hour", **kwargs) -> Dict[str, Any]:
        """Fetch logs from Wazuh."""
        # Similar implementation for Wazuh logs
        # This would use appropriate Wazuh API endpoints
        try:
            # Placeholder implementation
            response = self.connector.search_logs(
                limit=kwargs.get('size', 100),
                log_type=log_type
            )
            
            normalized_response = {
                'hits': [],
                'aggregations': {},
                'metadata': {
                    'total_hits': len(response.get('data', [])),
                    'platform': 'wazuh',
                    'query_type': 'logs'
                }
            }
            
            for log in response.get('data', []):
                normalized_response['hits'].append({
                    'id': log.get('id'),
                    'source': normalize_log_entry(log, 'wazuh'),
                    'score': 1.0
                })
            
            return normalized_response
            
        except Exception as e:
            logger.error(f"Wazuh log fetching failed: {e}")
            raise
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of SIEM platform."""
        try:
            if not self.connector:
                return {
                    'status': 'disconnected',
                    'platform': self.platform,
                    'error': 'No connector available'
                }
            
            if self.platform == "elasticsearch":
                health = self.connector.get_cluster_health()
                return {
                    'status': health.get('status', 'unknown'),
                    'platform': self.platform,
                    'details': health
                }
            elif self.platform == "wazuh":
                # Check Wazuh connection
                try:
                    info = self.connector.get_manager_info()
                    return {
                        'status': 'green' if info else 'red',
                        'platform': self.platform,
                        'details': info
                    }
                except:
                    return {
                        'status': 'red',
                        'platform': self.platform,
                        'error': 'Connection failed'
                    }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'error',
                'platform': self.platform,
                'error': str(e)
            }
    
    def get_available_indices(self) -> List[str]:
        """Get list of available indices/data sources."""
        try:
            if self.platform == "elasticsearch":
                return self.connector.get_indices()
            elif self.platform == "wazuh":
                # Wazuh doesn't have indices like Elasticsearch
                # Return available data types instead
                return ['alerts', 'logs', 'agents', 'rules']
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get indices: {e}")
            return []
    
    def convert_results_to_dataframe(self, response: Dict[str, Any]) -> Any:
        """Convert query results to pandas DataFrame."""
        try:
            hits = response.get('hits', [])
            if not hits:
                return None
            
            # Extract source data from hits
            sources = [hit.get('source', {}) for hit in hits]
            return convert_to_dataframe(sources)
            
        except Exception as e:
            logger.error(f"DataFrame conversion failed: {e}")
            return None


# Factory function for easier initialization
def create_siem_processor(platform: str = "elasticsearch") -> SIEMQueryProcessor:
    """Create a SIEM Query Processor instance."""
    return SIEMQueryProcessor(platform)


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    processor = create_siem_processor("elasticsearch")
    
    # Example query
    sample_query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"event.type": "authentication"}}
                ]
            }
        },
        "size": 10
    }
    
    print("SIEM Query Processor Test")
    print("=" * 50)
    
    # Test health status
    health = processor.get_health_status()
    print(f"Health Status: {health['status']}")
    
    # Test query processing
    try:
        response = processor.process_query(sample_query)
        print(f"Query Results: {response['metadata']['total_hits']} hits")
        
        # Test DataFrame conversion
        df = processor.convert_results_to_dataframe(response)
        if df is not None:
            print(f"DataFrame Shape: {df.shape}")
        
    except Exception as e:
        print(f"Query test failed: {e}")
    
    # Test alert fetching
    try:
        alerts = processor.fetch_alerts(severity="high", time_range="last_hour")
        print(f"Alerts: {alerts['metadata']['total_hits']} found")
    except Exception as e:
        print(f"Alert fetch failed: {e}")
# --- From backend/query_builder.py ---
"""
Query Builder for SIEM NLP
Converts natural language queries to Elasticsearch DSL/KQL queries.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
import os
from pathlib import Path
import yaml

# Import NLP components with error handling
try:
    from nlp.intent_classifier import QueryIntent, IntentClassifier
    from nlp.entity_extractor import EntityExtractor, Entity
except ImportError:
    # Fallback for different import contexts
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from nlp.intent_classifier import QueryIntent, IntentClassifier
    from nlp.entity_extractor import EntityExtractor, Entity

logger = logging.getLogger(__name__)


class QueryBuilder:
    """Converts natural language to Elasticsearch queries."""
    
    def __init__(self):
        """Initialize the query builder."""
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()

        # Optional index class hint and external field mappings
        self.index_class = os.getenv('INDEX_CLASS', '').strip().lower()
        self.external_mappings = self._load_index_mappings()
        
        # Event ID mappings for common security events
        self.event_id_mappings = {
            # Windows Security Events
            '4624': 'successful_login',
            '4625': 'failed_login', 
            '4634': 'logoff',
            '4648': 'explicit_login',
            '4720': 'account_created',
            '4726': 'account_deleted',
            '4740': 'account_locked',
            '4767': 'account_unlocked',
            '4771': 'kerberos_preauth_failed',
            '4776': 'credential_validation',
            '5156': 'network_connection_allowed',
            '5157': 'network_connection_blocked',
            
            # System Events
            '7034': 'service_crashed',
            '7035': 'service_control',
            '7036': 'service_state_change',
            '1074': 'system_shutdown',
            
            # Application Events
            '1000': 'application_error',
            '1001': 'application_hang',
        }
        
        # Field mappings for different log sources
        self.field_mappings = {
            'windows': {
                'username': ['winlog.event_data.TargetUserName', 'user.name', 'winlog.user.name'],
                'source_ip': ['source.ip', 'winlog.event_data.IpAddress'],
                'event_id': ['winlog.event_id', 'event.code'],
                'timestamp': ['@timestamp', 'winlog.time_created'],
                'hostname': ['host.name', 'winlog.computer_name'],
                'process': ['process.name', 'winlog.event_data.ProcessName'],
                'message': ['message', 'winlog.event_data.Message']
            },
            'linux': {
                'username': ['user.name', 'system.auth.user'],
                'source_ip': ['source.ip'],
                'timestamp': ['@timestamp'],
                'hostname': ['host.name'],
                'process': ['process.name', 'system.process.name'],
                'message': ['message']
            },
            'network': {
                'source_ip': ['source.ip'],
                'dest_ip': ['destination.ip'],
                'source_port': ['source.port'],
                'dest_port': ['destination.port'],
                'protocol': ['network.protocol'],
                'timestamp': ['@timestamp']
            }
        }
    
    async def build_query(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert natural language query to Elasticsearch DSL.
        
        Args:
            query_params: Dictionary containing:
                - raw_text: Natural language query string
                - intent: Optional pre-classified intent
                - entities: Optional pre-extracted entities
            
        Returns:
            Elasticsearch DSL query dictionary
        """
        # Extract params
        natural_query = query_params.get('raw_text', '')
        pre_intent = query_params.get('intent')
        pre_entities = query_params.get('entities', [])
        index_pattern = query_params.get('index_pattern', 'logs-*')
        filters = query_params.get('filters') or {}
        request_index_class = None
        try:
            if isinstance(filters, dict) and filters.get('index_class'):
                request_index_class = str(filters.get('index_class')).strip().lower()
        except Exception:
            request_index_class = None
        
        # Use pre-classified intent or classify now
        if pre_intent and isinstance(pre_intent, str):
            intent_str = pre_intent
            # Try to get enum value
            try:
                from backend.nlp.intent_classifier import QueryIntent
                intent = QueryIntent(intent_str) if hasattr(QueryIntent, intent_str.upper()) else None
            except:
                intent = None
            confidence = query_params.get('confidence', 0.5)
        else:
            intent, confidence = self.intent_classifier.classify_intent(natural_query)
        
        # Use pre-extracted entities or extract now
        if pre_entities and isinstance(pre_entities, list):
            entities = pre_entities
        else:
            entities = self.entity_extractor.extract_entities(natural_query)
        
        entity_summary = self.entity_extractor.get_entity_summary(entities)
        
        # Extract time range
        time_range = self.entity_extractor.extract_time_range(natural_query)
        
        # Get intent string safely
        intent_str = intent.value if (intent and hasattr(intent, 'value')) else (pre_intent or 'unknown')
        
        logger.info(f"Building query for intent: {intent_str}, entities: {entity_summary}")
        
        # Build base query structure
        query = {
            "query": {
                "bool": {
                    "must": [],
                    "should": [],
                    "filter": [],
                    "must_not": []
                }
            },
            "sort": [
                {"@timestamp": {"order": "desc"}}
            ],
            "size": 100
        }
        
        # Add intent-specific query components
        self._add_intent_filters(query, intent, entities, entity_summary)
        
        # Add entity-based filters
        self._add_entity_filters(query, entities, entity_summary, index_class_override=request_index_class)
        
        # Add time range filter (with fallback default and UI override)
        # UI override: filters.time_window_gte
        if isinstance(filters, dict) and filters.get('time_window_gte'):
            try:
                gte = str(filters.get('time_window_gte'))
                query['query']['bool'].setdefault('filter', []).append({
                    'range': {
                        '@timestamp': {
                            'gte': gte
                        }
                    }
                })
            except Exception:
                # fallback to parsed or default
                pass
        elif time_range and time_range.get('start_time'):
            self._add_time_filter(query, time_range)
        else:
            # Fallback default window (e.g., now-1d)
            default_window = os.getenv('ASSISTANT_DEFAULT_TIME_WINDOW', 'now-1d')
            query['query']['bool'].setdefault('filter', []).append({
                'range': {
                    '@timestamp': {
                        'gte': default_window
                    }
                }
            })

        # Severity override from UI filters (Critical/High/Medium/Low)
        if isinstance(filters, dict) and filters.get('severity') and str(filters.get('severity')).lower() != 'all':
            sev = str(filters.get('severity')).lower()
            sev_map_min = {
                'critical': 10,
                'high': 8,
                'medium': 5,
                'low': 3,
                'info': 1
            }
            if sev in sev_map_min:
                query['query']['bool'].setdefault('filter', []).append({
                    'range': {
                        'event.severity': {
                            'gte': sev_map_min[sev]
                        }
                    }
                })
        
        # Apply pagination/size caps
        max_size = int(os.getenv('ASSISTANT_MAX_RESULTS', '200'))
        requested_size = int(query_params.get('limit', query.get('size', 100)))
        query['size'] = min(requested_size, max_size)
        if 'offset' in query_params:
            try:
                offset = max(0, int(query_params.get('offset', 0)))
                query['from'] = offset
            except Exception:
                pass
        
        # Add aggregations for relevant intents
        self._add_aggregations(query, intent, entities)
        
        # Clean up empty bool clauses
        self._cleanup_bool_query(query)
        
        return query
    
    def _add_intent_filters(self, query: Dict[str, Any], intent: QueryIntent, 
                           entities: List[Entity], entity_summary: Dict[str, List[str]]):
        """Add filters based on classified intent."""
        bool_query = query["query"]["bool"]
        
        if intent == QueryIntent.SHOW_FAILED_LOGINS:
            # Add failed login specific filters
            bool_query["should"].extend([
                {"term": {"winlog.event_id": "4625"}},
                {"term": {"event.code": "4625"}},
                {"match": {"message": "authentication failed"}},
                {"match": {"message": "login failed"}},
                {"match": {"event.action": "logon-failed"}},
                {"term": {"event.outcome": "failure"}}
            ])
            bool_query["minimum_should_match"] = 1
            
        elif intent == QueryIntent.SHOW_SUCCESSFUL_LOGINS:
            bool_query["should"].extend([
                {"term": {"winlog.event_id": "4624"}},
                {"term": {"event.code": "4624"}},
                {"match": {"message": "authentication successful"}},
                {"match": {"message": "login successful"}},
                {"match": {"event.action": "logon"}},
                {"term": {"event.outcome": "success"}}
            ])
            bool_query["minimum_should_match"] = 1
            
        elif intent == QueryIntent.SECURITY_ALERTS:
            bool_query["should"].extend([
                {"range": {"event.severity": {"gte": 7}}},
                {"terms": {"event.type": ["alert", "security", "threat"]}},
                {"match": {"message": "security"}},
                {"match": {"message": "alert"}},
                {"match": {"tags": "security"}}
            ])
            bool_query["minimum_should_match"] = 1
            
        elif intent == QueryIntent.SYSTEM_ERRORS:
            bool_query["should"].extend([
                {"terms": {"log.level": ["ERROR", "CRITICAL", "FATAL"]}},
                {"match": {"message": "error"}},
                {"match": {"message": "crash"}},
                {"match": {"message": "exception"}},
                {"term": {"event.outcome": "failure"}}
            ])
            bool_query["minimum_should_match"] = 1
            
        elif intent == QueryIntent.NETWORK_TRAFFIC:
            bool_query["should"].extend([
                {"exists": {"field": "source.ip"}},
                {"exists": {"field": "destination.ip"}},
                {"exists": {"field": "network.protocol"}},
                {"match": {"event.category": "network"}}
            ])
            bool_query["minimum_should_match"] = 1
            
        elif intent == QueryIntent.MALWARE_DETECTION:
            bool_query["should"].extend([
                {"match": {"message": "malware"}},
                {"match": {"message": "virus"}},
                {"match": {"message": "trojan"}},
                {"match": {"message": "threat"}},
                {"match": {"event.type": "malware"}},
                {"match": {"tags": "malware"}}
            ])
            bool_query["minimum_should_match"] = 1
    
    def _add_entity_filters(self, query: Dict[str, Any], entities: List[Entity], 
                           entity_summary: Dict[str, List[str]], index_class_override: Optional[str] = None):
        """Add filters based on extracted entities."""
        bool_query = query["query"]["bool"]
        
        # Helper: return preferred fields from external mappings (if provided) or sensible defaults
        def preferred(kind: str, defaults: List[str]) -> List[str]:
            # kind examples: 'username', 'source_ip', 'dest_ip', 'event_id', 'process', 'file.path'
            results = []
            selected_class = (index_class_override or self.index_class)
            if self.external_mappings and selected_class:
                cls = self.external_mappings.get(selected_class, {})
                if kind in cls:
                    results.extend([f for f in cls.get(kind, []) if isinstance(f, str)])
            # Append defaults ensuring uniqueness
            for f in defaults:
                if f not in results:
                    results.append(f)
            return results

        # IP Address filters
        if 'ip_address' in entity_summary:
            ip_filters = []
            # gather candidate ip fields
            ip_fields = (
                preferred('source_ip', ['source.ip', 'client.ip', 'host.ip'])
                + preferred('destination_ip', ['destination.ip', 'server.ip'])
            )
            for ip in entity_summary['ip_address']:
                for f in ip_fields:
                    ip_filters.append({"term": {f: ip}})
            if ip_filters:
                bool_query.setdefault("should", []).extend(ip_filters)
                if not bool_query.get("minimum_should_match"):
                    bool_query["minimum_should_match"] = 1
        
        # Username filters
        if 'username' in entity_summary:
            username_filters = []
            user_fields = preferred('username', ['user.name', 'winlog.event_data.TargetUserName', 'system.auth.user'])
            for username in entity_summary['username']:
                for f in user_fields:
                    # exact via .keyword if applicable, else wildcard
                    username_filters.append({"term": {f + (".keyword" if not f.endswith('.keyword') else ""): username}})
                    username_filters.append({"wildcard": {f: f"*{username}*"}})
                username_filters.append({"match": {"message": username}})
            if username_filters:
                bool_query.setdefault("should", []).extend(username_filters)
                if not bool_query.get("minimum_should_match"):
                    bool_query["minimum_should_match"] = 1
        
        # Event ID filters
        if 'event_id' in entity_summary:
            for event_id in entity_summary['event_id']:
                bool_query["must"].extend([
                    {
                        "bool": {
                            "should": [
                                {"term": {"winlog.event_id": event_id}},
                                {"term": {"event.code": event_id}},
                                {"term": {"event.id": event_id}}
                            ]
                        }
                    }
                ])
        
        # Port filters
        if 'port' in entity_summary:
            port_filters = []
            for port in entity_summary['port']:
                port_filters.extend([
                    {"term": {"source.port": int(port)}},
                    {"term": {"destination.port": int(port)}},
                    {"term": {"network.port": int(port)}}
                ])
            
            if port_filters:
                bool_query["should"].extend(port_filters)
                if not bool_query.get("minimum_should_match"):
                    bool_query["minimum_should_match"] = 1
        
        # Domain filters
        if 'domain' in entity_summary:
            domain_filters = []
            domain_fields = preferred('domain', ['url.domain', 'dns.question.name'])
            for domain in entity_summary['domain']:
                for f in domain_fields:
                    domain_filters.append({"match": {f: domain}})
                domain_filters.append({"match": {"message": domain}})
            
            if domain_filters:
                bool_query.setdefault("should", []).extend(domain_filters)
        
        # Process name filters
        if 'process_name' in entity_summary:
            process_filters = []
            process_fields = preferred('process', ['process.name', 'winlog.event_data.ProcessName', 'process.executable'])
            for process in entity_summary['process_name']:
                for f in process_fields:
                    matcher = {"wildcard": {f: f"*{process}*"}} if f.endswith('executable') else {"match": {f: process}}
                    process_filters.append(matcher)
            
            if process_filters:
                bool_query.setdefault("should", []).extend(process_filters)
        
        # File path filters
        if 'file_path' in entity_summary:
            file_filters = []
            file_fields = preferred('file.path', ['file.path', 'winlog.event_data.ObjectName'])
            for file_path in entity_summary['file_path']:
                for f in file_fields:
                    file_filters.append({"match": {f: file_path}})
                file_filters.append({"wildcard": {"file.path.keyword": f"*{file_path}*"}})
            
            if file_filters:
                bool_query.setdefault("should", []).extend(file_filters)
        
        # Severity filters
        if 'severity' in entity_summary:
            for severity in entity_summary['severity']:
                severity_map = {
                    'critical': 10,
                    'high': 8, 
                    'medium': 5,
                    'low': 3,
                    'info': 1
                }
                
                if severity.lower() in severity_map:
                    bool_query["filter"].append({
                        "range": {
                            "event.severity": {
                                "gte": severity_map[severity.lower()]
                            }
                        }
                    })
    
    def _add_time_filter(self, query: Dict[str, Any], time_range: Dict[str, Any]):
        """Add time range filter to query."""
        if not time_range:
            return
        
        time_filter = {"range": {"@timestamp": {}}}
        
        if time_range.get('start_time'):
            if time_range.get('relative', False):
                # Use relative time for better performance
                if 'Last' in time_range.get('description', ''):
                    desc = time_range['description'].lower()
                    if 'hour' in desc:
                        time_filter["range"]["@timestamp"]["gte"] = "now-1h"
                    elif 'day' in desc:
                        time_filter["range"]["@timestamp"]["gte"] = "now-1d"
                    elif 'week' in desc:
                        time_filter["range"]["@timestamp"]["gte"] = "now-1w"
                    elif 'month' in desc:
                        time_filter["range"]["@timestamp"]["gte"] = "now-1M"
                    else:
                        time_filter["range"]["@timestamp"]["gte"] = "now-1h"
                elif time_range['description'].lower() == 'today':
                    time_filter["range"]["@timestamp"]["gte"] = "now/d"
                elif time_range['description'].lower() == 'yesterday':
                    time_filter["range"]["@timestamp"]["gte"] = "now-1d/d"
                    time_filter["range"]["@timestamp"]["lte"] = "now/d"
            else:
                # Use absolute timestamp
                time_filter["range"]["@timestamp"]["gte"] = time_range['start_time'].isoformat()
        
        if time_range.get('end_time') and not time_range.get('relative', False):
            time_filter["range"]["@timestamp"]["lte"] = time_range['end_time'].isoformat()
        
        query["query"]["bool"]["filter"].append(time_filter)
    
    def _add_aggregations(self, query: Dict[str, Any], intent: QueryIntent, entities: List[Entity]):
        """Add aggregations for summary statistics."""
        aggs = {}
        
        if intent in [QueryIntent.SHOW_FAILED_LOGINS, QueryIntent.SHOW_SUCCESSFUL_LOGINS]:
            aggs["users"] = {
                "terms": {
                    "field": "user.name.keyword",
                    "size": 20
                }
            }
            aggs["source_ips"] = {
                "terms": {
                    "field": "source.ip",
                    "size": 20
                }
            }
            aggs["timeline"] = {
                "date_histogram": {
                    "field": "@timestamp",
                    "calendar_interval": "hour"
                }
            }
        
        elif intent == QueryIntent.NETWORK_TRAFFIC:
            aggs["protocols"] = {
                "terms": {
                    "field": "network.protocol",
                    "size": 10
                }
            }
            aggs["top_source_ips"] = {
                "terms": {
                    "field": "source.ip",
                    "size": 20
                }
            }
            aggs["top_dest_ports"] = {
                "terms": {
                    "field": "destination.port",
                    "size": 20
                }
            }
        
        elif intent == QueryIntent.SECURITY_ALERTS:
            aggs["severity_breakdown"] = {
                "terms": {
                    "field": "event.severity",
                    "size": 10
                }
            }
            aggs["alert_types"] = {
                "terms": {
                    "field": "event.type",
                    "size": 20
                }
            }
        
        if aggs:
            query["aggs"] = aggs
    
    def _load_index_mappings(self) -> Dict[str, Any]:
        """Load optional external index mappings YAML (config/index_mappings.yaml)."""
        try:
            cfg_path = Path(__file__).resolve().parents[1] / 'config' / 'index_mappings.yaml'
            if cfg_path.exists():
                with cfg_path.open('r', encoding='utf-8') as fh:
                    return yaml.safe_load(fh) or {}
        except Exception as e:
            logger.warning(f"Index mappings load failed: {e}")
        return {}

    def _cleanup_bool_query(self, query: Dict[str, Any]):
        """Remove empty bool clauses."""
        bool_query = query["query"]["bool"]
        
        # Remove empty clauses
        for clause in ["must", "should", "filter", "must_not"]:
            if not bool_query.get(clause):
                bool_query.pop(clause, None)
        
        # If no clauses, add a match_all query
        if not any(bool_query.get(clause) for clause in ["must", "should", "filter", "must_not"]):
            query["query"] = {"match_all": {}}
    
    def build_kql_query(self, natural_query: str) -> str:
        """
        Convert natural language to KQL (Kibana Query Language).
        
        Args:
            natural_query: Natural language query
            
        Returns:
            KQL query string
        """
        # Classify intent and extract entities
        intent, _ = self.intent_classifier.classify_intent(natural_query)
        entities = self.entity_extractor.extract_entities(natural_query)
        entity_summary = self.entity_extractor.get_entity_summary(entities)
        
        kql_parts = []
        
        # Intent-based KQL
        if intent == QueryIntent.SHOW_FAILED_LOGINS:
            kql_parts.append("(winlog.event_id:4625 OR event.code:4625 OR event.outcome:failure)")
            
        elif intent == QueryIntent.SHOW_SUCCESSFUL_LOGINS:
            kql_parts.append("(winlog.event_id:4624 OR event.code:4624 OR event.outcome:success)")
            
        elif intent == QueryIntent.SECURITY_ALERTS:
            kql_parts.append("(event.type:alert OR event.type:security OR tags:security)")
            
        elif intent == QueryIntent.SYSTEM_ERRORS:
            kql_parts.append("(log.level:ERROR OR log.level:CRITICAL OR event.outcome:failure)")
        
        # Entity-based KQL
        if 'ip_address' in entity_summary:
            ip_conditions = []
            for ip in entity_summary['ip_address']:
                ip_conditions.append(f"(source.ip:{ip} OR destination.ip:{ip} OR client.ip:{ip})")
            kql_parts.append(f"({' OR '.join(ip_conditions)})")
        
        if 'username' in entity_summary:
            user_conditions = []
            for username in entity_summary['username']:
                user_conditions.append(f"user.name:{username}")
            kql_parts.append(f"({' OR '.join(user_conditions)})")
        
        if 'event_id' in entity_summary:
            event_conditions = []
            for event_id in entity_summary['event_id']:
                event_conditions.append(f"(winlog.event_id:{event_id} OR event.code:{event_id})")
            kql_parts.append(f"({' OR '.join(event_conditions)})")
        
        # Combine with AND
        if kql_parts:
            return " AND ".join(kql_parts)
        else:
            return "*"  # Match all if no specific conditions


# Example usage and testing
if __name__ == "__main__":
    builder = QueryBuilder()
    
    test_queries = [
        "Show failed logins from user admin in the last hour",
        "Find security alerts with high severity from 192.168.1.100",
        "Get network traffic on port 443 from yesterday",
        "Show successful logins for john.doe@company.com",
        "Find malware detections in the last 24 hours",
        "List system errors from server.example.com"
    ]
    
    print("Query Builder Test:")
    print("=" * 70)
    
    for natural_query in test_queries:
        print(f"\nNatural Query: {natural_query}")
        
        # Build Elasticsearch DSL
        es_query = builder.build_query(natural_query)
        print("Elasticsearch DSL:")
        import json
        print(json.dumps(es_query, indent=2))
        
        # Build KQL
        kql_query = builder.build_kql_query(natural_query)
        print(f"KQL: {kql_query}")
        
        print("-" * 70)
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
        
        logger.info("ConversationalPipeline initialized")
    
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
            
            self.wazuh_connector = WazuhConnector()
            await self._safe_component_init(
                lambda: None,  # WazuhConnector doesn't have initialize() method
                "Wazuh Connector"
            )
            
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
            query_result = await self._generate_query(nlp_result, user_input)
            
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
                
                logger.info(f"NLP Analysis - Intent: {intent_str}, Entities: {len(entities)}, Confidence: {confidence:.2f}")
                
                return {
                    'intent': intent_str,
                    'entities': entities,
                    'confidence': confidence,
                    'raw_intent': intent
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
    
    async def _generate_query(self, nlp_result: Dict, user_input: str) -> Dict[str, Any]:
        """Step 2: Generate SIEM query from NLP analysis."""
        try:
            if self.query_builder:
                query_params = {
                    'intent': nlp_result.get('intent'),
                    'entities': nlp_result.get('entities', []),
                    'raw_text': user_input
                }
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
            if self.elastic_connector:
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
            
            # Try Wazuh as backup/supplement
            if self.wazuh_connector and len(results) < 50:  # Only if we need more data
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
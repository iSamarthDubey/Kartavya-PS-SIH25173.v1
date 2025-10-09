"""
Conversational Pipeline
Main orchestrator that connects all NLP and SIEM components
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationalPipeline:
    """
    Main pipeline that orchestrates the entire NLP to SIEM flow
    """
    
    def __init__(self):
        """Initialize the pipeline components"""
        self.intent_classifier = None
        self.entity_extractor = None
        self.schema_mapper = None
        self.query_builder = None
        self.query_validator = None
        self.ambiguity_resolver = None
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize all pipeline components"""
        try:
            # Import components
            from .nlp.intent_classifier import IntentClassifier
            from .nlp.entity_extractor import EntityExtractor
            from .nlp.schema_mapper import SchemaMapper
            from .query.builder import QueryBuilder
            from .query.validator import QueryValidator
            
            # Initialize components
            self.intent_classifier = IntentClassifier()
            self.entity_extractor = EntityExtractor()
            self.schema_mapper = SchemaMapper()
            self.query_builder = QueryBuilder()
            self.query_validator = QueryValidator()
            
            self.initialized = True
            logger.info("Pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            self.initialized = False
            raise
    
    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a natural language query through the pipeline
        
        Args:
            query: Natural language query
            context: Conversation context
            user_context: User-specific context
            filters: Additional filters
            
        Returns:
            Processed result dictionary
        """
        if not self.initialized:
            await self.initialize()
        
        start_time = time.time()
        result = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "processing_time": 0
        }
        
        try:
            # Step 1: Intent Classification
            intent, confidence = self.intent_classifier.classify_intent(query)
            result["intent"] = intent.value if hasattr(intent, 'value') else str(intent)
            result["confidence"] = confidence
            
            # Step 2: Entity Extraction
            raw_entities = self.entity_extractor.extract_entities(query)
            # Convert Entity objects to dictionaries for consistent processing
            entities = [entity.to_dict() for entity in raw_entities]
            result["entities"] = entities
            
            # Step 3: Check for ambiguities
            if await self._has_ambiguities(query, entities):
                clarifications = await self._get_clarifications(query, entities)
                result["needs_clarification"] = True
                result["clarifications"] = clarifications
                return result
            
            # Step 4: Apply context if available
            if context and context.get("history"):
                entities = await self._apply_context(entities, context)
            
            # Step 5: Schema mapping
            field_mappings = await self.schema_mapper.map_entities(entities)
            result["field_mappings"] = field_mappings
            
            # Step 6: Build query
            siem_query = await self.build_query(
                intent=result["intent"],
                entities=entities,
                field_mappings=field_mappings,
                context=context
            )
            result["siem_query"] = siem_query
            
            # Step 7: Validate query
            is_valid, validation_error = await self.validate_query(siem_query)
            result["query_valid"] = is_valid
            if not is_valid:
                result["validation_error"] = validation_error
            
            # Calculate processing time
            result["processing_time"] = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline processing error: {e}")
            result["error"] = str(e)
            result["processing_time"] = time.time() - start_time
            return result
    
    async def build_query(
        self,
        intent: str,
        entities: List[Dict[str, Any]],
        field_mappings: Dict[str, List[str]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build SIEM query from processed components
        
        Args:
            intent: Query intent
            entities: Extracted entities
            field_mappings: Schema field mappings
            context: Conversation context
            
        Returns:
            SIEM query dictionary
        """
        if not self.query_builder:
            from .query.builder import QueryBuilder
            self.query_builder = QueryBuilder()
        
        return await self.query_builder.build(
            intent=intent,
            entities=entities,
            field_mappings=field_mappings,
            context=context
        )
    
    async def validate_query(
        self,
        query: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a query for safety and performance
        
        Args:
            query: Query to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.query_validator:
            from .query.validator import QueryValidator
            self.query_validator = QueryValidator()
        
        return await self.query_validator.validate(query)
    
    async def format_results(
        self,
        results: Dict[str, Any],
        query_type: str
    ) -> List[Dict[str, Any]]:
        """
        Format SIEM results for presentation
        
        Args:
            results: Raw SIEM results
            query_type: Type of query/intent
            
        Returns:
            Formatted results list
        """
        formatted = []
        
        # Extract hits from Elasticsearch-style response
        if "hits" in results:
            hits = results["hits"].get("hits", [])
            for hit in hits:
                source = hit.get("_source", {})
                formatted_item = self._format_event(source, query_type)
                formatted.append(formatted_item)
        
        return formatted
    
    def _format_event(self, event: Dict[str, Any], query_type: str) -> Dict[str, Any]:
        """Format a single event based on query type"""
        formatted = {
            "timestamp": event.get("@timestamp", ""),
            "message": event.get("message", ""),
            "severity": event.get("event", {}).get("severity", "unknown")
        }
        
        # Add specific fields based on query type
        if "authentication" in query_type or "login" in query_type:
            formatted.update({
                "user": event.get("source", {}).get("user", {}).get("name", ""),
                "source_ip": event.get("source", {}).get("ip", ""),
                "outcome": event.get("event", {}).get("outcome", ""),
                "host": event.get("host", {}).get("name", "")
            })
        elif "malware" in query_type or "threat" in query_type:
            formatted.update({
                "threat_name": event.get("threat", {}).get("indicator", {}).get("name", ""),
                "threat_type": event.get("threat", {}).get("indicator", {}).get("type", ""),
                "host": event.get("host", {}).get("name", ""),
                "file_path": event.get("file", {}).get("path", "")
            })
        elif "network" in query_type:
            formatted.update({
                "source_ip": event.get("source", {}).get("ip", ""),
                "dest_ip": event.get("destination", {}).get("ip", ""),
                "protocol": event.get("network", {}).get("protocol", ""),
                "bytes": event.get("network", {}).get("bytes", 0)
            })
        
        return formatted
    
    async def generate_summary(
        self,
        results: List[Dict[str, Any]],
        query: str,
        intent: str
    ) -> str:
        """
        Generate a natural language summary of results
        
        Args:
            results: Formatted results
            query: Original query
            intent: Query intent
            
        Returns:
            Natural language summary
        """
        if not results:
            return "No results found for your query."
        
        count = len(results)
        
        # Generate summary based on intent
        if "failed_login" in intent or "authentication_failure" in intent:
            unique_users = len(set(r.get("user", "") for r in results if r.get("user")))
            unique_ips = len(set(r.get("source_ip", "") for r in results if r.get("source_ip")))
            return f"Found {count} failed login attempts from {unique_users} users and {unique_ips} IP addresses."
        
        elif "malware" in intent or "threat" in intent:
            unique_threats = len(set(r.get("threat_name", "") for r in results if r.get("threat_name")))
            affected_hosts = len(set(r.get("host", "") for r in results if r.get("host")))
            return f"Detected {count} malware events involving {unique_threats} threats on {affected_hosts} hosts."
        
        elif "network" in intent:
            total_bytes = sum(r.get("bytes", 0) for r in results)
            unique_sources = len(set(r.get("source_ip", "") for r in results if r.get("source_ip")))
            return f"Found {count} network events from {unique_sources} sources, totaling {total_bytes:,} bytes."
        
        else:
            return f"Found {count} events matching your query."
    
    async def create_visualizations(
        self,
        data: List[Dict[str, Any]],
        query_type: str
    ) -> List[Dict[str, Any]]:
        """
        Create visualization specifications for the data
        
        Args:
            data: Data to visualize
            query_type: Type of query
            
        Returns:
            List of visualization specifications
        """
        visualizations = []
        
        if not data:
            return visualizations
        
        # Time series visualization
        if any("timestamp" in item for item in data):
            visualizations.append({
                "type": "time_series",
                "title": "Events Over Time",
                "x_field": "timestamp",
                "y_field": "count",
                "chart_type": "line"
            })
        
        # Top entities visualization
        if "authentication" in query_type:
            visualizations.append({
                "type": "bar_chart",
                "title": "Top Failed Login Users",
                "field": "user",
                "limit": 10
            })
        elif "malware" in query_type:
            visualizations.append({
                "type": "pie_chart",
                "title": "Threat Distribution",
                "field": "threat_name",
                "limit": 10
            })
        
        return visualizations
    
    async def generate_suggestions(
        self,
        current_query: str,
        results: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Generate follow-up query suggestions
        
        Args:
            current_query: Current query
            results: Current results
            context: Conversation context
            
        Returns:
            List of suggested queries
        """
        suggestions = []
        
        if results:
            # Suggest filtering
            suggestions.append(f"Filter only critical events")
            
            # Suggest time-based queries
            suggestions.append(f"Show me the same for the last hour")
            
            # Suggest drill-down
            if any("user" in r for r in results):
                suggestions.append(f"Show details for the top user")
            
            if any("source_ip" in r for r in results):
                suggestions.append(f"What else came from those IPs?")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def _has_ambiguities(
        self,
        query: str,
        entities: List[Dict[str, Any]]
    ) -> bool:
        """Check if query has ambiguities"""
        ambiguous_terms = ["recent", "unusual", "suspicious", "last week"]
        query_lower = query.lower()
        
        return any(term in query_lower for term in ambiguous_terms)
    
    async def _get_clarifications(
        self,
        query: str,
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get clarification options for ambiguous query"""
        clarifications = {}
        query_lower = query.lower()
        
        if "recent" in query_lower:
            clarifications["recent"] = {
                "question": "What time period do you mean by 'recent'?",
                "options": ["Last hour", "Last 24 hours", "Last 7 days", "Last month"]
            }
        
        if "unusual" in query_lower or "suspicious" in query_lower:
            clarifications["unusual"] = {
                "question": "What kind of unusual activity?",
                "options": ["High volume", "New source", "After hours", "Failed attempts"]
            }
        
        return clarifications
    
    async def _apply_context(
        self,
        entities: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply conversation context to entities"""
        # If no time range specified, use from context
        has_time = any(e.get("type") == "time_range" for e in entities)
        if not has_time and context.get("entities", {}).get("time_range"):
            entities.append({
                "type": "time_range",
                "value": context["entities"]["time_range"][-1],
                "from_context": True
            })
        
        return entities
    
    async def process_clarification(
        self,
        original_query: str,
        clarification: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a clarification response
        
        Args:
            original_query: Original ambiguous query
            clarification: User's clarification choice
            context: Conversation context
            
        Returns:
            Processed result with clarification applied
        """
        # Modify query based on clarification
        modified_query = original_query
        
        # Map clarification to concrete terms
        clarification_mappings = {
            "Last hour": "in the last hour",
            "Last 24 hours": "in the last 24 hours",
            "Last 7 days": "in the last 7 days",
            "Last month": "in the last month"
        }
        
        for key, value in clarification_mappings.items():
            if clarification == key:
                modified_query = modified_query.replace("recent", value)
                modified_query = modified_query.replace("recently", value)
                break
        
        # Process the modified query
        return await self.process(modified_query, context)
    
    async def cleanup(self) -> None:
        """Cleanup pipeline resources"""
        self.initialized = False
        logger.info("Pipeline cleaned up")

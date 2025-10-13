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
            from .nlp.smart_defaults import AdvancedQueryPreprocessor
            from .query.builder import QueryBuilder
            from .query.validator import QueryValidator
            from .query.advanced_builder import AdvancedQueryBuilder, QueryValidator as AdvancedValidator
            from .ai.response_generator import ResponseGenerator
            
            # Initialize components
            self.intent_classifier = IntentClassifier()
            self.entity_extractor = EntityExtractor()
            self.schema_mapper = SchemaMapper()
            self.query_preprocessor = AdvancedQueryPreprocessor()  # NEW: Smart defaults engine
            self.query_builder = QueryBuilder()
            self.advanced_query_builder = AdvancedQueryBuilder()
            self.query_validator = QueryValidator()
            self.advanced_validator = AdvancedValidator()
            self.response_generator = ResponseGenerator()
            
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
            
            # Store intent for AI suggestions
            self._last_intent = result["intent"]
            
            # Step 2: Entity Extraction
            raw_entities = self.entity_extractor.extract_entities(query)
            # Convert Entity objects to dictionaries for consistent processing
            entities = [entity.to_dict() for entity in raw_entities]
            result["entities"] = entities
            
            # Step 3: SMART DEFAULTS - Apply AI intelligence before clarification
            processed_query = self.query_preprocessor.preprocess_query(
                query=query,
                intent=result["intent"],
                entities=entities,
                user_context=user_context
            )
            
            # Update result with AI enhancements
            result["processed_query"] = processed_query["processed_query"]
            result["ai_enhancements"] = processed_query["enhancements"]
            result["confidence"] += processed_query["confidence_boost"]  # Boost confidence with smart defaults
            
            # Step 4: Check for ambiguities (ONLY if smart defaults couldn't resolve them)
            if processed_query["needs_clarification"] and await self._has_ambiguities(query, entities):
                clarifications = await self._get_clarifications(query, entities)
                result["needs_clarification"] = True
                result["clarifications"] = clarifications
                return result
            
            # Step 5: Apply context if available
            if context and context.get("history"):
                entities = await self._apply_context(entities, context)
            
            # Step 6: Schema mapping (using enhanced entities if available)
            enhanced_entities = entities.copy()
            if result["ai_enhancements"].get("suggested_fields"):
                # Add suggested fields as potential entities for better mapping
                for field in result["ai_enhancements"]["suggested_fields"]:
                    enhanced_entities.append({"type": field, "value": "*", "confidence": 0.5})
            
            field_mappings = await self.schema_mapper.map_entities(enhanced_entities)
            result["field_mappings"] = field_mappings
            
            # Step 7: Build query (with AI enhancements)
            siem_query = await self.build_query(
                intent=result["intent"],
                entities=enhanced_entities,
                field_mappings=field_mappings,
                context=context,
                ai_enhancements=result["ai_enhancements"]  # Pass AI enhancements to query builder
            )
            result["siem_query"] = siem_query
            
            # Step 8: Validate query
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
        context: Optional[Dict[str, Any]] = None,
        ai_enhancements: Optional[Dict[str, Any]] = None
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
        # Use advanced query builder if available
        if hasattr(self, 'advanced_query_builder') and self.advanced_query_builder:
            return self.advanced_query_builder.build_query(
                intent=intent,
                entities=entities,
                field_mappings=field_mappings,
                context=context
            )
        
        # Fallback to basic query builder
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
        # Use advanced validator if available
        if hasattr(self, 'advanced_validator') and self.advanced_validator:
            return await self.advanced_validator.validate_query(query)
        
        # Fallback to basic validator
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
        # Use AI response generator if available
        if hasattr(self, 'response_generator') and self.response_generator:
            return await self.response_generator.generate_summary(
                results=results,
                query=query,
                intent=intent
            )
        
        # Fallback to template-based summary
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
        # Use AI response generator if available
        if hasattr(self, 'response_generator') and self.response_generator:
            intent = getattr(self, '_last_intent', 'unknown')
            return await self.response_generator.generate_follow_up_questions(
                query=current_query,
                results=results,
                intent=intent
            )
        
        # Fallback to template-based suggestions
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
    
    # ========== MISSING METHODS FOR COMPLETE FUNCTIONALITY ==========
    
    async def format_results(
        self,
        results: Dict[str, Any],
        query_type: str
    ) -> List[Dict[str, Any]]:
        """Format SIEM query results for frontend consumption"""
        try:
            formatted_results = []
            
            # Handle different result formats
            if isinstance(results, list):
                # Results is already a list
                raw_results = results
            elif isinstance(results, dict):
                # Extract hits from Elasticsearch-style response
                if 'hits' in results and 'hits' in results['hits']:
                    raw_results = [hit.get('_source', hit) for hit in results['hits']['hits']]
                elif '_source' in results:
                    raw_results = [results['_source']]
                else:
                    raw_results = [results]
            else:
                raw_results = []
            
            # Format each result
            for result in raw_results:
                formatted_result = {
                    '@timestamp': result.get('@timestamp', result.get('timestamp', '')),
                    'message': result.get('message', result.get('event', {}).get('action', 'No message')),
                    'severity': result.get('event', {}).get('severity', result.get('severity', 'unknown')),
                    'source': {
                        'ip': result.get('source', {}).get('ip', ''),
                        'name': result.get('host', {}).get('name', '')
                    },
                    'destination': {
                        'ip': result.get('destination', {}).get('ip', ''),
                        'port': result.get('destination', {}).get('port', '')
                    },
                    'user': {
                        'name': result.get('user', {}).get('name', '')
                    },
                    'event': {
                        'action': result.get('event', {}).get('action', ''),
                        'category': result.get('event', {}).get('category', ''),
                        'outcome': result.get('event', {}).get('outcome', '')
                    },
                    'network': {
                        'protocol': result.get('network', {}).get('protocol', '')
                    },
                    'raw': result  # Keep original data
                }
                
                formatted_results.append(formatted_result)
            
            logger.info(f"Formatted {len(formatted_results)} results for query type: {query_type}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to format results: {e}")
            return []
    
    async def generate_summary(
        self,
        results: List[Dict[str, Any]],
        query: str,
        intent: str
    ) -> str:
        """Generate a human-readable summary of the query results"""
        try:
            if not results:
                return f"No results found for your query: '{query}'. Try refining your search criteria or expanding the time range."
            
            result_count = len(results)
            
            # Generate intent-specific summaries
            if intent == "failed_login" or intent == "show_failed_logins":
                unique_users = len(set(r.get('user', {}).get('name', '') for r in results if r.get('user', {}).get('name', '')))
                unique_ips = len(set(r.get('source', {}).get('ip', '') for r in results if r.get('source', {}).get('ip', '')))
                
                summary = f"Found {result_count} failed login attempts"
                if unique_users > 0:
                    summary += f" from {unique_users} unique user(s)"
                if unique_ips > 0:
                    summary += f" and {unique_ips} unique IP address(es)"
                
                # Add top offenders
                if result_count > 0:
                    summary += ". Recent attempts detected - investigate for potential brute force attacks."
                    
            elif intent == "successful_login" or intent == "show_successful_logins":
                unique_users = len(set(r.get('user', {}).get('name', '') for r in results if r.get('user', {}).get('name', '')))
                summary = f"Found {result_count} successful login events from {unique_users} unique user(s). All authentication attempts completed successfully."
                
            elif intent == "malware" or intent == "malware_detection":
                high_severity = len([r for r in results if r.get('severity', '').lower() in ['critical', 'high']])
                summary = f"Detected {result_count} malware-related events, with {high_severity} high/critical severity incidents requiring immediate attention."
                
            elif intent == "network" or intent == "network_traffic":
                protocols = set(r.get('network', {}).get('protocol', '') for r in results if r.get('network', {}).get('protocol', ''))
                summary = f"Analyzed {result_count} network events across {len(protocols)} protocols ({', '.join(list(protocols)[:3])})."
                
            elif intent == "user_activity":
                users = set(r.get('user', {}).get('name', '') for r in results if r.get('user', {}).get('name', ''))
                summary = f"Found {result_count} user activity events from {len(users)} unique user(s)."
                
            else:
                # Generic summary
                summary = f"Found {result_count} security events matching your query"
                
                # Add severity breakdown
                severity_counts = {}
                for result in results:
                    severity = result.get('severity', 'unknown').lower()
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                if severity_counts:
                    severity_parts = []
                    for sev in ['critical', 'high', 'medium', 'low']:
                        if sev in severity_counts:
                            severity_parts.append(f"{severity_counts[sev]} {sev}")
                    
                    if severity_parts:
                        summary += f" (Severity breakdown: {', '.join(severity_parts)})"
                
                summary += "."
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return f"Found {len(results)} results for your query."
    
    async def create_visualizations(
        self,
        data: List[Dict[str, Any]],
        query_type: str
    ) -> List[Dict[str, Any]]:
        """Create visualizations based on the data and query type"""
        try:
            visualizations = []
            
            if not data:
                return visualizations
            
            # Time series visualization
            if len(data) > 1:
                time_data = []
                for i, record in enumerate(data[:20]):  # Limit to 20 points
                    timestamp = record.get('@timestamp', f'Point {i+1}')
                    time_data.append({
                        'x': timestamp,
                        'y': 1
                    })
                
                visualizations.append({
                    'type': 'time_series',
                    'title': f'{query_type.replace("_", " ").title()} Over Time',
                    'data': time_data,
                    'config': {
                        'x_field': 'x',
                        'y_field': 'y',
                        'chart_type': 'line'
                    }
                })
            
            # Top sources/users chart
            if query_type in ['failed_login', 'successful_login', 'user_activity']:
                user_counts = {}
                for record in data:
                    user = record.get('user', {}).get('name', 'Unknown')
                    user_counts[user] = user_counts.get(user, 0) + 1
                
                top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                if top_users:
                    visualizations.append({
                        'type': 'bar_chart',
                        'title': 'Top Users',
                        'data': [{'name': user, 'value': count} for user, count in top_users],
                        'config': {
                            'x_field': 'name',
                            'y_field': 'value'
                        }
                    })
            
            # IP address analysis
            if len(data) > 0 and any(r.get('source', {}).get('ip') for r in data):
                ip_counts = {}
                for record in data:
                    ip = record.get('source', {}).get('ip', '')
                    if ip:
                        ip_counts[ip] = ip_counts.get(ip, 0) + 1
                
                top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                if top_ips:
                    visualizations.append({
                        'type': 'bar_chart',
                        'title': 'Top Source IPs',
                        'data': [{'name': ip, 'value': count} for ip, count in top_ips],
                        'config': {
                            'x_field': 'name',
                            'y_field': 'value'
                        }
                    })
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Failed to create visualizations: {e}")
            return []
    
    async def generate_suggestions(
        self,
        current_query: str,
        results: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate follow-up query suggestions based on current results"""
        try:
            suggestions = []
            
            if not results:
                # No results - suggest broadening the search
                suggestions.extend([
                    "Try expanding the time range (e.g., 'last 24 hours' instead of 'last hour')",
                    "Remove specific filters to see more results",
                    "Check for similar events with different keywords"
                ])
                return suggestions
            
            # Get unique values for suggestions
            unique_users = set(r.get('user', {}).get('name', '') for r in results if r.get('user', {}).get('name', ''))
            unique_ips = set(r.get('source', {}).get('ip', '') for r in results if r.get('source', {}).get('ip', ''))
            severities = set(r.get('severity', '') for r in results if r.get('severity', ''))
            
            # Intent-based suggestions
            if "login" in current_query.lower():
                if unique_users:
                    user = list(unique_users)[0]
                    suggestions.append(f"Show all activity for user {user}")
                if unique_ips:
                    ip = list(unique_ips)[0]
                    suggestions.append(f"Investigate all events from IP {ip}")
                suggestions.extend([
                    "Show successful logins for comparison",
                    "Find brute force attack patterns",
                    "Check for login anomalies by time"
                ])
                
            elif "malware" in current_query.lower():
                suggestions.extend([
                    "Show quarantined files",
                    "Find all infected hosts",
                    "Check for lateral movement",
                    "Analyze malware families detected"
                ])
                
            elif "network" in current_query.lower():
                suggestions.extend([
                    "Show blocked connections",
                    "Analyze bandwidth usage",
                    "Find port scan attempts",
                    "Check for data exfiltration"
                ])
            
            # Add time-based suggestions
            if "hour" not in current_query.lower():
                suggestions.append("Show trends over the last 24 hours")
            
            # Add severity-based suggestions
            if "critical" in severities:
                suggestions.append("Focus on critical severity events only")
            
            # Limit to top 5 suggestions
            return suggestions[:5]
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return [
                "Try refining your search with more specific terms",
                "Expand the time range to see more results",
                "Filter by severity level (critical, high, medium, low)"
            ]

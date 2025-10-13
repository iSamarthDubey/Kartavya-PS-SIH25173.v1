"""
Schema Mapper Module
Maps natural language entities to SIEM schema fields
Supports both Elasticsearch and Wazuh field mappings
"""

from typing import Dict, List, Optional, Any, Tuple
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class SchemaMapper:
    """
    Maps natural language entities to SIEM schema fields
    Maintains a dictionary of common terms to field mappings
    """
    
    def __init__(self, mapping_file: Optional[str] = None):
        """
        Initialize the schema mapper
        
        Args:
            mapping_file: Path to custom mapping YAML file
        """
        self.mapping_file = mapping_file or "config/schema_mappings.yaml"
        self.mappings = self._load_mappings()
        self.field_cache = {}
        self.discovered_fields = {}
        
    def _load_mappings(self) -> Dict:
        """Load schema mappings from file or use defaults"""
        mapping_path = Path(self.mapping_file)
        
        if mapping_path.exists():
            try:
                with open(mapping_path, 'r') as f:
                    return yaml.safe_load(f) or self._get_default_mappings()
            except Exception as e:
                logger.error(f"Failed to load mappings from {mapping_path}: {e}")
                return self._get_default_mappings()
        else:
            return self._get_default_mappings()
    
    def _get_default_mappings(self) -> Dict:
        """Get default field mappings for common SIEM schemas"""
        return {
            # Authentication events
            "failed_login": {
                "elastic": ["event.action:authentication_failure", "event.outcome:failure"],
                "wazuh": ["rule.groups:authentication_failed", "data.win.eventdata.logonType:3"],
                "fields": ["event.action", "event.outcome", "winlog.event_id"]
            },
            "successful_login": {
                "elastic": ["event.action:authentication_success", "event.outcome:success"],
                "wazuh": ["rule.groups:authentication_success"],
                "fields": ["event.action", "event.outcome"]
            },
            "brute_force": {
                "elastic": ["event.category:authentication", "event.type:denied"],
                "wazuh": ["rule.groups:brute_force"],
                "fields": ["event.category", "event.type", "rule.description"]
            },
            
            # User entities
            "user": {
                "elastic": ["user.name", "source.user.name", "destination.user.name", "winlog.event_data.TargetUserName"],
                "wazuh": ["data.win.eventdata.targetUserName", "data.srcuser"],
                "fields": ["user.name", "user.id", "user.email"]
            },
            "username": {
                "elastic": ["user.name", "source.user.name", "destination.user.name", "winlog.event_data.TargetUserName"],
                "wazuh": ["data.win.eventdata.targetUserName", "data.srcuser"],
                "fields": ["user.name", "user.id", "user.email"]
            },
            
            # Network entities
            "ip": {
                "elastic": ["source.ip", "destination.ip", "client.ip", "server.ip"],
                "wazuh": ["data.srcip", "data.dstip"],
                "fields": ["source.ip", "destination.ip", "host.ip"]
            },
            "port": {
                "elastic": ["source.port", "destination.port"],
                "wazuh": ["data.srcport", "data.dstport"],
                "fields": ["source.port", "destination.port"]
            },
            
            # Host entities
            "host": {
                "elastic": ["host.name", "host.hostname", "agent.hostname"],
                "wazuh": ["agent.name", "data.win.system.computer"],
                "fields": ["host.name", "host.id", "host.ip"]
            },
            
            # Threat entities
            "malware": {
                "elastic": ["threat.indicator.type:malware", "event.category:malware"],
                "wazuh": ["rule.groups:malware", "data.virustotal.malicious"],
                "fields": ["threat.indicator.name", "threat.indicator.type"]
            },
            "virus": {
                "elastic": ["threat.indicator.type:virus", "threat.software.name"],
                "wazuh": ["rule.groups:virus"],
                "fields": ["threat.software.name", "threat.software.type"]
            },
            
            # Service entities
            "vpn": {
                "elastic": ["service.name:vpn", "network.protocol:vpn"],
                "wazuh": ["rule.groups:vpn"],
                "fields": ["service.name", "network.protocol"]
            },
            "ssh": {
                "elastic": ["service.name:ssh", "network.protocol:ssh"],
                "wazuh": ["rule.groups:sshd"],
                "fields": ["service.name", "process.name"]
            },
            
            # Time entities
            "timestamp": {
                "elastic": ["@timestamp"],
                "wazuh": ["timestamp"],
                "fields": ["@timestamp", "event.created", "event.start"]
            },
            
            # Severity entities  
            "critical": {
                "elastic": ["event.severity:critical", "log.level:critical"],
                "wazuh": ["rule.level:[12 TO 15]"],
                "fields": ["event.severity", "rule.level"]
            },
            "high": {
                "elastic": ["event.severity:high", "log.level:error"],
                "wazuh": ["rule.level:[9 TO 11]"],
                "fields": ["event.severity", "rule.level"]
            },
            "medium": {
                "elastic": ["event.severity:medium", "log.level:warning"],
                "wazuh": ["rule.level:[6 TO 8]"],
                "fields": ["event.severity", "rule.level"]
            },
            "low": {
                "elastic": ["event.severity:low", "log.level:info"],
                "wazuh": ["rule.level:[0 TO 5]"],
                "fields": ["event.severity", "rule.level"]
            }
        }
    
    async def initialize(self, connector) -> None:
        """
        Initialize with live SIEM connector to discover actual schema
        
        Args:
            connector: SIEM connector instance
        """
        try:
            if hasattr(connector, 'get_field_mappings'):
                # Check if get_field_mappings is async
                import inspect
                if inspect.iscoroutinefunction(connector.get_field_mappings):
                    # It's async, so await it
                    self.discovered_fields = await connector.get_field_mappings()
                else:
                    # It's sync, call it directly
                    self.discovered_fields = connector.get_field_mappings()
                
                # Safely get the length of discovered fields
                if isinstance(self.discovered_fields, dict):
                    field_count = len(self.discovered_fields.get('properties', {}))
                    logger.info(f"Discovered {field_count} field mappings from SIEM")
                else:
                    logger.info("Schema discovery completed")
        except Exception as e:
            logger.warning(f"Could not discover schema from SIEM: {e}")
    
    def map_entity_to_fields(
        self,
        entity: str,
        entity_type: Optional[str] = None,
        platform: str = "elastic"
    ) -> List[str]:
        """
        Map a natural language entity to SIEM field names
        
        Args:
            entity: The entity value to map
            entity_type: Optional entity type hint
            platform: Target platform (elastic or wazuh)
            
        Returns:
            List of field names that match the entity
        """
        # Check cache first
        cache_key = f"{platform}:{entity_type}:{entity}" if entity_type else f"{platform}:{entity}"
        if cache_key in self.field_cache:
            return self.field_cache[cache_key]
        
        fields = []
        
        # Try direct mapping by entity type
        if entity_type and entity_type.lower() in self.mappings:
            mapping = self.mappings[entity_type.lower()]
            if platform in mapping:
                fields.extend(mapping[platform])
            else:
                fields.extend(mapping.get("fields", []))
        
        # Try to find mapping by entity value
        entity_lower = entity.lower()
        for key, mapping in self.mappings.items():
            if key in entity_lower or entity_lower in key:
                if platform in mapping:
                    fields.extend(mapping[platform])
                else:
                    fields.extend(mapping.get("fields", []))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_fields = []
        for field in fields:
            if field not in seen:
                seen.add(field)
                unique_fields.append(field)
        
        # Cache the result
        self.field_cache[cache_key] = unique_fields
        
        return unique_fields
    
    async def map_entities(
        self,
        entities: List[Dict[str, Any]],
        platform: str = "elastic"
    ) -> Dict[str, List[str]]:
        """
        Map multiple entities to field mappings
        
        Args:
            entities: List of entity dictionaries
            platform: Target platform
            
        Returns:
            Dictionary of entity to field mappings
        """
        field_mappings = {}
        
        for entity_dict in entities:
            entity_type = entity_dict.get("type")
            entity_value = entity_dict.get("value")
            
            if not entity_value:
                continue
            
            fields = self.map_entity_to_fields(
                entity=entity_value,
                entity_type=entity_type,
                platform=platform
            )
            
            if fields:
                field_mappings[entity_value] = fields
        
        return field_mappings
    
    def map_time_range(self, time_expression: str) -> Dict[str, str]:
        """
        Map natural language time expressions to query time ranges
        
        Args:
            time_expression: Natural language time expression
            
        Returns:
            Dictionary with 'gte' and 'lte' time bounds
        """
        now = datetime.now()
        time_lower = time_expression.lower()
        
        # Common time patterns
        patterns = {
            r"last (\d+) hour": lambda m: {"gte": f"now-{m.group(1)}h", "lte": "now"},
            r"last (\d+) day": lambda m: {"gte": f"now-{m.group(1)}d", "lte": "now"},
            r"last (\d+) week": lambda m: {"gte": f"now-{int(m.group(1))*7}d", "lte": "now"},
            r"last (\d+) month": lambda m: {"gte": f"now-{int(m.group(1))*30}d", "lte": "now"},
            r"yesterday": lambda m: {"gte": "now-1d/d", "lte": "now-1d/d"},
            r"today": lambda m: {"gte": "now/d", "lte": "now"},
            r"this week": lambda m: {"gte": "now/w", "lte": "now"},
            r"this month": lambda m: {"gte": "now/M", "lte": "now"},
        }
        
        for pattern, handler in patterns.items():
            match = re.search(pattern, time_lower)
            if match:
                return handler(match)
        
        # Default to last 24 hours
        return {"gte": "now-24h", "lte": "now"}
    
    def suggest_fields(self, partial_term: str, platform: str = "elastic") -> List[str]:
        """
        Suggest field names based on partial input
        
        Args:
            partial_term: Partial field name
            platform: Target platform
            
        Returns:
            List of suggested field names
        """
        suggestions = []
        partial_lower = partial_term.lower()
        
        # Search in mappings
        for key, mapping in self.mappings.items():
            if partial_lower in key:
                if platform in mapping:
                    suggestions.extend(mapping[platform])
                else:
                    suggestions.extend(mapping.get("fields", []))
        
        # Search in discovered fields
        if self.discovered_fields:
            for field in self.discovered_fields:
                if partial_lower in field.lower():
                    suggestions.append(field)
        
        # Remove duplicates and return
        return list(set(suggestions))[:10]  # Return top 10 suggestions
    
    def validate_field(self, field_name: str) -> bool:
        """
        Validate if a field exists in the schema
        
        Args:
            field_name: Field name to validate
            
        Returns:
            True if field is valid
        """
        # Check in discovered fields
        if self.discovered_fields:
            return field_name in self.discovered_fields
        
        # Check in known mappings
        for mapping in self.mappings.values():
            if field_name in mapping.get("fields", []):
                return True
            for platform_fields in ["elastic", "wazuh"]:
                if platform_fields in mapping:
                    for field in mapping[platform_fields]:
                        if field_name in field:
                            return True
        
        return False
    
    def get_field_info(self, field_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific field
        
        Args:
            field_name: Field name
            
        Returns:
            Dictionary with field information or None
        """
        # Try to get from discovered fields
        if self.discovered_fields and field_name in self.discovered_fields:
            return self.discovered_fields[field_name]
        
        # Try to find in mappings
        for entity_type, mapping in self.mappings.items():
            if field_name in mapping.get("fields", []):
                return {
                    "name": field_name,
                    "entity_type": entity_type,
                    "platforms": list(mapping.keys())
                }
        
        return None
    
    def export_mappings(self, output_file: str) -> None:
        """
        Export current mappings to file
        
        Args:
            output_file: Output file path
        """
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            export_data = {
                "mappings": self.mappings,
                "discovered_fields": self.discovered_fields,
                "timestamp": datetime.now().isoformat()
            }
            
            if output_file.endswith('.yaml') or output_file.endswith('.yml'):
                with open(output_path, 'w') as f:
                    yaml.dump(export_data, f, default_flow_style=False)
            else:
                with open(output_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported mappings to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export mappings: {e}")

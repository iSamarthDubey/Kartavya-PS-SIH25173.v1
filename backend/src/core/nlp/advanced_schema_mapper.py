"""
Advanced Schema Mapper for SIEM Systems
Provides dynamic field mapping and schema translation across different SIEM platforms
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class SIEMPlatform(Enum):
    """Supported SIEM platforms"""
    ELASTICSEARCH = "elasticsearch"
    SPLUNK = "splunk"
    QRADAR = "qradar"
    SENTINEL = "sentinel"
    WAZUH = "wazuh"
    SUMO_LOGIC = "sumo_logic"
    LOGRHYTHM = "logrhythm"
    ARCSIGHT = "arcsight"
    GENERIC = "generic"


@dataclass
class FieldMapping:
    """Field mapping configuration"""
    source_field: str
    target_fields: List[str]
    field_type: str  # "exact", "partial", "regex", "function"
    confidence: float
    transformation: Optional[str] = None  # Function to transform the value
    platform_specific: Optional[Dict[str, Any]] = None


@dataclass
class SchemaContext:
    """Schema mapping context"""
    platform: SIEMPlatform
    version: Optional[str] = None
    custom_fields: Optional[Dict[str, str]] = None
    data_source: Optional[str] = None


class AdvancedSchemaMapper:
    """Advanced schema mapper with dynamic field resolution"""
    
    def __init__(self):
        """Initialize the schema mapper"""
        self.field_mappings = self._load_field_mappings()
        self.schema_cache = {}
        self.custom_mappings = {}
        self.entity_type_mappings = self._load_entity_type_mappings()
        
    async def initialize(self, siem_connector=None):
        """Initialize mapper with SIEM connector information"""
        if siem_connector:
            # Detect platform from connector
            platform = self._detect_platform(siem_connector)
            logger.info(f"Initialized schema mapper for platform: {platform}")
            
            # Load platform-specific schemas
            await self._load_platform_schema(platform, siem_connector)
    
    async def map_entities(
        self, 
        entities: List[Dict[str, Any]], 
        context: Optional[SchemaContext] = None
    ) -> Dict[str, List[str]]:
        """
        Map entity types to SIEM field names
        
        Args:
            entities: List of extracted entities
            context: Schema mapping context
            
        Returns:
            Dictionary mapping entity types to field names
        """
        try:
            field_mappings = {}
            platform = context.platform if context else SIEMPlatform.ELASTICSEARCH
            
            for entity in entities:
                entity_type = entity.get("type")
                if not entity_type:
                    continue
                
                # Get field mappings for this entity type and platform
                fields = await self._get_fields_for_entity_type(entity_type, platform, context)
                
                if fields:
                    field_mappings[entity_type] = fields
                    
            logger.info(f"Mapped {len(field_mappings)} entity types to fields")
            return field_mappings
            
        except Exception as e:
            logger.error(f"Error mapping entities: {e}")
            return {}
    
    async def translate_field_names(
        self,
        source_fields: List[str],
        source_platform: SIEMPlatform,
        target_platform: SIEMPlatform
    ) -> Dict[str, str]:
        """
        Translate field names between SIEM platforms
        
        Args:
            source_fields: List of source field names
            source_platform: Source SIEM platform
            target_platform: Target SIEM platform
            
        Returns:
            Dictionary mapping source fields to target fields
        """
        try:
            translation_map = {}
            
            for source_field in source_fields:
                target_field = await self._translate_single_field(
                    source_field, source_platform, target_platform
                )
                if target_field:
                    translation_map[source_field] = target_field
            
            return translation_map
            
        except Exception as e:
            logger.error(f"Error translating field names: {e}")
            return {}
    
    async def get_field_suggestions(
        self,
        partial_field: str,
        platform: SIEMPlatform,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get field name suggestions for partial input
        
        Args:
            partial_field: Partial field name
            platform: Target SIEM platform
            limit: Maximum number of suggestions
            
        Returns:
            List of field suggestions with confidence scores
        """
        try:
            suggestions = []
            platform_fields = self.field_mappings.get(platform.value, {})
            
            partial_lower = partial_field.lower()
            
            # Search through all field mappings
            for entity_type, field_list in platform_fields.items():
                for field in field_list:
                    if partial_lower in field.lower():
                        confidence = self._calculate_field_similarity(partial_field, field)
                        suggestions.append({
                            "field": field,
                            "entity_type": entity_type,
                            "confidence": confidence,
                            "description": self._get_field_description(field, entity_type)
                        })
            
            # Sort by confidence and return top suggestions
            suggestions.sort(key=lambda x: x["confidence"], reverse=True)
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting field suggestions: {e}")
            return []
    
    async def validate_field_mapping(
        self,
        entity_type: str,
        field_name: str,
        platform: SIEMPlatform
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Validate if a field mapping is appropriate
        
        Args:
            entity_type: Entity type
            field_name: Field name to validate
            platform: SIEM platform
            
        Returns:
            Tuple of (is_valid, confidence, reason)
        """
        try:
            platform_fields = self.field_mappings.get(platform.value, {})
            entity_fields = platform_fields.get(entity_type, [])
            
            # Exact match
            if field_name in entity_fields:
                return True, 1.0, "Exact field match"
            
            # Partial match
            partial_matches = [f for f in entity_fields if field_name.lower() in f.lower()]
            if partial_matches:
                confidence = max(self._calculate_field_similarity(field_name, f) for f in partial_matches)
                return True, confidence, f"Partial match found"
            
            # Cross-entity type search
            for other_entity_type, other_fields in platform_fields.items():
                if field_name in other_fields:
                    return False, 0.7, f"Field belongs to {other_entity_type}, not {entity_type}"
            
            return False, 0.0, "Field not found in schema"
            
        except Exception as e:
            logger.error(f"Error validating field mapping: {e}")
            return False, 0.0, f"Validation error: {str(e)}"
    
    async def create_custom_mapping(
        self,
        entity_type: str,
        custom_fields: List[str],
        platform: SIEMPlatform,
        confidence: float = 0.8
    ) -> bool:
        """
        Create custom field mapping for specific use case
        
        Args:
            entity_type: Entity type
            custom_fields: List of custom field names
            platform: SIEM platform
            confidence: Confidence score for the mapping
            
        Returns:
            Boolean indicating success
        """
        try:
            platform_key = platform.value
            
            if platform_key not in self.custom_mappings:
                self.custom_mappings[platform_key] = {}
            
            self.custom_mappings[platform_key][entity_type] = {
                "fields": custom_fields,
                "confidence": confidence,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Created custom mapping for {entity_type} on {platform_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating custom mapping: {e}")
            return False
    
    async def get_schema_statistics(self, platform: SIEMPlatform) -> Dict[str, Any]:
        """
        Get statistics about the schema mapping coverage
        
        Args:
            platform: SIEM platform
            
        Returns:
            Dictionary with schema statistics
        """
        try:
            platform_fields = self.field_mappings.get(platform.value, {})
            
            stats = {
                "platform": platform.value,
                "entity_types": len(platform_fields),
                "total_fields": sum(len(fields) for fields in platform_fields.values()),
                "entity_coverage": {},
                "field_distribution": {},
                "custom_mappings": len(self.custom_mappings.get(platform.value, {}))
            }
            
            # Entity coverage
            for entity_type, fields in platform_fields.items():
                stats["entity_coverage"][entity_type] = len(fields)
            
            # Field distribution by type
            for entity_type, fields in platform_fields.items():
                field_types = self._classify_field_types(fields)
                stats["field_distribution"][entity_type] = field_types
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting schema statistics: {e}")
            return {"error": str(e)}
    
    def _detect_platform(self, connector) -> SIEMPlatform:
        """Detect SIEM platform from connector"""
        connector_type = type(connector).__name__.lower()
        
        if "elastic" in connector_type:
            return SIEMPlatform.ELASTICSEARCH
        elif "splunk" in connector_type:
            return SIEMPlatform.SPLUNK
        elif "qradar" in connector_type:
            return SIEMPlatform.QRADAR
        elif "sentinel" in connector_type:
            return SIEMPlatform.SENTINEL
        elif "wazuh" in connector_type:
            return SIEMPlatform.WAZUH
        else:
            return SIEMPlatform.GENERIC
    
    async def _load_platform_schema(self, platform: SIEMPlatform, connector):
        """Load platform-specific schema information"""
        try:
            # Try to get schema from connector if supported
            if hasattr(connector, 'get_schema'):
                schema_info = await connector.get_schema()
                if schema_info:
                    self._integrate_dynamic_schema(platform, schema_info)
            
            # Load from configuration files
            schema_file = f"schemas/{platform.value}_schema.json"
            schema_path = os.path.join(os.path.dirname(__file__), "../..", "config", schema_file)
            
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    schema_data = json.load(f)
                    self._integrate_static_schema(platform, schema_data)
        
        except Exception as e:
            logger.warning(f"Could not load platform schema for {platform.value}: {e}")
    
    def _integrate_dynamic_schema(self, platform: SIEMPlatform, schema_info: Dict[str, Any]):
        """Integrate dynamically discovered schema information"""
        if platform.value not in self.field_mappings:
            self.field_mappings[platform.value] = {}
        
        # Process discovered fields
        for field_info in schema_info.get("fields", []):
            field_name = field_info.get("name")
            field_type = field_info.get("type")
            
            if field_name and field_type:
                # Infer entity type from field name
                entity_type = self._infer_entity_type_from_field(field_name)
                if entity_type:
                    if entity_type not in self.field_mappings[platform.value]:
                        self.field_mappings[platform.value][entity_type] = []
                    
                    if field_name not in self.field_mappings[platform.value][entity_type]:
                        self.field_mappings[platform.value][entity_type].append(field_name)
    
    def _integrate_static_schema(self, platform: SIEMPlatform, schema_data: Dict[str, Any]):
        """Integrate static schema configuration"""
        if platform.value not in self.field_mappings:
            self.field_mappings[platform.value] = {}
        
        # Merge with existing mappings
        for entity_type, fields in schema_data.get("field_mappings", {}).items():
            if entity_type not in self.field_mappings[platform.value]:
                self.field_mappings[platform.value][entity_type] = []
            
            for field in fields:
                if field not in self.field_mappings[platform.value][entity_type]:
                    self.field_mappings[platform.value][entity_type].append(field)
    
    async def _get_fields_for_entity_type(
        self, 
        entity_type: str, 
        platform: SIEMPlatform,
        context: Optional[SchemaContext] = None
    ) -> List[str]:
        """Get field mappings for specific entity type and platform"""
        
        # Check custom mappings first
        custom_fields = self.custom_mappings.get(platform.value, {}).get(entity_type, {}).get("fields")
        if custom_fields:
            return custom_fields
        
        # Get standard mappings
        platform_fields = self.field_mappings.get(platform.value, {})
        fields = platform_fields.get(entity_type, [])
        
        # Apply context-specific modifications
        if context and context.custom_fields:
            additional_fields = context.custom_fields.get(entity_type, [])
            if isinstance(additional_fields, str):
                additional_fields = [additional_fields]
            fields.extend(additional_fields)
        
        return list(set(fields))  # Remove duplicates
    
    async def _translate_single_field(
        self, 
        source_field: str, 
        source_platform: SIEMPlatform,
        target_platform: SIEMPlatform
    ) -> Optional[str]:
        """Translate a single field name between platforms"""
        
        # Find entity type for source field
        source_fields = self.field_mappings.get(source_platform.value, {})
        source_entity_type = None
        
        for entity_type, fields in source_fields.items():
            if source_field in fields:
                source_entity_type = entity_type
                break
        
        if not source_entity_type:
            return None
        
        # Get target fields for same entity type
        target_fields = await self._get_fields_for_entity_type(
            source_entity_type, target_platform
        )
        
        # Return first available target field (could be enhanced with similarity matching)
        return target_fields[0] if target_fields else None
    
    def _calculate_field_similarity(self, field1: str, field2: str) -> float:
        """Calculate similarity between two field names"""
        field1_lower = field1.lower()
        field2_lower = field2.lower()
        
        # Exact match
        if field1_lower == field2_lower:
            return 1.0
        
        # Substring match
        if field1_lower in field2_lower or field2_lower in field1_lower:
            shorter = min(len(field1_lower), len(field2_lower))
            longer = max(len(field1_lower), len(field2_lower))
            return shorter / longer
        
        # Character overlap
        common_chars = set(field1_lower) & set(field2_lower)
        total_chars = set(field1_lower) | set(field2_lower)
        
        if total_chars:
            return len(common_chars) / len(total_chars)
        
        return 0.0
    
    def _get_field_description(self, field_name: str, entity_type: str) -> str:
        """Get description for a field"""
        descriptions = {
            "ip_address": {
                "source.ip": "Source IP address of the connection",
                "destination.ip": "Destination IP address",
                "host.ip": "Host IP address"
            },
            "username": {
                "user.name": "Username or account name",
                "user.id": "User identifier",
                "source.user.name": "Source user name"
            },
            "timestamp": {
                "@timestamp": "Event timestamp",
                "event.created": "Event creation time",
                "log.timestamp": "Log entry timestamp"
            }
        }
        
        entity_descriptions = descriptions.get(entity_type, {})
        return entity_descriptions.get(field_name, f"Field for {entity_type}")
    
    def _classify_field_types(self, fields: List[str]) -> Dict[str, int]:
        """Classify field types for statistics"""
        classification = {
            "network": 0,
            "user": 0,
            "system": 0,
            "security": 0,
            "timestamp": 0,
            "other": 0
        }
        
        for field in fields:
            field_lower = field.lower()
            
            if any(keyword in field_lower for keyword in ["ip", "port", "network", "protocol"]):
                classification["network"] += 1
            elif any(keyword in field_lower for keyword in ["user", "account", "login"]):
                classification["user"] += 1
            elif any(keyword in field_lower for keyword in ["host", "system", "process", "service"]):
                classification["system"] += 1
            elif any(keyword in field_lower for keyword in ["security", "threat", "alert", "event"]):
                classification["security"] += 1
            elif any(keyword in field_lower for keyword in ["time", "date", "timestamp"]):
                classification["timestamp"] += 1
            else:
                classification["other"] += 1
        
        return classification
    
    def _infer_entity_type_from_field(self, field_name: str) -> Optional[str]:
        """Infer entity type from field name"""
        field_lower = field_name.lower()
        
        if any(keyword in field_lower for keyword in ["ip", "addr"]):
            return "ip_address"
        elif any(keyword in field_lower for keyword in ["user", "account"]):
            return "username"
        elif any(keyword in field_lower for keyword in ["port"]):
            return "port"
        elif any(keyword in field_lower for keyword in ["process", "proc"]):
            return "process_name"
        elif any(keyword in field_lower for keyword in ["file", "path"]):
            return "file_path"
        elif any(keyword in field_lower for keyword in ["hash", "md5", "sha"]):
            return "hash"
        elif any(keyword in field_lower for keyword in ["time", "date"]):
            return "timestamp"
        elif any(keyword in field_lower for keyword in ["event", "code", "id"]):
            return "event_id"
        
        return None
    
    def _load_field_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Load field mappings for all supported platforms"""
        return {
            "elasticsearch": {
                "ip_address": ["source.ip", "destination.ip", "host.ip", "client.ip", "server.ip"],
                "username": ["user.name", "user.id", "source.user.name", "destination.user.name"],
                "port": ["source.port", "destination.port", "network.port", "client.port", "server.port"],
                "process_name": ["process.name", "process.executable", "process.title"],
                "event_id": ["event.code", "winlog.event_id", "event.id", "log.event.code"],
                "file_path": ["file.path", "file.name", "file.directory", "process.executable"],
                "domain": ["dns.question.name", "url.domain", "network.dns.name"],
                "hash": ["file.hash.md5", "file.hash.sha1", "file.hash.sha256", "process.hash.md5"],
                "timestamp": ["@timestamp", "event.created", "log.timestamp", "event.start"],
                "severity": ["event.severity", "log.level", "alert.severity"],
                "message": ["message", "log.message", "event.original"],
                "host": ["host.name", "host.hostname", "agent.hostname"],
                "threat": ["threat.indicator.type", "threat.indicator.name", "malware.name"]
            },
            
            "splunk": {
                "ip_address": ["src_ip", "dest_ip", "host", "clientip", "serverip"],
                "username": ["user", "src_user", "dest_user", "account", "username"],
                "port": ["src_port", "dest_port", "port", "service_port"],
                "process_name": ["process", "process_name", "image", "parent_process"],
                "event_id": ["EventCode", "event_id", "signature_id", "rule_id"],
                "file_path": ["file_path", "file_name", "path", "filename"],
                "domain": ["dns_query", "domain", "url_domain", "hostname"],
                "hash": ["file_hash", "md5", "sha1", "sha256"],
                "timestamp": ["_time", "timestamp", "event_time", "log_time"],
                "severity": ["severity", "priority", "level", "criticality"],
                "message": ["message", "_raw", "event_description"],
                "host": ["host", "hostname", "src_host", "dest_host"],
                "threat": ["signature", "malware", "threat_name", "virus"]
            },
            
            "qradar": {
                "ip_address": ["sourceip", "destinationip", "identityip", "hostip"],
                "username": ["username", "sourceusername", "destinationusername"],
                "port": ["sourceport", "destinationport", "port"],
                "process_name": ["processname", "applicationname", "servicename"],
                "event_id": ["qid", "eventid", "categoryid"],
                "file_path": ["filename", "filepath", "objectname"],
                "domain": ["domainname", "hostname", "fqdn"],
                "hash": ["filehash", "hashvalue"],
                "timestamp": ["starttime", "endtime", "devicetime"],
                "severity": ["severity", "magnitude", "relevance"],
                "message": ["message", "payload", "eventdescription"],
                "host": ["sourcehost", "destinationhost", "hostname"],
                "threat": ["category", "rulename", "eventname"]
            },
            
            "sentinel": {
                "ip_address": ["SourceIP", "DestinationIP", "ClientIP", "ServerIP"],
                "username": ["Account", "UserName", "SourceUserName", "TargetUserName"],
                "port": ["SourcePort", "DestinationPort", "Port"],
                "process_name": ["ProcessName", "Image", "ParentImage"],
                "event_id": ["EventID", "EventCode", "RuleId"],
                "file_path": ["FileName", "FilePath", "ImagePath"],
                "domain": ["DomainName", "DNSQuery", "UrlDomain"],
                "hash": ["Hash", "MD5", "SHA1", "SHA256"],
                "timestamp": ["TimeGenerated", "CreatedTime", "EventTime"],
                "severity": ["Severity", "Level", "Priority"],
                "message": ["Message", "Description", "EventDescription"],
                "host": ["Computer", "HostName", "DeviceName"],
                "threat": ["ThreatName", "MalwareName", "AlertName"]
            },
            
            "wazuh": {
                "ip_address": ["srcip", "dstip", "data.srcip", "data.dstip"],
                "username": ["data.dstuser", "data.srcuser", "data.uid", "data.euid"],
                "port": ["data.srcport", "data.dstport", "data.port"],
                "process_name": ["data.process", "data.program_name", "data.exe"],
                "event_id": ["rule.id", "data.id", "decoder.name"],
                "file_path": ["data.file", "data.path", "data.audit.file.name"],
                "domain": ["data.url", "data.hostname", "data.query"],
                "hash": ["data.hash", "data.md5", "data.sha1"],
                "timestamp": ["timestamp", "@timestamp", "data.timestamp"],
                "severity": ["rule.level", "rule.description", "data.status"],
                "message": ["full_log", "data.log", "rule.description"],
                "host": ["agent.name", "manager.name", "data.hostname"],
                "threat": ["rule.mitre.technique", "data.virustotal.scans", "rule.description"]
            }
        }
    
    def _load_entity_type_mappings(self) -> Dict[str, List[str]]:
        """Load entity type to standard field mappings"""
        return {
            "ip_address": ["network.ip", "network.source", "network.destination"],
            "username": ["identity.user", "identity.account", "authentication.user"],
            "port": ["network.port", "network.service", "application.port"],
            "process_name": ["process.executable", "system.process", "application.name"],
            "event_id": ["event.identifier", "log.event_id", "security.event_code"],
            "file_path": ["file.location", "filesystem.path", "object.file"],
            "domain": ["network.domain", "dns.query", "web.domain"],
            "hash": ["file.checksum", "crypto.hash", "integrity.hash"],
            "timestamp": ["event.time", "log.timestamp", "temporal.event"],
            "severity": ["event.severity", "alert.priority", "log.level"],
            "threat": ["security.threat", "malware.family", "attack.technique"]
        }

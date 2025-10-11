"""
Enterprise SIEM Connectors
Additional connectors for major SIEM platforms with data normalization and real-time streaming
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, AsyncIterator
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import aiohttp
import ssl
from urllib.parse import urljoin, urlparse

# Platform-specific imports (with fallbacks)
try:
    import splunklib.client as splunk_client
    import splunklib.results as splunk_results
    SPLUNK_AVAILABLE = True
except ImportError:
    SPLUNK_AVAILABLE = False

try:
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.monitor.query import LogsQueryClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SIEMConfig:
    """SIEM connection configuration"""
    host: str
    port: int = 443
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    token: Optional[str] = None
    ssl_verify: bool = True
    timeout: int = 30
    max_results: int = 10000
    
    # Platform-specific settings
    tenant_id: Optional[str] = None  # Azure
    client_id: Optional[str] = None  # Azure
    client_secret: Optional[str] = None  # Azure
    workspace_id: Optional[str] = None  # Azure Sentinel
    
    # QRadar specific
    sec_token: Optional[str] = None
    console_ip: Optional[str] = None


@dataclass
class NormalizedEvent:
    """Normalized event structure"""
    timestamp: str
    event_type: str
    severity: str
    source_system: str
    message: str
    
    # Network fields
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = None
    
    # User fields
    username: Optional[str] = None
    user_domain: Optional[str] = None
    
    # Host fields
    hostname: Optional[str] = None
    host_ip: Optional[str] = None
    
    # Process fields
    process_name: Optional[str] = None
    process_id: Optional[int] = None
    
    # File fields
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    
    # Security fields
    event_id: Optional[str] = None
    rule_name: Optional[str] = None
    threat_name: Optional[str] = None
    
    # Additional metadata
    raw_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class SIEMConnectorBase(ABC):
    """Base class for SIEM connectors"""
    
    def __init__(self, config: SIEMConfig):
        self.config = config
        self.connected = False
        self.session = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to SIEM platform"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from SIEM platform"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute query and return raw results"""
        pass
    
    @abstractmethod
    async def get_schema(self) -> Dict[str, Any]:
        """Get schema information"""
        pass
    
    async def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test SIEM connection"""
        try:
            success = await self.connect()
            if success:
                await self.disconnect()
                return True, None
            else:
                return False, "Connection failed"
        except Exception as e:
            return False, str(e)


class SplunkConnector(SIEMConnectorBase):
    """Splunk SIEM connector"""
    
    def __init__(self, config: SIEMConfig):
        super().__init__(config)
        self.service = None
        
    async def connect(self) -> bool:
        """Connect to Splunk"""
        if not SPLUNK_AVAILABLE:
            logger.error("Splunk SDK not available")
            return False
        
        try:
            # Create Splunk service connection
            self.service = splunk_client.connect(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                scheme="https" if self.config.ssl_verify else "http"
            )
            
            # Test connection
            self.service.info()
            self.connected = True
            logger.info(f"Connected to Splunk at {self.config.host}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Splunk: {e}")
            self.connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Splunk"""
        try:
            if self.service:
                self.service.logout()
            self.connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Splunk: {e}")
            return False
    
    async def execute_query(self, query: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute Splunk search"""
        if not self.connected or not self.service:
            raise Exception("Not connected to Splunk")
        
        try:
            # Build Splunk search query
            search_query = self._build_splunk_query(query)
            
            # Execute search
            search_kwargs = {
                "count": kwargs.get("size", self.config.max_results),
                "timeout": self.config.timeout,
                "exec_mode": "blocking"
            }
            
            # Add time range if specified
            if "range" in query:
                search_kwargs.update(self._parse_time_range(query["range"]))
            
            job = self.service.jobs.create(search_query, **search_kwargs)
            
            # Get results
            results = []
            for result in splunk_results.ResultsReader(job.results()):
                if isinstance(result, dict):
                    results.append(result)
            
            return {
                "hits": {
                    "total": {"value": len(results)},
                    "hits": [{"_source": result} for result in results]
                },
                "took": job.content.get("runDuration", 0),
                "_metadata": {
                    "search_query": search_query,
                    "job_id": job.sid
                }
            }
            
        except Exception as e:
            logger.error(f"Splunk query execution failed: {e}")
            raise
    
    async def get_schema(self) -> Dict[str, Any]:
        """Get Splunk schema information"""
        if not self.connected or not self.service:
            raise Exception("Not connected to Splunk")
        
        try:
            # Get indexes
            indexes = []
            for index in self.service.indexes:
                indexes.append({
                    "name": index.name,
                    "earliest_time": index.content.get("minTime"),
                    "latest_time": index.content.get("maxTime"),
                    "total_events": index.content.get("totalEventCount")
                })
            
            # Get data models
            data_models = []
            for model in self.service.datamodels:
                data_models.append({
                    "name": model.name,
                    "objects": [obj.name for obj in model.objects]
                })
            
            return {
                "platform": "splunk",
                "version": self.service.info().get("version"),
                "indexes": indexes,
                "data_models": data_models
            }
            
        except Exception as e:
            logger.error(f"Error getting Splunk schema: {e}")
            return {}
    
    def _build_splunk_query(self, query: Dict[str, Any]) -> str:
        """Build Splunk search query from structured query"""
        search_parts = ["search"]
        
        # Handle different query structures
        if "search" in query:
            # Direct search string
            return query["search"]
        
        elif "query" in query and "bool" in query["query"]:
            # Elasticsearch-style query
            bool_query = query["query"]["bool"]
            
            # Process must clauses
            for must_clause in bool_query.get("must", []):
                search_parts.extend(self._process_splunk_clause(must_clause))
            
            # Process filter clauses
            for filter_clause in bool_query.get("filter", []):
                search_parts.extend(self._process_splunk_clause(filter_clause))
        
        return " ".join(search_parts)
    
    def _process_splunk_clause(self, clause: Dict[str, Any]) -> List[str]:
        """Process individual query clause for Splunk"""
        parts = []
        
        if "match" in clause:
            field, value = next(iter(clause["match"].items()))
            parts.append(f'{field}="*{value}*"')
        elif "term" in clause:
            field, value = next(iter(clause["term"].items()))
            if isinstance(value, dict):
                value = value.get("value", value)
            parts.append(f'{field}="{value}"')
        elif "range" in clause:
            field, range_values = next(iter(clause["range"].items()))
            if "gte" in range_values:
                parts.append(f'{field}>={range_values["gte"]}')
            if "lte" in range_values:
                parts.append(f'{field}<={range_values["lte"]}')
        
        return parts
    
    def _parse_time_range(self, time_range: str) -> Dict[str, str]:
        """Parse time range for Splunk"""
        if time_range.lower() == "last 24 hours":
            return {"earliest_time": "-24h", "latest_time": "now"}
        elif time_range.lower() == "last hour":
            return {"earliest_time": "-1h", "latest_time": "now"}
        elif time_range.lower() == "last week":
            return {"earliest_time": "-7d", "latest_time": "now"}
        else:
            return {"earliest_time": "-24h", "latest_time": "now"}


class QRadarConnector(SIEMConnectorBase):
    """IBM QRadar SIEM connector"""
    
    def __init__(self, config: SIEMConfig):
        super().__init__(config)
        self.base_url = f"https://{config.host}/api"
        self.headers = {
            "SEC": config.sec_token or config.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
    async def connect(self) -> bool:
        """Connect to QRadar"""
        try:
            # Create HTTP session
            connector = aiohttp.TCPConnector(
                ssl=ssl.create_default_context() if self.config.ssl_verify else False
            )
            self.session = aiohttp.ClientSession(
                connector=connector,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # Test connection with system info
            url = urljoin(self.base_url, "/system/about")
            async with self.session.get(url) as response:
                if response.status == 200:
                    self.connected = True
                    logger.info(f"Connected to QRadar at {self.config.host}")
                    return True
                else:
                    logger.error(f"QRadar connection failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to connect to QRadar: {e}")
            self.connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from QRadar"""
        try:
            if self.session:
                await self.session.close()
            self.connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from QRadar: {e}")
            return False
    
    async def execute_query(self, query: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute QRadar AQL query"""
        if not self.connected or not self.session:
            raise Exception("Not connected to QRadar")
        
        try:
            # Build AQL query
            aql_query = self._build_aql_query(query)
            
            # Create search
            search_data = {
                "query_expression": aql_query
            }
            
            url = urljoin(self.base_url, "/ariel/searches")
            async with self.session.post(url, json=search_data) as response:
                if response.status != 201:
                    raise Exception(f"Failed to create QRadar search: {response.status}")
                
                search_result = await response.json()
                search_id = search_result["search_id"]
            
            # Poll for completion
            search_status = "WAIT"
            while search_status in ["WAIT", "EXECUTE"]:
                await asyncio.sleep(1)
                
                status_url = urljoin(self.base_url, f"/ariel/searches/{search_id}")
                async with self.session.get(status_url) as response:
                    status_data = await response.json()
                    search_status = status_data["status"]
            
            if search_status != "COMPLETED":
                raise Exception(f"QRadar search failed with status: {search_status}")
            
            # Get results
            results_url = urljoin(self.base_url, f"/ariel/searches/{search_id}/results")
            async with self.session.get(results_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get QRadar results: {response.status}")
                
                results_data = await response.json()
            
            # Format results
            results = results_data.get("events", [])
            return {
                "hits": {
                    "total": {"value": len(results)},
                    "hits": [{"_source": result} for result in results]
                },
                "took": 0,  # QRadar doesn't provide timing
                "_metadata": {
                    "aql_query": aql_query,
                    "search_id": search_id
                }
            }
            
        except Exception as e:
            logger.error(f"QRadar query execution failed: {e}")
            raise
    
    async def get_schema(self) -> Dict[str, Any]:
        """Get QRadar schema information"""
        if not self.connected or not self.session:
            raise Exception("Not connected to QRadar")
        
        try:
            # Get log sources
            log_sources_url = urljoin(self.base_url, "/config/event_sources/log_source_management/log_sources")
            async with self.session.get(log_sources_url) as response:
                log_sources = await response.json() if response.status == 200 else []
            
            # Get event properties
            properties_url = urljoin(self.base_url, "/data_classification/qid_records")
            async with self.session.get(properties_url) as response:
                properties = await response.json() if response.status == 200 else []
            
            return {
                "platform": "qradar",
                "log_sources": log_sources,
                "event_properties": properties[:100]  # Limit for performance
            }
            
        except Exception as e:
            logger.error(f"Error getting QRadar schema: {e}")
            return {}
    
    def _build_aql_query(self, query: Dict[str, Any]) -> str:
        """Build AQL query from structured query"""
        if "query_expression" in query:
            return query["query_expression"]
        
        # Build basic AQL query
        select_fields = [
            "QIDNAME(qid)",
            "LOGSOURCENAME(logsourceid)",
            "starttime",
            "sourceip",
            "destinationip",
            "username"
        ]
        
        aql_parts = [f"SELECT {', '.join(select_fields)} FROM events"]
        
        # Add WHERE conditions
        conditions = []
        if "query" in query and "bool" in query["query"]:
            bool_query = query["query"]["bool"]
            
            for must_clause in bool_query.get("must", []):
                condition = self._process_aql_clause(must_clause)
                if condition:
                    conditions.append(condition)
        
        if conditions:
            aql_parts.append(f"WHERE {' AND '.join(conditions)}")
        
        # Add time range
        aql_parts.append("LAST 24 HOURS")
        
        return " ".join(aql_parts)
    
    def _process_aql_clause(self, clause: Dict[str, Any]) -> Optional[str]:
        """Process query clause for AQL"""
        if "match" in clause:
            field, value = next(iter(clause["match"].items()))
            return f"{field} ILIKE '%{value}%'"
        elif "term" in clause:
            field, value = next(iter(clause["term"].items()))
            if isinstance(value, dict):
                value = value.get("value", value)
            return f"{field} = '{value}'"
        elif "range" in clause:
            field, range_values = next(iter(clause["range"].items()))
            conditions = []
            if "gte" in range_values:
                conditions.append(f"{field} >= '{range_values['gte']}'")
            if "lte" in range_values:
                conditions.append(f"{field} <= '{range_values['lte']}'")
            return " AND ".join(conditions)
        
        return None


class AzureSentinelConnector(SIEMConnectorBase):
    """Azure Sentinel SIEM connector"""
    
    def __init__(self, config: SIEMConfig):
        super().__init__(config)
        self.credential = None
        self.client = None
        
    async def connect(self) -> bool:
        """Connect to Azure Sentinel"""
        if not AZURE_AVAILABLE:
            logger.error("Azure SDK not available")
            return False
        
        try:
            # Create Azure credentials
            if self.config.client_id and self.config.client_secret and self.config.tenant_id:
                self.credential = ClientSecretCredential(
                    tenant_id=self.config.tenant_id,
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret
                )
            else:
                self.credential = DefaultAzureCredential()
            
            # Create Logs Query client
            self.client = LogsQueryClient(self.credential)
            
            # Test connection with a simple query
            test_query = "SecurityEvent | take 1"
            await asyncio.to_thread(
                self.client.query_workspace,
                workspace_id=self.config.workspace_id,
                query=test_query,
                timespan=timedelta(minutes=5)
            )
            
            self.connected = True
            logger.info(f"Connected to Azure Sentinel workspace: {self.config.workspace_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Azure Sentinel: {e}")
            self.connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Azure Sentinel"""
        try:
            if self.client:
                self.client.close()
            self.connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Azure Sentinel: {e}")
            return False
    
    async def execute_query(self, query: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute KQL query in Azure Sentinel"""
        if not self.connected or not self.client:
            raise Exception("Not connected to Azure Sentinel")
        
        try:
            # Build KQL query
            kql_query = self._build_kql_query(query)
            
            # Set timespan
            timespan = timedelta(hours=24)  # Default 24 hours
            if "timespan" in query:
                timespan = self._parse_timespan(query["timespan"])
            
            # Execute query
            response = await asyncio.to_thread(
                self.client.query_workspace,
                workspace_id=self.config.workspace_id,
                query=kql_query,
                timespan=timespan
            )
            
            # Process results
            results = []
            if response.tables:
                table = response.tables[0]
                for row in table.rows:
                    result = {}
                    for i, column in enumerate(table.columns):
                        result[column.name] = row[i]
                    results.append(result)
            
            return {
                "hits": {
                    "total": {"value": len(results)},
                    "hits": [{"_source": result} for result in results]
                },
                "took": 0,  # Azure doesn't provide timing
                "_metadata": {
                    "kql_query": kql_query,
                    "workspace_id": self.config.workspace_id
                }
            }
            
        except Exception as e:
            logger.error(f"Azure Sentinel query execution failed: {e}")
            raise
    
    async def get_schema(self) -> Dict[str, Any]:
        """Get Azure Sentinel schema information"""
        if not self.connected or not self.client:
            raise Exception("Not connected to Azure Sentinel")
        
        try:
            # Get table schemas
            schema_query = """
            union withsource=TableName *
            | summarize count() by TableName
            | order by count_ desc
            | take 50
            """
            
            response = await asyncio.to_thread(
                self.client.query_workspace,
                workspace_id=self.config.workspace_id,
                query=schema_query,
                timespan=timedelta(days=1)
            )
            
            tables = []
            if response.tables:
                table = response.tables[0]
                for row in table.rows:
                    tables.append({
                        "name": row[0],
                        "record_count": row[1]
                    })
            
            return {
                "platform": "azure_sentinel",
                "workspace_id": self.config.workspace_id,
                "tables": tables
            }
            
        except Exception as e:
            logger.error(f"Error getting Azure Sentinel schema: {e}")
            return {}
    
    def _build_kql_query(self, query: Dict[str, Any]) -> str:
        """Build KQL query from structured query"""
        if "query" in query and isinstance(query["query"], str):
            return query["query"]
        
        # Default to SecurityEvent table
        table = "SecurityEvent"
        kql_parts = [table]
        
        # Add WHERE conditions
        conditions = []
        if "query" in query and "bool" in query["query"]:
            bool_query = query["query"]["bool"]
            
            for must_clause in bool_query.get("must", []):
                condition = self._process_kql_clause(must_clause)
                if condition:
                    conditions.append(condition)
        
        if conditions:
            kql_parts.append(f"| where {' and '.join(conditions)}")
        
        # Add limit
        limit = query.get("size", 100)
        kql_parts.append(f"| take {limit}")
        
        return " ".join(kql_parts)
    
    def _process_kql_clause(self, clause: Dict[str, Any]) -> Optional[str]:
        """Process query clause for KQL"""
        if "match" in clause:
            field, value = next(iter(clause["match"].items()))
            return f'{field} contains "{value}"'
        elif "term" in clause:
            field, value = next(iter(clause["term"].items()))
            if isinstance(value, dict):
                value = value.get("value", value)
            return f'{field} == "{value}"'
        elif "range" in clause:
            field, range_values = next(iter(clause["range"].items()))
            conditions = []
            if "gte" in range_values:
                conditions.append(f'{field} >= datetime("{range_values["gte"]}")')
            if "lte" in range_values:
                conditions.append(f'{field} <= datetime("{range_values["lte"]}")')
            return " and ".join(conditions)
        
        return None
    
    def _parse_timespan(self, timespan_str: str) -> timedelta:
        """Parse timespan string to timedelta"""
        if timespan_str == "P1D":
            return timedelta(days=1)
        elif timespan_str == "PT1H":
            return timedelta(hours=1)
        elif timespan_str == "P7D":
            return timedelta(days=7)
        else:
            return timedelta(hours=24)


class DataNormalizer:
    """Data normalization for different SIEM platforms"""
    
    def __init__(self):
        self.field_mappings = self._load_field_mappings()
        
    def normalize_event(self, raw_event: Dict[str, Any], source_platform: str) -> NormalizedEvent:
        """Normalize event from any SIEM platform"""
        try:
            mappings = self.field_mappings.get(source_platform, {})
            
            # Extract common fields
            timestamp = self._extract_timestamp(raw_event, mappings)
            event_type = self._extract_field(raw_event, mappings, "event_type", "unknown")
            severity = self._extract_field(raw_event, mappings, "severity", "info")
            message = self._extract_field(raw_event, mappings, "message", "")
            
            # Create normalized event
            normalized = NormalizedEvent(
                timestamp=timestamp,
                event_type=event_type,
                severity=severity,
                source_system=source_platform,
                message=message,
                
                # Network fields
                source_ip=self._extract_field(raw_event, mappings, "source_ip"),
                destination_ip=self._extract_field(raw_event, mappings, "destination_ip"),
                source_port=self._extract_field(raw_event, mappings, "source_port", converter=int),
                destination_port=self._extract_field(raw_event, mappings, "destination_port", converter=int),
                protocol=self._extract_field(raw_event, mappings, "protocol"),
                
                # User fields
                username=self._extract_field(raw_event, mappings, "username"),
                user_domain=self._extract_field(raw_event, mappings, "user_domain"),
                
                # Host fields
                hostname=self._extract_field(raw_event, mappings, "hostname"),
                host_ip=self._extract_field(raw_event, mappings, "host_ip"),
                
                # Process fields
                process_name=self._extract_field(raw_event, mappings, "process_name"),
                process_id=self._extract_field(raw_event, mappings, "process_id", converter=int),
                
                # File fields
                file_path=self._extract_field(raw_event, mappings, "file_path"),
                file_hash=self._extract_field(raw_event, mappings, "file_hash"),
                
                # Security fields
                event_id=self._extract_field(raw_event, mappings, "event_id"),
                rule_name=self._extract_field(raw_event, mappings, "rule_name"),
                threat_name=self._extract_field(raw_event, mappings, "threat_name"),
                
                # Metadata
                raw_data=raw_event,
                tags=self._generate_tags(raw_event, source_platform)
            )
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing event: {e}")
            # Return minimal normalized event
            return NormalizedEvent(
                timestamp=datetime.now().isoformat(),
                event_type="unknown",
                severity="info",
                source_system=source_platform,
                message=str(raw_event),
                raw_data=raw_event
            )
    
    def _extract_timestamp(self, event: Dict[str, Any], mappings: Dict[str, Any]) -> str:
        """Extract timestamp from event"""
        timestamp_fields = mappings.get("timestamp", ["@timestamp", "timestamp", "_time"])
        
        for field in timestamp_fields:
            value = self._get_nested_field(event, field)
            if value:
                try:
                    # Try to parse and normalize timestamp
                    if isinstance(value, str):
                        # Try ISO format first
                        try:
                            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            return dt.isoformat()
                        except:
                            pass
                    
                    # Return as-is if parsing fails
                    return str(value)
                except:
                    continue
        
        # Default to current time
        return datetime.now().isoformat()
    
    def _extract_field(
        self, 
        event: Dict[str, Any], 
        mappings: Dict[str, Any], 
        field_name: str, 
        default: Any = None,
        converter: Optional[callable] = None
    ) -> Any:
        """Extract field with optional type conversion"""
        field_mappings = mappings.get(field_name, [field_name])
        
        for field in field_mappings:
            value = self._get_nested_field(event, field)
            if value is not None:
                try:
                    if converter:
                        return converter(value)
                    return value
                except:
                    continue
        
        return default
    
    def _get_nested_field(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get nested field using dot notation"""
        try:
            current = data
            for part in field_path.split('.'):
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            return current
        except:
            return None
    
    def _generate_tags(self, event: Dict[str, Any], source_platform: str) -> List[str]:
        """Generate tags for the event"""
        tags = [f"source:{source_platform}"]
        
        # Add tags based on content
        if self._get_nested_field(event, "error"):
            tags.append("error")
        if self._get_nested_field(event, "warning"):
            tags.append("warning")
        if "malware" in str(event).lower():
            tags.append("malware")
        if "failed" in str(event).lower():
            tags.append("failed")
        
        return tags
    
    def _load_field_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Load field mappings for different platforms"""
        return {
            "splunk": {
                "timestamp": ["_time", "timestamp"],
                "event_type": ["eventtype", "sourcetype"],
                "severity": ["severity", "priority"],
                "message": ["_raw", "message"],
                "source_ip": ["src_ip", "src", "clientip"],
                "destination_ip": ["dest_ip", "dest", "serverip"],
                "source_port": ["src_port"],
                "destination_port": ["dest_port"],
                "protocol": ["protocol", "transport"],
                "username": ["user", "username", "src_user"],
                "hostname": ["host", "hostname", "computername"],
                "process_name": ["process", "process_name", "image"],
                "event_id": ["signature_id", "event_id"],
                "rule_name": ["signature", "rule_name"]
            },
            
            "qradar": {
                "timestamp": ["starttime", "endtime", "devicetime"],
                "event_type": ["category", "qidname"],
                "severity": ["severity", "magnitude"],
                "message": ["message", "payload"],
                "source_ip": ["sourceip"],
                "destination_ip": ["destinationip"],
                "source_port": ["sourceport"],
                "destination_port": ["destinationport"],
                "username": ["username", "sourceusername"],
                "hostname": ["hostname", "sourcehost"],
                "process_name": ["processname", "applicationname"],
                "event_id": ["qid", "eventid"]
            },
            
            "azure_sentinel": {
                "timestamp": ["TimeGenerated", "EventTime"],
                "event_type": ["EventID", "Type"],
                "severity": ["Severity", "Level"],
                "message": ["Message", "Description"],
                "source_ip": ["SourceIP", "ClientIP"],
                "destination_ip": ["DestinationIP", "ServerIP"],
                "source_port": ["SourcePort"],
                "destination_port": ["DestinationPort"],
                "username": ["Account", "UserName"],
                "hostname": ["Computer", "HostName"],
                "process_name": ["ProcessName", "Image"],
                "event_id": ["EventID", "RuleId"]
            }
        }


# Factory function for creating SIEM connectors
def create_siem_connector(platform: str, config: SIEMConfig) -> SIEMConnectorBase:
    """Create SIEM connector for specified platform"""
    platform_lower = platform.lower()
    
    if platform_lower == "splunk":
        return SplunkConnector(config)
    elif platform_lower == "qradar":
        return QRadarConnector(config)
    elif platform_lower in ["azure_sentinel", "sentinel"]:
        return AzureSentinelConnector(config)
    else:
        raise ValueError(f"Unsupported SIEM platform: {platform}")


# Streaming data processor
class StreamingProcessor:
    """Real-time streaming data processor"""
    
    def __init__(self, normalizer: DataNormalizer):
        self.normalizer = normalizer
        self.subscribers = []
        
    def subscribe(self, callback: callable):
        """Subscribe to streaming events"""
        self.subscribers.append(callback)
    
    async def process_stream(self, connector: SIEMConnectorBase, query: Dict[str, Any]):
        """Process streaming data from SIEM"""
        try:
            while True:
                # Execute query to get latest events
                results = await connector.execute_query(query)
                
                # Process each event
                for hit in results.get("hits", {}).get("hits", []):
                    raw_event = hit.get("_source", {})
                    
                    # Normalize event
                    normalized = self.normalizer.normalize_event(raw_event, connector.__class__.__name__.lower().replace("connector", ""))
                    
                    # Notify subscribers
                    for callback in self.subscribers:
                        try:
                            await callback(normalized)
                        except Exception as e:
                            logger.error(f"Error in stream callback: {e}")
                
                # Wait before next poll
                await asyncio.sleep(30)  # Poll every 30 seconds
                
        except Exception as e:
            logger.error(f"Streaming processor error: {e}")


# Export main classes
__all__ = [
    'SIEMConfig',
    'NormalizedEvent', 
    'SplunkConnector',
    'QRadarConnector',
    'AzureSentinelConnector',
    'DataNormalizer',
    'StreamingProcessor',
    'create_siem_connector'
]

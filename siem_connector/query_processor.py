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
"""
Utility functions for SIEM connectors.
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def parse_time_range(time_str: str) -> Dict[str, str]:
    """Parse natural language time ranges to datetime strings."""
    now = datetime.now()
    
    time_mappings = {
        'last hour': now - timedelta(hours=1),
        'last 24 hours': now - timedelta(days=1),
        'last day': now - timedelta(days=1),
        'last week': now - timedelta(weeks=1),
        'last month': now - timedelta(days=30),
        'today': now.replace(hour=0, minute=0, second=0, microsecond=0),
        'yesterday': (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    }
    
    if time_str.lower() in time_mappings:
        start_time = time_mappings[time_str.lower()]
        return {
            'gte': start_time.isoformat(),
            'lte': now.isoformat()
        }
    
    # Default to last hour if no match
    return {
        'gte': (now - timedelta(hours=1)).isoformat(),
        'lte': now.isoformat()
    }


def normalize_log_entry(log_entry: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Normalize log entries from different sources to a common format."""
    normalized = {
        'timestamp': None,
        'source': source,
        'event_type': None,
        'severity': None,
        'message': None,
        'source_ip': None,
        'dest_ip': None,
        'user': None,
        'raw': log_entry
    }
    
    try:
        if source == 'elasticsearch':
            normalized.update({
                'timestamp': log_entry.get('_source', {}).get('@timestamp'),
                'message': log_entry.get('_source', {}).get('message'),
                'source_ip': log_entry.get('_source', {}).get('source', {}).get('ip'),
                'dest_ip': log_entry.get('_source', {}).get('destination', {}).get('ip'),
                'user': log_entry.get('_source', {}).get('user', {}).get('name'),
                'event_type': log_entry.get('_source', {}).get('event', {}).get('type'),
                'severity': log_entry.get('_source', {}).get('log', {}).get('level')
            })
        
        elif source == 'wazuh':
            normalized.update({
                'timestamp': log_entry.get('timestamp'),
                'message': log_entry.get('rule', {}).get('description'),
                'source_ip': log_entry.get('data', {}).get('srcip'),
                'user': log_entry.get('data', {}).get('srcuser'),
                'event_type': log_entry.get('rule', {}).get('groups', [None])[0],
                'severity': log_entry.get('rule', {}).get('level')
            })
    
    except Exception as e:
        logger.warning(f"Failed to normalize log entry: {e}")
    
    return normalized


def format_query_results(results: List[Dict[str, Any]], format_type: str = 'table') -> str:
    """Format query results for display."""
    if not results:
        return "No results found."
    
    if format_type == 'json':
        return json.dumps(results, indent=2, default=str)
    
    elif format_type == 'table':
        # Simple table format
        if not results:
            return "No data to display."
        
        headers = list(results[0].keys())
        table = f"{'|'.join(headers)}\n"
        table += f"{'|'.join(['-' * len(h) for h in headers])}\n"
        
        for row in results[:10]:  # Limit to first 10 rows
            values = [str(row.get(h, '')) for h in headers]
            table += f"{'|'.join(values)}\n"
        
        if len(results) > 10:
            table += f"\n... and {len(results) - 10} more rows"
        
        return table
    
    return str(results)


def extract_common_fields(log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract commonly used fields from log entries for summary."""
    if not log_entries:
        return {}
    
    summary = {
        'total_events': len(log_entries),
        'time_range': {
            'earliest': None,
            'latest': None
        },
        'event_types': {},
        'severity_distribution': {},
        'top_source_ips': {},
        'top_users': {},
        'unique_indices': set()
    }
    
    for entry in log_entries:
        # Handle both normalized and raw entries
        source = entry.get('source', entry)
        
        # Extract timestamp
        timestamp = source.get('@timestamp') or source.get('timestamp')
        if timestamp:
            if not summary['time_range']['earliest'] or timestamp < summary['time_range']['earliest']:
                summary['time_range']['earliest'] = timestamp
            if not summary['time_range']['latest'] or timestamp > summary['time_range']['latest']:
                summary['time_range']['latest'] = timestamp
        
        # Extract event type
        event_type = (source.get('event', {}).get('type') or 
                     source.get('event_type') or 
                     source.get('log', {}).get('level') or 'unknown')
        summary['event_types'][event_type] = summary['event_types'].get(event_type, 0) + 1
        
        # Extract severity
        severity = (source.get('rule', {}).get('level') or 
                   source.get('log', {}).get('level') or 
                   source.get('severity') or 'unknown')
        summary['severity_distribution'][str(severity)] = summary['severity_distribution'].get(str(severity), 0) + 1
        
        # Extract source IP
        source_ip = (source.get('source', {}).get('ip') or 
                    source.get('client', {}).get('ip') or 
                    source.get('src_ip'))
        if source_ip:
            summary['top_source_ips'][source_ip] = summary['top_source_ips'].get(source_ip, 0) + 1
        
        # Extract user
        user = (source.get('user', {}).get('name') or 
               source.get('user') or 
               source.get('username'))
        if user:
            summary['top_users'][user] = summary['top_users'].get(user, 0) + 1
        
        # Extract index
        index = entry.get('index') or entry.get('_index')
        if index:
            summary['unique_indices'].add(index)
    
    # Convert sets to lists for JSON serialization
    summary['unique_indices'] = list(summary['unique_indices'])
    
    # Sort top items by frequency
    summary['top_source_ips'] = dict(sorted(summary['top_source_ips'].items(), 
                                          key=lambda x: x[1], reverse=True)[:10])
    summary['top_users'] = dict(sorted(summary['top_users'].items(), 
                                     key=lambda x: x[1], reverse=True)[:10])
    
    return summary


def convert_to_dataframe(results: List[Dict[str, Any]]) -> Any:
    """Convert query results to pandas DataFrame."""
    try:
        import pandas as pd
        
        if not results:
            return pd.DataFrame()
        
        # Flatten nested dictionaries for better DataFrame representation
        flattened_results = []
        for result in results:
            flattened = flatten_dict(result.get('source', result))
            flattened_results.append(flattened)
        
        df = pd.DataFrame(flattened_results)
        return df
        
    except ImportError:
        logger.warning("Pandas not available, cannot convert to DataFrame")
        return None
    except Exception as e:
        logger.error(f"Failed to convert to DataFrame: {e}")
        return None


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            # Handle list of dictionaries by taking the first item
            items.extend(flatten_dict(v[0], new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def sanitize_query_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize response by removing sensitive information."""
    # Fields that might contain sensitive data
    sensitive_fields = [
        'password', 'passwd', 'secret', 'token', 'key', 'credential',
        'authorization', 'cookie', 'session'
    ]
    
    def remove_sensitive(obj):
        if isinstance(obj, dict):
            return {k: remove_sensitive(v) for k, v in obj.items() 
                   if not any(sensitive in k.lower() for sensitive in sensitive_fields)}
        elif isinstance(obj, list):
            return [remove_sensitive(item) for item in obj]
        else:
            return obj
    
    return remove_sensitive(response)


def validate_query_dsl(query: Dict[str, Any]) -> tuple[bool, str]:
    """Validate Elasticsearch DSL query structure."""
    try:
        # Check if query has required structure
        if not isinstance(query, dict):
            return False, "Query must be a dictionary"
        
        # Check for query clause
        if 'query' not in query:
            return False, "Query must contain 'query' clause"
        
        query_clause = query['query']
        if not isinstance(query_clause, dict):
            return False, "Query clause must be a dictionary"
        
        # Validate common query types
        valid_query_types = [
            'match', 'match_all', 'term', 'terms', 'range', 'bool', 
            'query_string', 'multi_match', 'exists', 'wildcard'
        ]
        
        if not any(qt in query_clause for qt in valid_query_types):
            return False, f"Query must contain one of: {', '.join(valid_query_types)}"
        
        # Additional size validation
        size = query.get('size', 10)
        if not isinstance(size, int) or size < 0 or size > 10000:
            return False, "Size must be an integer between 0 and 10000"
        
        return True, "Valid query"
        
    except Exception as e:
        return False, f"Query validation error: {str(e)}"


def build_error_response(error_message: str, query: str = None) -> Dict[str, Any]:
    """Build standardized error response."""
    return {
        'hits': [],
        'aggregations': {},
        'metadata': {
            'total_hits': 0,
            'error': error_message,
            'query': query,
            'timestamp': datetime.now().isoformat()
        }
    }
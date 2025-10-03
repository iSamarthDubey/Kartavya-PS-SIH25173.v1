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
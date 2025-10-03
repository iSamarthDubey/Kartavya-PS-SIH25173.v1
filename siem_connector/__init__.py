"""
SIEM Connector Module

This module provides connectors and utilities for integrating with various SIEM platforms.
Supports Elasticsearch, Wazuh, and other security information and event management systems.
"""

from .elastic_connector import ElasticConnector
from .wazuh_connector import WazuhConnector
from .query_processor import SIEMQueryProcessor, create_siem_processor
from .utils import (
    normalize_log_entry,
    extract_common_fields,
    sanitize_query_response,
    validate_query_dsl,
    build_error_response,
    convert_to_dataframe,
    format_query_results,
    parse_time_range,
    flatten_dict
)

__version__ = "1.0.0"
__author__ = "SIEM NLP Assistant Team"

# Export main classes and functions
__all__ = [
    # Main processor
    'SIEMQueryProcessor',
    'create_siem_processor',
    
    # Connectors
    'ElasticConnector',
    'WazuhConnector', 
    
    # Utility functions
    'normalize_log_entry',
    'extract_common_fields',
    'sanitize_query_response',
    'validate_query_dsl',
    'build_error_response',
    'convert_to_dataframe',
    'format_query_results',
    'parse_time_range',
    'flatten_dict'
]

# Supported SIEM platforms
SUPPORTED_PLATFORMS = ['elasticsearch', 'wazuh']

def get_supported_platforms():
    """Get list of supported SIEM platforms."""
    return SUPPORTED_PLATFORMS.copy()
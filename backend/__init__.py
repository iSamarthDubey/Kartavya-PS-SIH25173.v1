"""
Backend module for SIEM NLP Assistant.

This module contains core processing components:
- NLP analysis (intent classification, entity extraction)
- Query generation (NL to Elasticsearch DSL)
- Response formatting
"""

__version__ = "1.0.0"

# Import main components for easy access
try:
    from .query_builder import QueryBuilder
    from .elastic_client import ElasticsearchClient
    
    __all__ = [
        'QueryBuilder',
        'ElasticsearchClient',
    ]
except ImportError:
    # Allow module to be imported even if dependencies aren't installed
    __all__ = []

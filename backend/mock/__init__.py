"""
Dynamic Mock Data System for SIEM Demo
=====================================

This module provides realistic, time-varying mock data sources that simulate
real SIEM platforms like Elasticsearch, Wazuh, etc. for demonstration purposes.

Features:
- Dynamic data generation every few seconds
- Realistic security event patterns
- Platform-aware data structures
- API-compatible with real data sources
- No hardcoded/static data - everything is generated dynamically
"""

__version__ = "1.0.0"
__author__ = "Kartavya SIEM Team"

from .connectors import MockElasticsearchConnector
from .generators import (
    WindowsEventGenerator,
    SystemMetricsGenerator,
    AuthenticationEventGenerator
)

__all__ = [
    "MockElasticsearchConnector",
    "WindowsEventGenerator",
    "SystemMetricsGenerator", 
    "AuthenticationEventGenerator"
]

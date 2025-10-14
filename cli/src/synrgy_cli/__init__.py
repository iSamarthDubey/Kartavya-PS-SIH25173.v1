"""
SYNRGY CLI - Production-ready SIEM NLP Assistant Command Line Interface

A comprehensive CLI tool for interacting with the SYNRGY SIEM platform.
Provides natural language query processing, threat hunting capabilities,
and comprehensive security event analysis.

Features:
- Interactive assistant chat with NLP query processing
- Platform event analysis and filtering
- Report generation and management
- Query translation and optimization
- Dashboard metrics and alerting
- Admin user management and audit logs
"""

__version__ = "1.0.0"
__author__ = "SYNRGY Team"
__email__ = "support@synrgy.dev"

from .core.config import Config
from .core.client import APIClient
from .core.output import OutputFormatter

__all__ = ["Config", "APIClient", "OutputFormatter", "__version__"]

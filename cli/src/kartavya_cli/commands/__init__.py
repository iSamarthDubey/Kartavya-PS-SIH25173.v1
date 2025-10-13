"""
Commands package for Kartavya CLI
Contains all command modules for the CLI application
"""

# Import all command modules for easy access
from . import assistant
from . import platform_events
from . import reports
from . import query
from . import dashboard
from . import admin
from . import config

__all__ = [
    "assistant",
    "platform_events", 
    "reports",
    "query",
    "dashboard",
    "admin",
    "config"
]

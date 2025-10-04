"""
Response Formatter Package for SIEM Query Results

Components:
- ResponseFormatter: Main formatting orchestrator
- TextFormatter: Plain text formatting
- ChartFormatter: Chart/visualization generation
- DashboardExport: Export to dashboard formats
"""

__version__ = "1.0.0"

try:
    from .formatter import ResponseFormatter, FormattedResponse
    from .text_formatter import TextFormatter
    from .chart_formatter import ChartFormatter
    
    __all__ = [
        'ResponseFormatter',
        'FormattedResponse',
        'TextFormatter',
        'ChartFormatter',
    ]
except ImportError:
    __all__ = []
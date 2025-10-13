"""
Output formatting utilities for displaying API responses
Supports table, JSON, CSV formats with rich styling
"""

import csv
import json
import sys
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.json import JSON
from rich.tree import Tree
from tabulate import tabulate

from .config import get_config

console = Console()


class OutputFormatter:
    """Formats API responses for different output modes"""
    
    def __init__(self, format_type: Optional[str] = None):
        self.config = get_config()
        self.format = format_type or self.config.output_format
        self.use_color = self.config.color
    
    def format_response(self, data: Any, title: Optional[str] = None) -> str:
        """Format response data based on configured format"""
        if self.format == "json":
            return self.format_json(data)
        elif self.format == "csv":
            return self.format_csv(data)
        elif self.format == "table":
            return self.format_table(data, title)
        else:
            return self.format_table(data, title)
    
    def format_json(self, data: Any) -> str:
        """Format data as JSON"""
        return json.dumps(data, indent=2, default=str)
    
    def format_csv(self, data: Any) -> str:
        """Format data as CSV"""
        output = StringIO()
        
        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], list):
                data = data["data"]
            else:
                # Flatten dict into single row
                writer = csv.DictWriter(output, fieldnames=data.keys())
                writer.writeheader()
                writer.writerow(data)
                return output.getvalue()
        
        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                fieldnames = set()
                for item in data:
                    fieldnames.update(item.keys())
                
                writer = csv.DictWriter(output, fieldnames=list(fieldnames))
                writer.writeheader()
                for item in data:
                    writer.writerow(item)
            else:
                writer = csv.writer(output)
                for item in data:
                    writer.writerow([item])
        else:
            writer = csv.writer(output)
            writer.writerow([data])
        
        return output.getvalue()
    
    def format_table(self, data: Any, title: Optional[str] = None) -> str:
        """Format data as a rich table"""
        if not self.use_color:
            # Plain table format
            return self._format_plain_table(data)
        
        # Rich table format
        if isinstance(data, dict):
            return self._format_dict_table(data, title)
        elif isinstance(data, list):
            return self._format_list_table(data, title)
        else:
            return str(data)
    
    def _format_plain_table(self, data: Any) -> str:
        """Format data as plain text table using tabulate"""
        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], list):
                data = data["data"]
            else:
                rows = [[k, v] for k, v in data.items()]
                return tabulate(rows, headers=["Key", "Value"], tablefmt="grid")
        
        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                return tabulate(data, headers="keys", tablefmt="grid")
            else:
                return tabulate([[item] for item in data], headers=["Value"], tablefmt="grid")
        
        return str(data)
    
    def _format_dict_table(self, data: Dict, title: Optional[str] = None) -> str:
        """Format dictionary as rich table"""
        # Handle API response wrapper
        if "data" in data and isinstance(data["data"], (list, dict)):
            main_data = data["data"]
            metadata = {k: v for k, v in data.items() if k != "data"}
            
            result = self._format_data_as_table(main_data, title)
            
            if metadata:
                result += "\\n\\n" + self._format_metadata(metadata)
            
            return result
        else:
            return self._format_data_as_table(data, title)
    
    def _format_list_table(self, data: List, title: Optional[str] = None) -> str:
        """Format list as rich table"""
        return self._format_data_as_table(data, title)
    
    def _format_data_as_table(self, data: Any, title: Optional[str] = None) -> str:
        """Format any data structure as a table"""
        table = Table(show_header=True, header_style="bold magenta")
        
        if title:
            table.title = title
        
        if isinstance(data, dict):
            table.add_column("Key", style="cyan", no_wrap=True)
            table.add_column("Value", style="green")
            
            for key, value in data.items():
                # Format complex values
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, indent=2, default=str)[:200]
                    if len(str(value)) > 200:
                        value_str += "..."
                else:
                    value_str = str(value)
                
                table.add_row(str(key), value_str)
        
        elif isinstance(data, list) and data:
            if isinstance(data[0], dict):
                # List of dictionaries - create columns from keys
                all_keys = set()
                for item in data:
                    if isinstance(item, dict):
                        all_keys.update(item.keys())
                
                # Add columns
                for key in sorted(all_keys):
                    table.add_column(str(key), style="dim")
                
                # Add rows
                for item in data:
                    if isinstance(item, dict):
                        row = []
                        for key in sorted(all_keys):
                            value = item.get(key, "")
                            if isinstance(value, (dict, list)):
                                value_str = json.dumps(value, default=str)[:100]
                                if len(str(value)) > 100:
                                    value_str += "..."
                            else:
                                value_str = str(value)
                            row.append(value_str)
                        table.add_row(*row)
                    else:
                        table.add_row(str(item))
            else:
                # List of simple values
                table.add_column("Value", style="green")
                for item in data:
                    table.add_row(str(item))
        else:
            # Single value
            table.add_column("Value", style="green")
            table.add_row(str(data))
        
        with console.capture() as capture:
            console.print(table)
        
        return capture.get()
    
    def _format_metadata(self, metadata: Dict) -> str:
        """Format metadata section"""
        if not metadata:
            return ""
        
        table = Table(title="Metadata", show_header=True, header_style="bold yellow")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="dim")
        
        for key, value in metadata.items():
            table.add_row(str(key), str(value))
        
        with console.capture() as capture:
            console.print(table)
        
        return capture.get()


def print_success(message: str):
    """Print success message"""
    config = get_config()
    if config.color:
        console.print(f"✅ {message}", style="bold green")
    else:
        print(f"SUCCESS: {message}")


def print_error(message: str):
    """Print error message"""
    config = get_config()
    if config.color:
        console.print(f"❌ {message}", style="bold red")
    else:
        print(f"ERROR: {message}", file=sys.stderr)


def print_warning(message: str):
    """Print warning message"""
    config = get_config()
    if config.color:
        console.print(f"⚠️ {message}", style="bold yellow")
    else:
        print(f"WARNING: {message}")


def print_info(message: str):
    """Print info message"""
    config = get_config()
    if config.color:
        console.print(f"ℹ️ {message}", style="bold blue")
    else:
        print(f"INFO: {message}")


def print_output(data: Any, title: Optional[str] = None, format_type: Optional[str] = None):
    """Print formatted output"""
    formatter = OutputFormatter(format_type)
    output = formatter.format_response(data, title)
    
    if formatter.use_color and formatter.format == "json":
        # Use rich JSON formatting for colored JSON
        console.print(JSON(output))
    else:
        print(output)


def print_chat_response(response: Dict[str, Any]):
    """Print chat response with special formatting"""
    config = get_config()
    
    if not config.color:
        print_output(response)
        return
    
    # Extract key information
    query = response.get("query", "")
    summary = response.get("summary", "")
    results = response.get("results", [])
    intent = response.get("intent", "")
    confidence = response.get("confidence", 0.0)
    
    # Print query
    console.print(Panel(f"[bold cyan]Query:[/bold cyan] {query}", title="User Query"))
    
    # Print summary
    if summary:
        console.print(Panel(f"[green]{summary}[/green]", title="Summary"))
    
    # Print metadata
    metadata_text = f"Intent: [yellow]{intent}[/yellow] | Confidence: [blue]{confidence:.2%}[/blue]"
    if response.get("status"):
        metadata_text += f" | Status: [magenta]{response['status']}[/magenta]"
    
    console.print(metadata_text)
    
    # Print results if available
    if results:
        console.print("\\n")
        print_output(results, "Results")
    
    # Print suggestions
    suggestions = response.get("suggestions", [])
    if suggestions:
        console.print("\\n[bold]💡 Suggestions:[/bold]")
        for i, suggestion in enumerate(suggestions, 1):
            console.print(f"  {i}. {suggestion}")


def format_timestamp(timestamp: Union[str, datetime]) -> str:
    """Format timestamp for display"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return timestamp
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

"""
Output formatting utilities for the Kartavya CLI.

Provides rich formatting for different output types including tables,
JSON, CSV, and styled console output with colors and formatting.
"""

import json
import csv
import io
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from rich.console import Console
from rich.table import Table, Column
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.tree import Tree
from tabulate import tabulate

from .config import Config

class OutputFormatter:
    """Handles formatted output for various data types and formats."""
    
    def __init__(self, config: Optional[Config] = None, console: Optional[Console] = None):
        """Initialize the output formatter."""
        self.config = config or Config()
        self.console = console or Console()
        self.output_config = self.config.get_output_config()
    
    def format_data(
        self, 
        data: Union[Dict, List, str], 
        format_type: Optional[str] = None,
        title: Optional[str] = None
    ) -> str:
        """Format data according to specified format type."""
        format_type = format_type or self.output_config.get('format', 'table')
        
        if isinstance(data, str):
            return self.format_text(data, title)
        elif isinstance(data, dict):
            return self.format_dict(data, format_type, title)
        elif isinstance(data, list):
            return self.format_list(data, format_type, title)
        else:
            return str(data)
    
    def format_text(self, text: str, title: Optional[str] = None) -> str:
        """Format plain text with optional title."""
        if title:
            return f"\n{title}\n{'=' * len(title)}\n{text}\n"
        return text
    
    def format_dict(self, data: Dict, format_type: str = 'table', title: Optional[str] = None) -> str:
        """Format dictionary data."""
        if format_type == 'json':
            return self.to_json(data, title)
        elif format_type == 'yaml':
            return self.to_yaml(data, title)
        else:
            return self.dict_to_table(data, title)
    
    def format_list(self, data: List, format_type: str = 'table', title: Optional[str] = None) -> str:
        """Format list data."""
        if not data:
            return self.format_text("No data available", title)
        
        if format_type == 'json':
            return self.to_json(data, title)
        elif format_type == 'csv':
            return self.to_csv(data, title)
        elif format_type == 'yaml':
            return self.to_yaml(data, title)
        else:
            return self.list_to_table(data, title)
    
    def print_data(
        self, 
        data: Union[Dict, List, str], 
        format_type: Optional[str] = None,
        title: Optional[str] = None,
        style: Optional[str] = None
    ):
        """Print formatted data to console."""
        if isinstance(data, str) and not title:
            self.console.print(data, style=style)
            return
            
        format_type = format_type or self.output_config.get('format', 'table')
        
        if isinstance(data, str):
            self.print_text(data, title, style)
        elif isinstance(data, dict):
            self.print_dict(data, format_type, title)
        elif isinstance(data, list):
            self.print_list(data, format_type, title)
        else:
            self.console.print(str(data), style=style)
    
    def print_text(self, text: str, title: Optional[str] = None, style: Optional[str] = None):
        """Print formatted text."""
        if title:
            self.console.print(Panel.fit(text, title=title, border_style=style or "blue"))
        else:
            self.console.print(text, style=style)
    
    def print_dict(self, data: Dict, format_type: str = 'table', title: Optional[str] = None):
        """Print formatted dictionary."""
        if format_type == 'json':
            self.print_json(data, title)
        else:
            table = self.create_key_value_table(data, title)
            self.console.print(table)
    
    def print_list(self, data: List, format_type: str = 'table', title: Optional[str] = None):
        """Print formatted list."""
        if not data:
            self.console.print("[dim]No data available[/dim]")
            return
            
        if format_type == 'json':
            self.print_json(data, title)
        else:
            table = self.create_data_table(data, title)
            self.console.print(table)
    
    def create_key_value_table(self, data: Dict, title: Optional[str] = None) -> Table:
        """Create a key-value table from dictionary."""
        table = Table(
            Column("Key", style="cyan", no_wrap=True),
            Column("Value", style="white"),
            title=title,
            show_header=True,
            header_style="bold blue",
            border_style="blue"
        )
        
        for key, value in data.items():
            # Format value based on type
            if isinstance(value, (dict, list)):
                formatted_value = json.dumps(value, indent=2, default=str)
            elif isinstance(value, datetime):
                formatted_value = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                formatted_value = str(value)
            
            table.add_row(str(key), formatted_value)
        
        return table
    
    def create_data_table(self, data: List[Dict], title: Optional[str] = None) -> Table:
        """Create a table from list of dictionaries."""
        if not data or not isinstance(data[0], dict):
            # Handle list of non-dict items
            table = Table(
                Column("Item", style="white"),
                title=title,
                show_header=True,
                header_style="bold blue",
                border_style="blue"
            )
            for item in data:
                table.add_row(str(item))
            return table
        
        # Get all unique keys from all dictionaries
        all_keys = set()
        for item in data:
            if isinstance(item, dict):
                all_keys.update(item.keys())
        
        columns = []
        for key in sorted(all_keys):
            # Style based on key name
            style = "cyan" if "id" in key.lower() else "white"
            if "time" in key.lower() or "date" in key.lower():
                style = "green"
            elif "status" in key.lower() or "level" in key.lower():
                style = "yellow"
            
            columns.append(Column(
                str(key).replace('_', ' ').title(),
                style=style,
                no_wrap=True if len(str(key)) < 15 else False
            ))
        
        table = Table(
            *columns,
            title=title,
            show_header=True,
            header_style="bold blue",
            border_style="blue",
            row_styles=["none", "dim"]
        )
        
        for item in data:
            if isinstance(item, dict):
                row = []
                for key in sorted(all_keys):
                    value = item.get(key, "")
                    
                    # Format value based on type
                    if isinstance(value, datetime):
                        formatted_value = value.strftime("%Y-%m-%d %H:%M:%S")
                    elif isinstance(value, (dict, list)):
                        formatted_value = json.dumps(value, default=str)[:50] + "..." if len(json.dumps(value, default=str)) > 50 else json.dumps(value, default=str)
                    else:
                        formatted_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    
                    row.append(formatted_value)
                
                table.add_row(*row)
        
        return table
    
    def print_json(self, data: Union[Dict, List], title: Optional[str] = None):
        """Print JSON-formatted data with syntax highlighting."""
        json_str = json.dumps(data, indent=2, default=str, ensure_ascii=False)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        
        if title:
            self.console.print(Panel(syntax, title=title, border_style="green"))
        else:
            self.console.print(syntax)
    
    def to_json(self, data: Union[Dict, List], title: Optional[str] = None) -> str:
        """Convert data to JSON string."""
        json_str = json.dumps(data, indent=2, default=str, ensure_ascii=False)
        if title:
            return f"\n# {title}\n{json_str}\n"
        return json_str
    
    def to_csv(self, data: List[Dict], title: Optional[str] = None) -> str:
        """Convert list of dictionaries to CSV string."""
        if not data:
            return ""
        
        output = io.StringIO()
        if title:
            output.write(f"# {title}\n")
        
        if isinstance(data[0], dict):
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        else:
            writer = csv.writer(output)
            for item in data:
                writer.writerow([str(item)])
        
        return output.getvalue()
    
    def to_yaml(self, data: Union[Dict, List], title: Optional[str] = None) -> str:
        """Convert data to YAML string."""
        try:
            import yaml
            yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            if title:
                return f"# {title}\n{yaml_str}"
            return yaml_str
        except ImportError:
            # Fallback to JSON if PyYAML not available
            return self.to_json(data, title)
    
    def dict_to_table(self, data: Dict, title: Optional[str] = None) -> str:
        """Convert dictionary to table format."""
        table_data = [[k, v] for k, v in data.items()]
        headers = ["Key", "Value"]
        
        table_str = tabulate(table_data, headers=headers, tablefmt="grid")
        
        if title:
            return f"\n{title}\n{'=' * len(title)}\n{table_str}\n"
        return table_str
    
    def list_to_table(self, data: List, title: Optional[str] = None) -> str:
        """Convert list to table format."""
        if not data:
            return "No data available"
        
        if isinstance(data[0], dict):
            # List of dictionaries
            headers = list(data[0].keys())
            table_data = [[item.get(k, "") for k in headers] for item in data]
            table_str = tabulate(table_data, headers=headers, tablefmt="grid")
        else:
            # Simple list
            table_data = [[i+1, str(item)] for i, item in enumerate(data)]
            headers = ["#", "Value"]
            table_str = tabulate(table_data, headers=headers, tablefmt="grid")
        
        if title:
            return f"\n{title}\n{'=' * len(title)}\n{table_str}\n"
        return table_str
    
    def save_to_file(
        self, 
        data: Union[Dict, List, str], 
        filepath: str, 
        format_type: Optional[str] = None
    ):
        """Save formatted data to file."""
        filepath = Path(filepath)
        format_type = format_type or filepath.suffix.lstrip('.') or 'json'
        
        formatted_data = self.format_data(data, format_type)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_data)
    
    def print_success(self, message: str):
        """Print success message."""
        self.console.print(f"✓ {message}", style="bold green")
    
    def print_error(self, message: str):
        """Print error message."""
        self.console.print(f"✗ {message}", style="bold red")
    
    def print_warning(self, message: str):
        """Print warning message."""
        self.console.print(f"⚠ {message}", style="bold yellow")
    
    def print_info(self, message: str):
        """Print info message."""
        self.console.print(f"ℹ {message}", style="bold blue")
    
    def create_progress(self, description: str = "Processing...") -> Progress:
        """Create a progress bar."""
        return Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
    
    def print_tree(self, data: Dict, title: str = "Data Structure"):
        """Print data as a tree structure."""
        tree = Tree(title)
        self._add_to_tree(tree, data)
        self.console.print(tree)
    
    def _add_to_tree(self, tree: Tree, data: Any, max_depth: int = 3, current_depth: int = 0):
        """Recursively add data to tree."""
        if current_depth >= max_depth:
            tree.add("[dim]...[/dim]")
            return
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)) and value:
                    subtree = tree.add(f"[cyan]{key}[/cyan]")
                    self._add_to_tree(subtree, value, max_depth, current_depth + 1)
                else:
                    tree.add(f"[cyan]{key}[/cyan]: {str(value)[:50]}")
        elif isinstance(data, list):
            for i, item in enumerate(data[:5]):  # Limit to first 5 items
                if isinstance(item, (dict, list)):
                    subtree = tree.add(f"[yellow][{i}][/yellow]")
                    self._add_to_tree(subtree, item, max_depth, current_depth + 1)
                else:
                    tree.add(f"[yellow][{i}][/yellow]: {str(item)[:50]}")
            if len(data) > 5:
                tree.add(f"[dim]... and {len(data) - 5} more items[/dim]")
        else:
            tree.add(str(data)[:100])

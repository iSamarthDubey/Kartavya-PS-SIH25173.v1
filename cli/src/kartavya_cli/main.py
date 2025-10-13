"""
Main CLI application for Kartavya SIEM NLP Assistant
Production-ready command line interface with comprehensive features
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from . import __version__
from .core.config import get_config, save_config, config_manager
from .core.client import APIError, get_client, run_async
from .core.output import print_error, print_success, print_info, print_output

from .commands import (
    assistant,
    platform_events,
    reports,
    query,
    dashboard,
    admin,
    config as config_cmd
)

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create main app
app = typer.Typer(
    name="kartavya",
    help="🔒 Production-ready CLI for Kartavya SIEM NLP Assistant",
    add_completion=False,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]}
)

console = Console()

# Add command groups
app.add_typer(assistant.app, name="chat", help="💬 Chat with the AI assistant")
app.add_typer(platform_events.app, name="events", help="🔍 Query platform security events")
app.add_typer(reports.app, name="reports", help="📊 Generate and manage reports")
app.add_typer(query.app, name="query", help="🔎 Execute and optimize SIEM queries")
app.add_typer(dashboard.app, name="dashboard", help="📈 Dashboard metrics and alerts")
app.add_typer(admin.app, name="admin", help="⚙️ Administrative commands")
app.add_typer(config_cmd.app, name="config", help="🔧 Configuration management")


@app.command()
def version(
    json_format: bool = typer.Option(False, "--json", help="Output version info as JSON")
):
    """Show version information"""
    version_info = {
        "version": __version__,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform
    }
    
    if json_format:
        print_output(version_info, format_type="json")
    else:
        if get_config().color:
            console.print(f"[bold green]Kartavya CLI[/bold green] [cyan]v{__version__}[/cyan]")
            console.print(f"Python {version_info['python_version']} on {version_info['platform']}")
        else:
            print(f"Kartavya CLI v{__version__}")
            print(f"Python {version_info['python_version']} on {version_info['platform']}")


@app.command()
def health(
    timeout: int = typer.Option(10, "--timeout", "-t", help="Request timeout in seconds"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed health info")
):
    """Check API health and connectivity"""
    
    async def check_health():
        config = get_config()
        config.api_timeout = timeout
        
        async with get_client() as client:
            try:
                # Test basic connectivity
                is_healthy = await client.health_check()
                
                if not is_healthy:
                    print_error("API is not accessible")
                    return False
                
                # Get detailed health if verbose
                if verbose:
                    health_data = await client.get("/health")
                    print_output(health_data, "API Health Status")
                else:
                    print_success("API is healthy and accessible")
                
                return True
                
            except APIError as e:
                print_error(f"Health check failed: {e}")
                return False
    
    try:
        is_healthy = run_async(check_health())
        sys.exit(0 if is_healthy else 1)
    except Exception as e:
        print_error(f"Health check failed: {e}")
        sys.exit(1)


@app.command()
def setup(
    api_url: Optional[str] = typer.Option(None, "--api-url", help="API base URL"),
    api_token: Optional[str] = typer.Option(None, "--token", help="API authentication token"),
    output_format: Optional[str] = typer.Option(None, "--format", help="Default output format (table, json, csv)"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive setup")
):
    """Initial setup and configuration"""
    
    config = get_config()
    
    if interactive:
        console.print(Panel.fit(
            "[bold green]Kartavya CLI Setup[/bold green]\\n"
            "Let's configure your CLI for the Kartavya SIEM NLP Assistant",
            title="🔒 Welcome"
        ))
        
        # API URL
        if not api_url:
            api_url = typer.prompt(
                "API URL", 
                default=config.api_url,
                show_default=True
            )
        
        # API Token
        if not api_token:
            api_token = typer.prompt(
                "API Token (optional, press Enter to skip)", 
                default="",
                hide_input=True,
                show_default=False
            )
            if not api_token:
                api_token = None
        
        # Output format
        if not output_format:
            output_format = typer.prompt(
                "Default output format", 
                default=config.output_format,
                type=typer.Choice(['table', 'json', 'csv'])
            )
    
    # Update configuration
    if api_url:
        config.api_url = api_url.rstrip('/')
    if api_token:
        config.api_token = api_token
    if output_format:
        config.output_format = output_format
    if no_color:
        config.color = False
    
    # Save configuration
    try:
        save_config(config)
        print_success("Configuration saved successfully!")
        
        # Test connection
        if typer.confirm("Test connection to API?", default=True):
            test_connection(config)
            
    except Exception as e:
        print_error(f"Failed to save configuration: {e}")
        sys.exit(1)


def test_connection(config=None):
    """Test API connection"""
    async def test():
        test_config = config or get_config()
        
        async with get_client() as client:
            client.config = test_config
            try:
                health_data = await client.get("/health")
                print_success("✅ Connection successful!")
                if test_config.verbose:
                    print_output(health_data, "Health Status")
                return True
            except APIError as e:
                print_error(f"Connection failed: {e}")
                return False
    
    return run_async(test())


@app.command()
def info():
    """Show system and configuration information"""
    config = get_config()
    config_info = config_manager.get_config_info()
    
    info_data = {
        "version": __version__,
        "configuration": {
            "api_url": config.api_url,
            "has_token": bool(config.api_token),
            "output_format": config.output_format,
            "color_enabled": config.color,
            "timeout": config.api_timeout
        },
        "config_file": {
            "path": config_info["config_file"],
            "exists": config_info["config_file_exists"],
            "env_vars": config_info["env_vars_found"]
        }
    }
    
    print_output(info_data, "System Information")


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)"),
    api_url: Optional[str] = typer.Option(None, "--api-url", help="Override API URL"),
    api_token: Optional[str] = typer.Option(None, "--token", help="Override API token")
):
    """
    🔒 Kartavya CLI - Production-ready command line interface for SIEM operations
    
    A comprehensive CLI tool for interacting with the Kartavya SIEM NLP Assistant.
    
    Examples:
        kartavya setup                          # Initial configuration
        kartavya health                         # Check API connectivity
        kartavya chat ask "failed logins today" # Chat with AI assistant
        kartavya events auth --time-range 1h    # Get authentication events
        kartavya reports generate security_summary # Generate security report
    """
    
    # Configure logging based on verbosity
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
    elif quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Update config with CLI overrides
    config = get_config()
    if api_url:
        config.api_url = api_url.rstrip('/')
    if api_token:
        config.api_token = api_token
    if output_format:
        config.output_format = output_format
    if no_color:
        config.color = False
    if verbose:
        config.verbose = True


if __name__ == "__main__":
    app()

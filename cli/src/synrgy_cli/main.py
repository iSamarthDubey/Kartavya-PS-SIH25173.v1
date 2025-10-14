"""
Main entry point for the Kartavya CLI application.
Sets up the Typer app and registers all command groups.
"""

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from synrgy_cli import __version__
from synrgy_cli.core.config import Config
from synrgy_cli.core.client import APIClient
from synrgy_cli.core.output import OutputFormatter

# Import command modules
from synrgy_cli.commands import (
    assistant,
    platform_events,
    reports,
    query,
    dashboard,
    admin,
    config
)

# Initialize console and app
console = Console()
app = typer.Typer(
    name="kartavya",
    help="Kartavya SIEM NLP Assistant CLI - Intelligent Security Operations",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Add command groups
app.add_typer(config.app, name="config", help="🔧 Configuration management")
app.add_typer(assistant.app, name="chat", help="💬 Interactive AI assistant")
app.add_typer(platform_events.app, name="events", help="🔍 Platform event analysis")
app.add_typer(reports.app, name="reports", help="📊 Report generation")
app.add_typer(query.app, name="query", help="🔧 Query operations")
app.add_typer(dashboard.app, name="dashboard", help="📈 Dashboard metrics")
app.add_typer(admin.app, name="admin", help="👥 Admin operations")


@app.command()
def version():
    """Show version information."""
    console.print(f"[bold blue]Kartavya CLI[/bold blue] version [green]{__version__}[/green]")


@app.command()
def setup(
        base_url: str = typer.Option(
        ..., 
        "--url", 
        help="Base URL for the Kartavya API"
    ),
    api_key: Optional[str] = typer.Option(
        None, 
        "--api-key", 
        help="API key for authentication"
    ),
    username: Optional[str] = typer.Option(
        None, 
        "--username", 
        help="Username for authentication"
    ),
    password: Optional[str] = typer.Option(
        None, 
        "--password", 
        hide_input=True,
        help="Password for authentication"
    ),
):
    """Initial setup and configuration."""
    try:
        config = Config()
        
        # Update configuration
        config.set('api', 'base_url', base_url)
        
        if api_key:
            config.set('auth', 'api_key', api_key)
        elif username and password:
            config.set('auth', 'username', username)
            config.set('auth', 'password', password)
        else:
            console.print("[red]Error: Either --api-key or both --username and --password are required[/red]")
            raise typer.Exit(1)
        
        config.save()
        
        console.print("[green]✓[/green] Configuration saved successfully!")
        console.print(f"[dim]API URL:[/dim] {base_url}")
        
        # Test connection
        with console.status("[bold blue]Testing connection..."):
            client = APIClient()
            health = client.get_health()
            
        if health:
            console.print("[green]✓[/green] Connection test successful!")
        else:
            console.print("[yellow]⚠[/yellow] Connection test failed, but configuration was saved.")
            
    except Exception as e:
        console.print(f"[red]Error during setup: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def health():
    """Check API health and connectivity."""
    try:
        with console.status("[bold blue]Checking API health..."):
            client = APIClient()
            health = client.get_health()
            
        if health:
            console.print(Panel.fit(
                "[green]✓ API is healthy and accessible[/green]",
                title="Health Check",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                "[red]✗ API is not responding[/red]",
                title="Health Check",
                border_style="red"
            ))
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]Health check failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info():
    """Show configuration and system information."""
    try:
        config = Config()
        
        # Basic info
        info_data = [
            ("Version", __version__),
            ("Config File", str(config.config_file)),
            ("API URL", config.get('api', 'base_url', 'Not configured')),
            ("Auth Method", "API Key" if config.get('auth', 'api_key') else "Username/Password"),
        ]
        
        console.print("\n[bold blue]Kartavya CLI Information[/bold blue]\n")
        
        for key, value in info_data:
            console.print(f"[dim]{key}:[/dim] {value}")
        
        # Test API if configured
        if config.get('api', 'base_url'):
            console.print("\n[bold]API Status:[/bold]")
            try:
                client = APIClient()
                health = client.get_health()
                status = "[green]✓ Connected[/green]" if health else "[red]✗ Disconnected[/red]"
                console.print(f"  {status}")
            except Exception as e:
                console.print(f"  [red]✗ Error: {e}[/red]")
                
    except Exception as e:
        console.print(f"[red]Error getting info: {e}[/red]")
        raise typer.Exit(1)


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    config_file: Optional[str] = typer.Option(None, "--config", help="Path to config file"),
):
    """
    Kartavya SIEM NLP Assistant CLI
    
    A comprehensive command-line interface for the Kartavya SIEM platform.
    Provides natural language query processing, threat hunting, and security analysis.
    
    Quick start:
    1. Run 'kartavya config setup' for interactive setup
    2. Test with 'kartavya config test'
    3. Start chatting with 'kartavya chat ask "Show me recent events"'
    
    For help with any command, use: kartavya COMMAND --help
    """
    # Set global config if provided
    if config_file:
        Config._config_file = config_file
    
    # Set verbose mode (could be used in other modules)
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


def cli_main():
    """Entry point for console scripts."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback
            console.print("\n[dim]" + traceback.format_exc() + "[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()

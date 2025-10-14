"""
Configuration management commands for Kartavya CLI.

Provides commands to set up, view, and manage CLI configuration
including backend API endpoints and authentication.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from ..core.config import Config
from ..core.client import APIClient, APIError

console = Console()
app = typer.Typer(name="config", help="🔧 Configuration management")

@app.command("setup")
def setup_config(
    backend_url: Optional[str] = typer.Option(
        None, 
        "--backend-url", 
        "-u", 
        help="Backend API URL (e.g., https://your-render-app.onrender.com)"
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k", 
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
        help="Password for authentication (will be prompted securely if not provided)"
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        "-i/-n",
        help="Run interactive setup"
    )
):
    """🚀 Set up Kartavya CLI configuration"""
    
    config = Config()
    
    rprint("\n[bold blue]🚀 Kartavya CLI Setup[/bold blue]")
    rprint("Let's configure your CLI to connect to your Kartavya backend!")
    
    # Backend URL configuration
    if not backend_url and interactive:
        rprint("\n[yellow]📡 Backend Configuration[/yellow]")
        backend_url = Prompt.ask(
            "Enter your Kartavya backend URL",
            default="https://your-app.onrender.com"
        )
    
    if backend_url:
        # Clean up URL
        backend_url = backend_url.rstrip('/')
        if not backend_url.startswith(('http://', 'https://')):
            backend_url = f"https://{backend_url}"
        
        config.set('api', 'base_url', backend_url)
        rprint(f"✅ Backend URL set to: [green]{backend_url}[/green]")
    
    # Authentication configuration
    if not api_key and not username and interactive:
        rprint("\n[yellow]🔐 Authentication Configuration[/yellow]")
        auth_method = Prompt.ask(
            "Choose authentication method",
            choices=["api-key", "username-password", "none"],
            default="api-key"
        )
        
        if auth_method == "api-key":
            api_key = Prompt.ask("Enter your API key", password=True)
        elif auth_method == "username-password":
            username = Prompt.ask("Enter username")
            password = Prompt.ask("Enter password", password=True)
    
    # Set authentication
    if api_key:
        config.set('auth', 'api_key', api_key)
        rprint("✅ API key configured")
    
    if username:
        config.set('auth', 'username', username)
        if not password and interactive:
            password = Prompt.ask("Enter password", password=True)
        if password:
            config.set('auth', 'password', password)
        rprint("✅ Username/password configured")
    
    # Additional settings
    if interactive:
        rprint("\n[yellow]⚙️ Additional Settings[/yellow]")
        
        output_format = Prompt.ask(
            "Default output format",
            choices=["table", "json", "csv"],
            default="table"
        )
        config.set('output', 'format', output_format)
        
        timeout = Prompt.ask("Request timeout (seconds)", default="30")
        config.set('api', 'timeout', timeout)
        
        verify_ssl = Confirm.ask("Verify SSL certificates?", default=True)
        config.set('api', 'verify_ssl', str(verify_ssl).lower())
    
    # Save configuration
    config.save()
    
    # Test connection
    if backend_url:
        rprint("\n[yellow]🔍 Testing connection...[/yellow]")
        try:
            client = APIClient(config)
            if client.get_health():
                rprint("✅ [green]Connection successful! Your CLI is ready to use.[/green]")
            else:
                rprint("⚠️ [yellow]Backend is reachable but may not be fully ready.[/yellow]")
        except APIError as e:
            rprint(f"❌ [red]Connection failed: {e.message}[/red]")
            if "base URL not configured" not in e.message:
                rprint("[yellow]Your backend might still be starting up. Try again in a few moments.[/yellow]")
        except Exception as e:
            rprint(f"⚠️ [yellow]Connection test failed: {str(e)}[/yellow]")
    
    rprint("\n[bold green]🎉 Setup completed![/bold green]")
    rprint("You can now use: [cyan]kartavya chat ask \"Show me recent security events\"[/cyan]")


@app.command("show")
def show_config():
    """📋 Show current configuration"""
    
    config = Config()
    
    rprint("\n[bold blue]📋 Current Configuration[/bold blue]")
    
    # API Configuration
    api_table = Table(title="🌐 API Configuration", show_header=True, header_style="bold magenta")
    api_table.add_column("Setting", style="cyan", no_wrap=True)
    api_table.add_column("Value", style="green")
    
    api_config = config.get_api_config()
    api_table.add_row("Base URL", api_config.get('base_url') or '[red]Not set[/red]')
    api_table.add_row("Timeout", f"{api_config.get('timeout', 30)}s")
    api_table.add_row("Max Retries", str(api_config.get('max_retries', 3)))
    api_table.add_row("Verify SSL", str(api_config.get('verify_ssl', True)))
    
    console.print(api_table)
    
    # Authentication Configuration
    auth_table = Table(title="🔐 Authentication", show_header=True, header_style="bold magenta")
    auth_table.add_column("Setting", style="cyan", no_wrap=True)
    auth_table.add_column("Status", style="green")
    
    auth_config = config.get_auth_config()
    auth_table.add_row("API Key", "✅ Set" if auth_config.get('api_key') else "❌ Not set")
    auth_table.add_row("Username", auth_config.get('username') or "❌ Not set")
    auth_table.add_row("Password", "✅ Set" if auth_config.get('password') else "❌ Not set")
    
    console.print(auth_table)
    
    # Output Configuration
    output_table = Table(title="🎨 Output Settings", show_header=True, header_style="bold magenta")
    output_table.add_column("Setting", style="cyan", no_wrap=True)
    output_table.add_column("Value", style="green")
    
    output_config = config.get_output_config()
    output_table.add_row("Format", output_config.get('format', 'table'))
    output_table.add_row("Pager", output_config.get('pager', 'auto'))
    output_table.add_row("Color", str(output_config.get('color', True)))
    output_table.add_row("Timestamps", str(output_config.get('timestamps', True)))
    
    console.print(output_table)


@app.command("set")
def set_config(
    section: str = typer.Argument(..., help="Configuration section (api, auth, output)"),
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value")
):
    """⚙️ Set a configuration value"""
    
    config = Config()
    
    # Validate section
    valid_sections = ['api', 'auth', 'output', 'cli']
    if section not in valid_sections:
        rprint(f"[red]❌ Invalid section '{section}'. Valid sections: {', '.join(valid_sections)}[/red]")
        raise typer.Exit(1)
    
    # Set the value
    config.set(section, key, value)
    config.save()
    
    # Mask sensitive values in output
    display_value = value
    if key in ['password', 'api_key'] and value:
        display_value = '*' * min(len(value), 8)
    
    rprint(f"✅ Set [cyan]{section}.{key}[/cyan] = [green]{display_value}[/green]")


@app.command("get")
def get_config(
    section: str = typer.Argument(..., help="Configuration section"),
    key: str = typer.Argument(..., help="Configuration key")
):
    """📖 Get a configuration value"""
    
    config = Config()
    value = config.get(section, key)
    
    if value is None:
        rprint(f"[red]❌ Configuration [cyan]{section}.{key}[/cyan] not found[/red]")
        raise typer.Exit(1)
    
    # Mask sensitive values
    if key in ['password', 'api_key'] and value:
        value = '*' * min(len(value), 8)
    
    rprint(f"[cyan]{section}.{key}[/cyan] = [green]{value}[/green]")


@app.command("test")
def test_connection():
    """🔍 Test connection to backend"""
    
    rprint("\n[yellow]🔍 Testing backend connection...[/yellow]")
    
    try:
        config = Config()
        api_config = config.get_api_config()
        
        if not api_config.get('base_url'):
            rprint("[red]❌ Backend URL not configured. Run 'kartavya config setup' first.[/red]")
            raise typer.Exit(1)
        
        client = APIClient(config)
        
        rprint(f"📡 Connecting to: [cyan]{api_config['base_url']}[/cyan]")
        
        if client.get_health():
            rprint("✅ [green]Connection successful! Backend is healthy.[/green]")
            
            # Try a simple API call
            try:
                metrics = client.get_dashboard_metrics()
                rprint("✅ [green]API endpoints are accessible.[/green]")
            except Exception as e:
                rprint(f"⚠️ [yellow]Backend is healthy but some endpoints may need authentication: {str(e)}[/yellow]")
        else:
            rprint("❌ [red]Backend health check failed.[/red]")
            raise typer.Exit(1)
            
    except APIError as e:
        rprint(f"❌ [red]Connection failed: {e.message}[/red]")
        if e.status_code:
            rprint(f"Status Code: [red]{e.status_code}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"❌ [red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("env")
def show_env_vars():
    """🌍 Show environment variables that can override config"""
    
    rprint("\n[bold blue]🌍 Environment Variables[/bold blue]")
    rprint("These environment variables can override configuration settings:")
    
    env_table = Table(show_header=True, header_style="bold magenta")
    env_table.add_column("Variable", style="cyan", no_wrap=True)
    env_table.add_column("Current Value", style="green")
    env_table.add_column("Description", style="white")
    
    env_vars = [
        ("SYNRGY_API_BASE_URL", "Backend API base URL"),
        ("SYNRGY_AUTH_API_KEY", "API key for authentication"),
        ("SYNRGY_AUTH_USERNAME", "Username for authentication"),
        ("SYNRGY_AUTH_PASSWORD", "Password for authentication"),
        ("SYNRGY_OUTPUT_FORMAT", "Default output format (table/json/csv)"),
        ("SYNRGY_API_TIMEOUT", "Request timeout in seconds"),
        ("SYNRGY_API_VERIFY_SSL", "Verify SSL certificates (true/false)"),
    ]
    
    for var_name, description in env_vars:
        value = os.environ.get(var_name)
        if value and 'password' in var_name.lower() or 'key' in var_name.lower():
            value = '*' * min(len(value), 8)
        env_table.add_row(
            var_name,
            value or "[dim]Not set[/dim]",
            description
        )
    
    console.print(env_table)
    
    rprint("\n[dim]💡 Tip: Set these in your .env file or shell environment[/dim]")


@app.command("reset")
def reset_config():
    """🔄 Reset configuration to defaults"""
    
    if not Confirm.ask("⚠️ This will reset all configuration. Continue?"):
        rprint("Configuration reset cancelled.")
        raise typer.Exit()
    
    config = Config()
    
    # Remove config file
    if config.config_file.exists():
        config.config_file.unlink()
        rprint(f"✅ Removed configuration file: [cyan]{config.config_file}[/cyan]")
    
    # Create new default config
    new_config = Config()
    rprint("✅ Reset to default configuration")
    rprint("Run [cyan]kartavya config setup[/cyan] to reconfigure")


if __name__ == "__main__":
    app()

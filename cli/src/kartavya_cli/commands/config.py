"""
Configuration management commands
Handles CLI configuration, authentication, and settings
"""

from typing import Optional
import typer

from ..core.config import get_config, save_config, config_manager
from ..core.output import print_output, print_error, print_success, print_info

app = typer.Typer(help="🔧 Configuration management")


@app.command("show")
def show_config(
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """Show current configuration"""
    
    config = get_config()
    config_info = config_manager.get_config_info()
    
    config_data = {
        "api_configuration": {
            "api_url": config.api_url,
            "has_token": bool(config.api_token),
            "api_timeout": config.api_timeout
        },
        "output_settings": {
            "output_format": config.output_format,
            "color": config.color,
            "verbose": config.verbose
        },
        "cli_behavior": {
            "auto_confirm": config.auto_confirm,
            "page_size": config.page_size
        },
        "cache_settings": {
            "cache_enabled": config.cache_enabled,
            "cache_ttl": config.cache_ttl
        },
        "file_info": {
            "config_file": config_info["config_file"],
            "config_exists": config_info["config_file_exists"],
            "env_vars_count": config_info["env_vars_found"]
        }
    }
    
    print_output(config_data, "Configuration", output_format)


@app.command("set")
def set_config(
    api_url: Optional[str] = typer.Option(None, "--api-url", help="API base URL"),
    api_token: Optional[str] = typer.Option(None, "--token", help="API authentication token"),
    output_format: Optional[str] = typer.Option(None, "--format", help="Default output format (table, json, csv)"),
    timeout: Optional[int] = typer.Option(None, "--timeout", help="API timeout in seconds"),
    no_color: Optional[bool] = typer.Option(None, "--no-color", help="Disable colored output"),
    verbose: Optional[bool] = typer.Option(None, "--verbose", help="Enable verbose output"),
    auto_confirm: Optional[bool] = typer.Option(None, "--auto-confirm", help="Skip confirmation prompts"),
    page_size: Optional[int] = typer.Option(None, "--page-size", help="Default page size"),
    cache_enabled: Optional[bool] = typer.Option(None, "--cache", help="Enable response caching"),
    cache_ttl: Optional[int] = typer.Option(None, "--cache-ttl", help="Cache TTL in seconds")
):
    """Set configuration values"""
    
    config = get_config()
    changes = []
    
    if api_url is not None:
        config.api_url = api_url.rstrip('/')
        changes.append(f"api_url = {config.api_url}")
    
    if api_token is not None:
        config.api_token = api_token
        changes.append("api_token = [set]" if api_token else "api_token = [cleared]")
    
    if output_format is not None:
        if output_format not in ['table', 'json', 'csv']:
            print_error("Invalid format. Must be 'table', 'json', or 'csv'")
            return
        config.output_format = output_format
        changes.append(f"output_format = {output_format}")
    
    if timeout is not None:
        config.api_timeout = timeout
        changes.append(f"api_timeout = {timeout}")
    
    if no_color is not None:
        config.color = not no_color
        changes.append(f"color = {config.color}")
    
    if verbose is not None:
        config.verbose = verbose
        changes.append(f"verbose = {verbose}")
    
    if auto_confirm is not None:
        config.auto_confirm = auto_confirm
        changes.append(f"auto_confirm = {auto_confirm}")
    
    if page_size is not None:
        config.page_size = page_size
        changes.append(f"page_size = {page_size}")
    
    if cache_enabled is not None:
        config.cache_enabled = cache_enabled
        changes.append(f"cache_enabled = {cache_enabled}")
    
    if cache_ttl is not None:
        config.cache_ttl = cache_ttl
        changes.append(f"cache_ttl = {cache_ttl}")
    
    if not changes:
        print_info("No configuration changes specified")
        return
    
    try:
        save_config(config)
        print_success("Configuration updated:")
        for change in changes:
            print_info(f"  • {change}")
    except Exception as e:
        print_error(f"Failed to save configuration: {e}")


@app.command("reset")
def reset_config(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Reset configuration to defaults"""
    
    if not confirm:
        if not typer.confirm("Reset all configuration to defaults? This will clear your API token."):
            print("Operation cancelled.")
            return
    
    # Create default configuration
    from ..core.config import KartavyaConfig
    default_config = KartavyaConfig()
    
    try:
        save_config(default_config)
        print_success("Configuration reset to defaults")
        print_info("Run 'kartavya setup' to configure API settings")
    except Exception as e:
        print_error(f"Failed to reset configuration: {e}")


@app.command("edit")
def edit_config():
    """Open configuration file in default editor"""
    
    import subprocess
    import os
    
    config_info = config_manager.get_config_info()
    config_file = config_info["config_file"]
    
    if not os.path.exists(config_file):
        print_info("Configuration file doesn't exist. Creating default configuration...")
        save_config(get_config())
    
    try:
        # Try to open with default system editor
        if os.name == 'nt':  # Windows
            os.startfile(config_file)
        elif os.name == 'posix':  # Unix/Linux/Mac
            editor = os.environ.get('EDITOR', 'nano')
            subprocess.call([editor, config_file])
        
        print_info(f"Opened configuration file: {config_file}")
    except Exception as e:
        print_error(f"Failed to open configuration file: {e}")
        print_info(f"You can manually edit: {config_file}")


@app.command("validate")
def validate_config():
    """Validate current configuration"""
    
    try:
        config = get_config()
        issues = []
        warnings = []
        
        # Validate API URL
        if not config.api_url:
            issues.append("API URL is not set")
        elif not config.api_url.startswith(('http://', 'https://')):
            issues.append("API URL must start with http:// or https://")
        
        # Check API token
        if not config.api_token:
            warnings.append("API token is not set - authentication may fail")
        
        # Validate timeout
        if config.api_timeout <= 0:
            issues.append("API timeout must be positive")
        
        # Validate output format
        if config.output_format not in ['table', 'json', 'csv']:
            issues.append(f"Invalid output format: {config.output_format}")
        
        # Validate page size
        if config.page_size <= 0:
            issues.append("Page size must be positive")
        
        # Validate cache TTL
        if config.cache_ttl <= 0:
            issues.append("Cache TTL must be positive")
        
        # Report results
        if issues:
            print_error("Configuration validation failed:")
            for issue in issues:
                print_error(f"  • {issue}")
        else:
            print_success("✅ Configuration is valid")
        
        if warnings:
            print_info("Warnings:")
            for warning in warnings:
                print_info(f"  • {warning}")
        
        return len(issues) == 0
        
    except Exception as e:
        print_error(f"Configuration validation failed: {e}")
        return False


@app.command("path")
def config_path():
    """Show configuration file path"""
    
    config_info = config_manager.get_config_info()
    print(config_info["config_file"])


@app.command("env")
def show_env_vars():
    """Show configuration environment variables"""
    
    import os
    
    env_vars = {
        "KARTAVYA_API_URL": os.getenv("KARTAVYA_API_URL"),
        "KARTAVYA_API_TOKEN": "[set]" if os.getenv("KARTAVYA_API_TOKEN") else None,
        "KARTAVYA_OUTPUT_FORMAT": os.getenv("KARTAVYA_OUTPUT_FORMAT"),
        "KARTAVYA_COLOR": os.getenv("KARTAVYA_COLOR"),
        "KARTAVYA_VERBOSE": os.getenv("KARTAVYA_VERBOSE"),
        "KARTAVYA_API_TIMEOUT": os.getenv("KARTAVYA_API_TIMEOUT"),
        "KARTAVYA_AUTO_CONFIRM": os.getenv("KARTAVYA_AUTO_CONFIRM"),
        "KARTAVYA_PAGE_SIZE": os.getenv("KARTAVYA_PAGE_SIZE"),
        "KARTAVYA_CACHE_ENABLED": os.getenv("KARTAVYA_CACHE_ENABLED"),
        "KARTAVYA_CACHE_TTL": os.getenv("KARTAVYA_CACHE_TTL")
    }
    
    # Filter out None values
    set_env_vars = {k: v for k, v in env_vars.items() if v is not None}
    
    if set_env_vars:
        print_output(set_env_vars, "Environment Variables")
    else:
        print_info("No Kartavya environment variables are set")
        print_info("Available environment variables:")
        for var in env_vars.keys():
            print_info(f"  • {var}")


@app.command("backup")
def backup_config(
    output_file: Optional[str] = typer.Option(None, "--file", "-f", help="Output file for backup")
):
    """Backup current configuration"""
    
    import json
    import datetime
    
    config = get_config()
    config_data = config.model_dump()
    
    # Add metadata
    backup_data = {
        "backup_created": datetime.datetime.now().isoformat(),
        "cli_version": "1.0.0",
        "configuration": config_data
    }
    
    if not output_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"kartavya_config_backup_{timestamp}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2)
        
        print_success(f"Configuration backed up to: {output_file}")
    except Exception as e:
        print_error(f"Failed to backup configuration: {e}")


@app.command("restore")
def restore_config(
    backup_file: str = typer.Argument(..., help="Backup file to restore from"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Restore configuration from backup"""
    
    import json
    import os
    
    if not os.path.exists(backup_file):
        print_error(f"Backup file not found: {backup_file}")
        return
    
    if not confirm:
        if not typer.confirm(f"Restore configuration from {backup_file}? This will overwrite current settings."):
            print("Operation cancelled.")
            return
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        config_data = backup_data.get("configuration", backup_data)
        
        # Create config object from backup data
        from ..core.config import KartavyaConfig
        restored_config = KartavyaConfig(**config_data)
        
        save_config(restored_config)
        print_success(f"Configuration restored from: {backup_file}")
        
        if "backup_created" in backup_data:
            print_info(f"Backup was created: {backup_data['backup_created']}")
        
    except Exception as e:
        print_error(f"Failed to restore configuration: {e}")

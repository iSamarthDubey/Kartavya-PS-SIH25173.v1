"""
Configuration management for Kartavya CLI.

Handles loading, saving, and accessing configuration values from
both file-based config and environment variables.
"""

import os
import configparser
from pathlib import Path
from typing import Any, Optional, Dict
from dotenv import load_dotenv

class Config:
    """Configuration manager for Kartavya CLI."""
    
    _config_file: Optional[Path] = None
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager."""
        if config_file:
            self.config_file = Path(config_file)
        elif self._config_file:
            self.config_file = self._config_file
        else:
            # Default config file location
            self.config_file = self._get_default_config_path()
        
        self.config = configparser.ConfigParser()
        self._load_dotenv()
        self.load()
    
    def _get_default_config_path(self) -> Path:
        """Get the default configuration file path."""
        # Try to use XDG config directory on Unix-like systems
        if os.name != 'nt':
            config_home = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            config_dir = Path(config_home) / 'kartavya-cli'
        else:
            # Use AppData on Windows
            config_dir = Path.home() / '.kartavya-cli'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'config.ini'
    
    def _load_dotenv(self):
        """Load environment variables from .env file."""
        # Look for .env in current directory and parent directories
        current_dir = Path.cwd()
        for parent in [current_dir] + list(current_dir.parents):
            env_file = parent / '.env'
            if env_file.exists():
                load_dotenv(env_file)
                break
    
    def load(self):
        """Load configuration from file."""
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            # Create default configuration
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration sections."""
        self.config.add_section('api')
        self.config.add_section('auth')
        self.config.add_section('output')
        self.config.add_section('cli')
        
        # Set default values
        self.config.set('output', 'format', 'table')
        self.config.set('output', 'pager', 'auto')
        self.config.set('cli', 'timeout', '30')
        self.config.set('cli', 'max_retries', '3')
    
    def save(self):
        """Save configuration to file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value with environment variable override."""
        # Check environment variable first (uppercase with underscore)
        env_key = f"KARTAVYA_{section.upper()}_{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value
        
        # Check config file
        if self.config.has_section(section) and self.config.has_option(section, key):
            return self.config.get(section, key)
        
        return default
    
    def getint(self, section: str, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        value = self.get(section, key, default)
        if isinstance(value, str):
            return int(value)
        return value
    
    def getbool(self, section: str, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = self.get(section, key, default)
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, key, str(value))
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API-related configuration."""
        return {
            'base_url': self.get('api', 'base_url'),
            'timeout': self.getint('api', 'timeout', 30),
            'max_retries': self.getint('api', 'max_retries', 3),
            'verify_ssl': self.getbool('api', 'verify_ssl', True),
        }
    
    def get_auth_config(self) -> Dict[str, Any]:
        """Get authentication configuration."""
        return {
            'api_key': self.get('auth', 'api_key'),
            'username': self.get('auth', 'username'),
            'password': self.get('auth', 'password'),
            'token_file': self.get('auth', 'token_file'),
        }
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output formatting configuration."""
        return {
            'format': self.get('output', 'format', 'table'),
            'pager': self.get('output', 'pager', 'auto'),
            'color': self.getbool('output', 'color', True),
            'timestamps': self.getbool('output', 'timestamps', True),
        }

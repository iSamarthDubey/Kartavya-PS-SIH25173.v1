"""
Configuration management for Kartavya CLI
Handles config files, environment variables, and API settings
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import toml
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class KartavyaConfig(BaseModel):
    """Configuration model for Kartavya CLI"""
    
    # API Configuration
    api_url: str = Field(default="http://localhost:8000", description="Base URL for Kartavya API")
    api_token: Optional[str] = Field(default=None, description="API authentication token")
    api_timeout: int = Field(default=30, description="API request timeout in seconds")
    
    # Output Configuration
    output_format: str = Field(default="table", description="Default output format: table, json, csv")
    color: bool = Field(default=True, description="Enable colored output")
    verbose: bool = Field(default=False, description="Enable verbose output")
    
    # CLI Behavior
    auto_confirm: bool = Field(default=False, description="Skip confirmation prompts")
    page_size: int = Field(default=50, description="Default page size for paginated results")
    
    # Cache Configuration
    cache_enabled: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    
    class Config:
        env_prefix = "KARTAVYA_"


class ConfigManager:
    """Manages CLI configuration with file-based and environment variable support"""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.toml"
        self._ensure_config_dir()
        
    def _get_config_dir(self) -> Path:
        """Get the configuration directory path"""
        if sys.platform.startswith('win'):
            # Windows
            config_dir = Path(os.environ.get('APPDATA', Path.home() / 'AppData/Roaming')) / 'kartavya-cli'
        elif sys.platform.startswith('darwin'):
            # macOS
            config_dir = Path.home() / 'Library' / 'Application Support' / 'kartavya-cli'
        else:
            # Linux/Unix
            config_dir = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'kartavya-cli'
        
        return config_dir
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> KartavyaConfig:
        """Load configuration from file and environment variables"""
        config_data = {}
        
        # Load from config file if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = toml.load(f)
                config_data.update(file_config)
                logger.debug(f"Loaded config from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # Override with environment variables
        env_vars = self._load_env_vars()
        config_data.update(env_vars)
        
        return KartavyaConfig(**config_data)
    
    def save_config(self, config: KartavyaConfig):
        """Save configuration to file"""
        try:
            config_data = config.model_dump()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                toml.dump(config_data, f)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise
    
    def _load_env_vars(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        env_config = {}
        prefix = "KARTAVYA_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                
                # Convert string values to appropriate types
                if config_key in ['color', 'verbose', 'auto_confirm', 'cache_enabled']:
                    env_config[config_key] = value.lower() in ('true', '1', 'yes', 'on')
                elif config_key in ['api_timeout', 'page_size', 'cache_ttl']:
                    try:
                        env_config[config_key] = int(value)
                    except ValueError:
                        logger.warning(f"Invalid integer value for {key}: {value}")
                else:
                    env_config[config_key] = value
        
        return env_config
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about configuration sources"""
        return {
            "config_dir": str(self.config_dir),
            "config_file": str(self.config_file),
            "config_file_exists": self.config_file.exists(),
            "env_vars_found": len(self._load_env_vars())
        }


# Global config manager instance
config_manager = ConfigManager()


def get_config() -> KartavyaConfig:
    """Get the current configuration"""
    return config_manager.load_config()


def save_config(config: KartavyaConfig):
    """Save configuration to file"""
    config_manager.save_config(config)

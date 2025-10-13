"""
🔧 Environment Configuration Manager
Handles demo vs production modes and toggleable AI
"""

import os
from typing import Optional, Dict, Any, List
from enum import Enum
import logging
from pydantic_settings import BaseSettings
from pydantic import Field

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Deployment environments"""
    DEMO = "demo"
    PRODUCTION = "production" 
    DEVELOPMENT = "development"


class DataSourceMode(str, Enum):
    """Data source operation modes"""
    SINGLE = "single"      # Use single best data source
    MULTI = "multi"        # Use ALL available real data sources (recommended)
    AUTO = "auto"          # Same as MULTI - auto-detect and use all available


class SiemPlatform(str, Enum):
    """Supported data source platforms"""
    AUTO = "auto"
    ELASTICSEARCH = "elasticsearch"
    WAZUH = "wazuh"
    SPLUNK = "splunk"
    DATASET = "dataset"
    MOCK = "mock"


class Settings(BaseSettings):
    """Application settings with environment-based configuration"""
    
    # =============================================================================
    # 🚀 DEPLOYMENT MODE
    # =============================================================================
    environment: Environment = Field(default=Environment.DEMO, env="ENVIRONMENT")
    
    # =============================================================================
    # 🤖 AI CONFIGURATION (TOGGLEABLE)
    # =============================================================================
    enable_ai: bool = Field(default=True, env="ENABLE_AI")
    
    # Google Gemini API (Primary)
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-pro", env="GEMINI_MODEL")
    
    # OpenAI API (Backup)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    
    # =============================================================================
    # 🗄️ DATABASE CONFIGURATION
    # =============================================================================
    
    # Supabase (PostgreSQL + Auth)
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_anon_key: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    supabase_service_key: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_KEY")
    
    # MongoDB Atlas (SIEM Logs)
    mongodb_uri: Optional[str] = Field(default=None, env="MONGODB_URI")
    mongodb_database: str = Field(default="kartavya_siem", env="MONGODB_DATABASE")
    
    # Redis Cloud (Cache + Context)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # =============================================================================
    # 🔧 BACKEND CONFIGURATION
    # =============================================================================
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=4, env="API_WORKERS")
    
    # CORS Origins
    cors_origins: str = Field(
        default="http://localhost:3000",
        env="CORS_ORIGINS"
    )
    
    # JWT Secret
    jwt_secret: str = Field(
        default="your-super-secret-jwt-key-change-in-production",
        env="JWT_SECRET"
    )
    
    # =============================================================================
    # 📊 MONITORING & LOGGING
    # =============================================================================
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # =============================================================================
    # 🔐 SECURITY SETTINGS
    # =============================================================================
    rate_limit_requests: int = Field(default=60, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    session_timeout: int = Field(default=3600, env="SESSION_TIMEOUT")
    max_context_messages: int = Field(default=50, env="MAX_CONTEXT_MESSAGES")
    
    # =============================================================================
    # 🎯 DATA SOURCE CONFIGURATION
    # =============================================================================
    
    # Data source operation mode
    data_source_mode: DataSourceMode = Field(
        default=DataSourceMode.AUTO,
        env="DATA_SOURCE_MODE"
    )
    
    # Primary data source selection
    default_data_source: SiemPlatform = Field(
        default=SiemPlatform.AUTO,
        env="DEFAULT_DATA_SOURCE"
    )
    
    # Multi-source configuration
    enable_multi_source: bool = Field(
        default=True,
        env="ENABLE_MULTI_SOURCE"
    )
    
    # Correlation fields for deduplication across sources
    correlation_fields: str = Field(
        default="source.ip,destination.ip,user.name,@timestamp",
        env="CORRELATION_FIELDS"
    )
    
    # Maximum sources to use simultaneously  
    max_concurrent_sources: int = Field(
        default=3,
        env="MAX_CONCURRENT_SOURCES"
    )
    
    # Multi-source query timeout
    multi_source_timeout: float = Field(
        default=30.0,
        env="MULTI_SOURCE_TIMEOUT"
    )
    
    # Legacy support for existing env vars
    default_siem_platform: Optional[SiemPlatform] = Field(
        default=None,
        env="DEFAULT_SIEM_PLATFORM"
    )
    
    # Elasticsearch
    elasticsearch_url: str = Field(default="http://localhost:9200", env="ELASTICSEARCH_URL")
    elasticsearch_username: str = Field(default="elastic", env="ELASTICSEARCH_USERNAME")
    elasticsearch_password: Optional[str] = Field(default=None, env="ELASTICSEARCH_PASSWORD")
    
    # Wazuh
    wazuh_api_url: Optional[str] = Field(default=None, env="WAZUH_API_URL")
    wazuh_username: str = Field(default="wazuh", env="WAZUH_USERNAME")
    wazuh_password: Optional[str] = Field(default=None, env="WAZUH_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow extra fields for backwards compatibility

    @property
    def is_demo(self) -> bool:
        """Check if running in demo mode"""
        return self.environment == Environment.DEMO
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == Environment.PRODUCTION
    
    @property
    def ai_enabled(self) -> bool:
        """Check if AI features are enabled"""
        # In production mode, AI can be disabled for security
        if self.is_production:
            return self.enable_ai and (self.gemini_api_key or self.openai_api_key)
        return self.enable_ai and (self.gemini_api_key or self.openai_api_key)
    
    def get_effective_data_source(self) -> SiemPlatform:
        """Get the effective data source, considering legacy env vars"""
        # Support legacy DEFAULT_SIEM_PLATFORM for backward compatibility
        if self.default_siem_platform:
            return self.default_siem_platform
        return self.default_data_source
    
    def get_effective_mode(self) -> DataSourceMode:
        """Get the effective data source mode"""
        # If multi-source is disabled, force single mode
        if not self.enable_multi_source:
            return DataSourceMode.SINGLE
        return self.data_source_mode
    
    def get_correlation_fields_list(self) -> List[str]:
        """Get correlation fields as a list"""
        return [field.strip() for field in self.correlation_fields.split(",") if field.strip()]
    
    def should_use_multi_source(self) -> bool:
        """Determine if multi-source mode should be used"""
        mode = self.get_effective_mode()
        
        # In production, prefer multi-source for real data sources
        # In demo, single source (dataset) is fine
        if mode == DataSourceMode.SINGLE:
            return False
        else:  # MULTI or AUTO mode
            return self.enable_multi_source and self.is_production
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration - all databases always available"""
        # Always provide all database configurations
        # The actual connection will depend on which environment variables are set
        config = {
            "supabase": {
                "url": self.supabase_url,
                "anon_key": self.supabase_anon_key,
                "service_key": self.supabase_service_key,
            },
            "mongodb": {
                "uri": self.mongodb_uri,
                "database": self.mongodb_database,
            },
            "redis": {
                "url": self.redis_url,
                "password": self.redis_password,
            },
            # Local fallback configurations
            "postgresql_local": {
                "url": "postgresql://localhost:5432/kartavya",
            },
            "redis_local": {
                "url": "redis://localhost:6379",
            }
        }
        
        return config
    
    def validate_configuration(self) -> bool:
        """Validate configuration - now focuses only on critical requirements"""
        warnings = []
        
        # Check if at least one database option is available
        has_supabase = bool(self.supabase_url and self.supabase_anon_key)
        has_mongodb = bool(self.mongodb_uri)
        has_redis = bool(self.redis_url)
        
        if not (has_supabase or has_mongodb or has_redis):
            warnings.append("No cloud databases configured - will use local fallbacks")
        
        if self.ai_enabled:
            if not self.gemini_api_key and not self.openai_api_key:
                warnings.append("No AI API keys configured - AI features will be disabled")
        
        # Log warnings but don't fail startup
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")
        
        return True  # Always return True - let the app run with fallbacks


# Global settings instance
settings = Settings()

# Import secure logging after settings are initialized
try:
    from .security_filter import setup_secure_logging
    # Setup secure logging with credential redaction
    setup_secure_logging(settings.log_level)
except ImportError:
    # Fallback to basic logging if security filter is not available
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger.warning("⚠️ Secure logging filter not available, using basic logging")

# Validate configuration on startup
if not settings.validate_configuration():
    logger.error("❌ Configuration validation failed!")
else:
    logger.info(f"✅ Configuration loaded for {settings.environment.upper()} mode")
    logger.info(f"🤖 AI enabled: {settings.gemini_api_key is not None or settings.openai_api_key is not None}")
    logger.info(f"🎯 Default data source: {settings.get_effective_data_source()}")


def get_ai_config() -> Dict[str, Any]:
    """Get AI configuration"""
    if not settings.ai_enabled:
        return {"enabled": False}
    
    return {
        "enabled": True,
        "gemini": {
            "api_key": settings.gemini_api_key,
            "model": settings.gemini_model,
            "available": bool(settings.gemini_api_key)
        },
        "openai": {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
            "available": bool(settings.openai_api_key)
        }
    }


def get_deployment_info() -> Dict[str, Any]:
    """Get deployment information"""
    return {
        "environment": settings.environment,
        "ai_enabled": settings.ai_enabled,
        "data_source": settings.get_effective_data_source(),
        "version": "1.0.0",
        "demo_mode": settings.is_demo,
        "production_mode": settings.is_production,
        "auto_detection": settings.get_effective_data_source() == SiemPlatform.AUTO
    }

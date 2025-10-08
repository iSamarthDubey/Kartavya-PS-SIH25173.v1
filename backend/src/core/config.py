"""
🔧 Environment Configuration Manager
Handles demo vs production modes and toggleable AI
"""

import os
from typing import Optional, Dict, Any
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


class SiemPlatform(str, Enum):
    """Supported SIEM platforms"""
    ELASTICSEARCH = "elasticsearch"
    WAZUH = "wazuh"
    DATASET = "dataset"


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
    # 🎯 SIEM CONFIGURATION
    # =============================================================================
    default_siem_platform: SiemPlatform = Field(
        default=SiemPlatform.DATASET,
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

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Validate configuration on startup
if not settings.validate_configuration():
    logger.error("❌ Configuration validation failed!")
else:
    logger.info(f"✅ Configuration loaded for {settings.environment.upper()} mode")
    logger.info(f"🤖 AI enabled: {settings.ai_enabled}")
    logger.info(f"🎯 Default SIEM: {settings.default_siem_platform}")


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
        "siem_platform": settings.default_siem_platform,
        "version": "1.0.0",
        "demo_mode": settings.is_demo,
        "production_mode": settings.is_production
    }

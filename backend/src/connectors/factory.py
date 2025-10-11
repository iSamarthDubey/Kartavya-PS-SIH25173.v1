"""
SIEM Connector Factory
Creates appropriate SIEM connector based on platform and environment
"""

import logging
import os
from typing import Optional
from .base import BaseSIEMConnector
from .elastic import ElasticConnector
from .wazuh import WazuhConnector
from .dataset_connector import DatasetConnector

logger = logging.getLogger(__name__)

def create_connector(
    platform: str = "elasticsearch",
    environment: str = "demo",
    **kwargs
) -> BaseSIEMConnector:
    """
    Factory function to create appropriate SIEM connector
    
    Args:
        platform: SIEM platform ('elasticsearch', 'wazuh', 'dataset')
        environment: 'demo' (uses datasets) or 'production' (real SIEM)
        **kwargs: Additional arguments for connector
        
    Returns:
        SIEM connector instance
    """
    # Get environment from env var if not provided
    if not environment:
        environment = os.getenv("ENVIRONMENT", "demo")
    
    platform_lower = platform.lower()
    
    # For demo mode with elasticsearch platform, use real Elasticsearch
    if environment == "demo" and platform_lower == "elasticsearch":
        logger.info("🎭 Demo mode with Elasticsearch: Using live Elasticsearch connector")
        try:
            connector = ElasticConnector(**kwargs)
            if connector.is_available():
                logger.info("✅ Elasticsearch connection successful in demo mode")
                return connector
            else:
                logger.warning("⚠️ Elasticsearch not available, falling back to dataset")
        except Exception as e:
            logger.warning(f"⚠️ Elasticsearch connection failed: {e}, using dataset fallback")
    
    # For demo mode with other platforms, use dataset connector
    if environment == "demo":
        logger.info("🎭 Demo mode: Using dataset connector with real SIEM datasets")
        return DatasetConnector(
            name=f"dataset_{platform_lower}",
            **kwargs
        )
    
    # Production mode: Use real SIEM connectors
    connectors = {
        "elasticsearch": ElasticConnector,
        "elastic": ElasticConnector,
        "wazuh": WazuhConnector,
        "dataset": DatasetConnector  # Fallback option
    }
    
    if platform_lower not in connectors:
        logger.warning(f"Unknown platform '{platform}', using dataset connector")
        return DatasetConnector(**kwargs)
    
    try:
        connector_class = connectors[platform_lower]
        connector = connector_class(**kwargs)
        
        logger.info(f"✅ Successfully created {platform} connector for {environment} mode")
        return connector
        
    except Exception as e:
        logger.error(f"❌ Failed to create {platform} connector: {e}")
        logger.info("📊 Falling back to dataset connector")
        return DatasetConnector(**kwargs)

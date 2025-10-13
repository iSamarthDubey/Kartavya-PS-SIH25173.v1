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
    platform: str = "auto",
    environment: str = "demo",
    **kwargs
) -> BaseSIEMConnector:
    """
    Factory function to create appropriate data source connector
    
    Args:
        platform: Data source platform ('auto', 'elasticsearch', 'wazuh', 'splunk', 'dataset')
        environment: 'demo' (uses datasets) or 'production' (real sources)
        **kwargs: Additional arguments for connector
        
    Returns:
        Data source connector instance
    """
    # Get environment from env var if not provided
    if not environment:
        environment = os.getenv("ENVIRONMENT", "demo")
    
    platform_lower = platform.lower()
    
    # AUTO detection logic
    if platform_lower == "auto":
        logger.info("🔍 AUTO mode: Detecting available data sources...")
        return _auto_detect_connector(environment, **kwargs)
    
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


def _auto_detect_connector(environment: str = "demo", **kwargs) -> BaseSIEMConnector:
    """
    Auto-detect available data sources in order of preference
    
    Detection order:
    1. Elasticsearch (if configured and available)
    2. Splunk (if configured and available) 
    3. Wazuh (if configured and available)
    4. Dataset (fallback)
    """
    logger.info("🔍 Starting auto-detection of available data sources...")
    
    # Detection order by preference
    detection_order = [
        ("elasticsearch", ElasticConnector, "Elasticsearch"),
        ("wazuh", WazuhConnector, "Wazuh"),
    ]
    
    for platform_name, connector_class, display_name in detection_order:
        try:
            logger.info(f"🔍 Testing {display_name} availability...")
            
            # Try to create and test the connector
            connector = connector_class(**kwargs)
            
            # Check if connector has availability check
            if hasattr(connector, 'is_available'):
                if connector.is_available():
                    logger.info(f"✅ AUTO detected: Using {display_name}")
                    return connector
                else:
                    logger.info(f"⏭️ {display_name} not available, trying next...")
                    continue
            
            # If no availability check, try basic connection test
            try:
                # For demo environment, be more lenient
                if environment == "demo":
                    logger.info(f"✅ AUTO detected (demo mode): Using {display_name}")
                    return connector
                    
                # For production, we'd need actual connection tests here
                logger.info(f"✅ AUTO detected: Using {display_name}")
                return connector
                
            except Exception as test_e:
                logger.info(f"⏭️ {display_name} connection test failed: {test_e}")
                continue
                
        except Exception as e:
            logger.info(f"⏭️ {display_name} creation failed: {e}")
            continue
    
    # If no live sources detected, fall back to dataset
    logger.info("📊 AUTO fallback: No live data sources detected, using dataset connector")
    return DatasetConnector(
        name="auto_dataset",
        **kwargs
    )


def get_available_platforms(environment: str = "demo") -> list[str]:
    """
    Get list of currently available platforms
    """
    available = []
    
    # PRODUCTION: NO dataset, only real sources
    if environment != "production":
        available.append("dataset")  # Only available in demo/dev
    
    # Test real platforms
    platforms_to_test = [
        ("elasticsearch", ElasticConnector),
        ("wazuh", WazuhConnector),
    ]
    
    for platform_name, connector_class in platforms_to_test:
        try:
            connector = connector_class()
            if hasattr(connector, 'is_available') and connector.is_available():
                available.append(platform_name)
        except Exception:
            continue
    
    return available

"""
SIEM Connector Factory
Creates appropriate SIEM connector based on platform
"""

import logging
from typing import Optional, Union
from .base import BaseSIEMConnector
from .elastic import ElasticConnector
from .wazuh import WazuhConnector
from .mock import MockConnector

logger = logging.getLogger(__name__)

def create_connector(
    platform: str = "elasticsearch",
    use_mock: bool = False,
    **kwargs
) -> BaseSIEMConnector:
    """
    Factory function to create appropriate SIEM connector
    
    Args:
        platform: SIEM platform ('elasticsearch', 'wazuh', 'mock')
        use_mock: Force use of mock connector for testing
        **kwargs: Additional arguments for connector
        
    Returns:
        SIEM connector instance
    """
    if use_mock or platform == "mock":
        logger.info("Using mock SIEM connector")
        return MockConnector(**kwargs)
    
    platform_lower = platform.lower()
    
    connectors = {
        "elasticsearch": ElasticConnector,
        "elastic": ElasticConnector,
        "wazuh": WazuhConnector,
    }
    
    if platform_lower not in connectors:
        logger.warning(f"Unknown platform '{platform}', using mock connector")
        return MockConnector(**kwargs)
    
    try:
        connector_class = connectors[platform_lower]
        connector = connector_class(**kwargs)
        
        # Test connection
        if hasattr(connector, 'test_connection'):
            if not connector.test_connection():
                logger.warning(f"{platform} connection failed, falling back to mock")
                return MockConnector(**kwargs)
        
        logger.info(f"Successfully created {platform} connector")
        return connector
        
    except Exception as e:
        logger.error(f"Failed to create {platform} connector: {e}")
        logger.info("Falling back to mock connector")
        return MockConnector(**kwargs)

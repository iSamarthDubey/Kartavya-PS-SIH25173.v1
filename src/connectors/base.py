"""
Base SIEM Connector
Abstract base class for all SIEM connectors
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseSIEMConnector(ABC):
    """Abstract base class for SIEM connectors"""
    
    def __init__(self, **kwargs):
        """Initialize connector with configuration"""
        self.config = kwargs
        self.connected = False
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to SIEM"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to SIEM"""
        pass
    
    @abstractmethod
    async def execute_query(
        self,
        query: Dict[str, Any],
        size: int = 100,
        index: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a query against the SIEM
        
        Args:
            query: Query in appropriate format (DSL/KQL)
            size: Maximum number of results
            index: Target index/dataset
            
        Returns:
            Query results dictionary
        """
        pass
    
    @abstractmethod
    async def get_field_mappings(
        self,
        index: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get field mappings from SIEM
        
        Args:
            index: Target index
            
        Returns:
            Field mappings dictionary
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if connection is working
        
        Returns:
            True if connection is successful
        """
        pass
    
    async def search(
        self,
        query_string: str,
        size: int = 100,
        index: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simple text search
        
        Args:
            query_string: Search string
            size: Max results
            index: Target index
            
        Returns:
            Search results
        """
        query = self._build_text_query(query_string)
        return await self.execute_query(query, size, index)
    
    def _build_text_query(self, query_string: str) -> Dict[str, Any]:
        """
        Build a text search query
        
        Args:
            query_string: Search string
            
        Returns:
            Query dictionary
        """
        return {
            "query": {
                "query_string": {
                    "query": query_string,
                    "default_operator": "AND"
                }
            }
        }
    
    async def get_indices(self) -> List[str]:
        """
        Get list of available indices
        
        Returns:
            List of index names
        """
        return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get SIEM statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            "connected": self.connected,
            "platform": self.__class__.__name__
        }

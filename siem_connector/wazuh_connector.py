"""
Wazuh SIEM Connector
Handles connections and queries to Wazuh SIEM platforms.
"""

import os
import requests
from typing import Dict, List, Any, Optional
import logging
import base64

logger = logging.getLogger(__name__)


class WazuhConnector:
    """Connector for Wazuh SIEM platforms."""
    
    def __init__(self):
        """Initialize Wazuh connection."""
        self.host = os.getenv('WAZUH_HOST', 'localhost')
        self.port = int(os.getenv('WAZUH_PORT', 55000))
        self.username = os.getenv('WAZUH_USERNAME')
        self.password = os.getenv('WAZUH_PASSWORD')
        self.base_url = f"https://{self.host}:{self.port}"
        
        self.session = requests.Session()
        self.token = self._authenticate()
    
    def _authenticate(self) -> str:
        """Authenticate with Wazuh API."""
        try:
            credentials = base64.b64encode(
                f"{self.username}:{self.password}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                f"{self.base_url}/security/user/authenticate",
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                token = response.json()['data']['token']
                self.session.headers.update({'Authorization': f'Bearer {token}'})
                logger.info("Successfully authenticated with Wazuh")
                return token
            else:
                raise Exception(f"Authentication failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Wazuh authentication failed: {e}")
            raise
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get list of Wazuh agents."""
        try:
            response = self.session.get(
                f"{self.base_url}/agents",
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()['data']['affected_items']
            else:
                raise Exception(f"Failed to get agents: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            return []
    
    def get_alerts(self, **filters) -> List[Dict[str, Any]]:
        """Get alerts with optional filters."""
        try:
            params = {}
            if 'limit' in filters:
                params['limit'] = filters['limit']
            if 'agent_id' in filters:
                params['agent_id'] = filters['agent_id']
            if 'rule_id' in filters:
                params['rule_id'] = filters['rule_id']
            
            response = self.session.get(
                f"{self.base_url}/security/alerts",
                params=params,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()['data']['affected_items']
            else:
                raise Exception(f"Failed to get alerts: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def get_rules(self, **filters) -> List[Dict[str, Any]]:
        """Get Wazuh rules."""
        try:
            params = {}
            if 'limit' in filters:
                params['limit'] = filters['limit']
            
            response = self.session.get(
                f"{self.base_url}/rules",
                params=params,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()['data']['affected_items']
            else:
                raise Exception(f"Failed to get rules: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to get rules: {e}")
            return []
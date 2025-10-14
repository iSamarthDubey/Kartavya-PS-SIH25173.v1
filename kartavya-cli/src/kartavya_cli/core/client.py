"""
HTTP API client for Kartavya backend communication.

Handles authentication, request/response processing, error handling,
and provides methods for all backend endpoints.
"""

import json
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlparse
import httpx
from rich.console import Console
from pydantic import BaseModel, ValidationError

from .config import Config

console = Console()

class APIError(Exception):
    """Custom exception for API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)

class APIClient:
    """HTTP client for Kartavya API communication."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize API client with configuration."""
        self.config = config or Config()
        self.api_config = self.config.get_api_config()
        self.auth_config = self.config.get_auth_config()
        
        # Validate base URL
        self.base_url = self.api_config.get('base_url')
        if not self.base_url:
            raise APIError("API base URL not configured. Run 'kartavya setup' first.")
        
        # Ensure base URL ends with /
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        
        # Initialize HTTP client
        timeout = httpx.Timeout(self.api_config.get('timeout', 30.0))
        verify_ssl = self.api_config.get('verify_ssl', True)
        
        self.client = httpx.Client(
            timeout=timeout,
            verify=verify_ssl,
            follow_redirects=True
        )
        
        # Set up authentication
        self._setup_auth()
    
    def _setup_auth(self):
        """Set up authentication headers."""
        api_key = self.auth_config.get('api_key')
        username = self.auth_config.get('username')
        password = self.auth_config.get('password')
        
        if api_key:
            self.client.headers.update({
                'Authorization': f'Bearer {api_key}',
                'X-API-Key': api_key
            })
        elif username and password:
            # Use basic auth or login to get token
            self._login(username, password)
        else:
            console.print("[yellow]Warning: No authentication configured[/yellow]")
        
        # Set common headers
        self.client.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'kartavya-cli/1.0.0'
        })
    
    def _login(self, username: str, password: str):
        """Login with username/password to get access token."""
        try:
            response = self.client.post(
                urljoin(self.base_url, 'auth/login'),
                json={'username': username, 'password': password}
            )
            response.raise_for_status()
            
            data = response.json()
            access_token = data.get('access_token')
            
            if access_token:
                self.client.headers.update({
                    'Authorization': f'Bearer {access_token}'
                })
            else:
                raise APIError("Login failed: No access token received")
                
        except httpx.HTTPStatusError as e:
            raise APIError(f"Login failed: {e.response.status_code}", e.response.status_code)
        except Exception as e:
            raise APIError(f"Login error: {str(e)}")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        data: Optional[Dict] = None,
        stream: bool = False
    ) -> Union[Dict, httpx.Response]:
        """Make HTTP request with error handling."""
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        try:
            response = self.client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                data=data,
                stream=stream
            )
            
            if stream:
                return response
            
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                # Return text content if not JSON
                return {'content': response.text}
                
        except httpx.HTTPStatusError as e:
            error_data = None
            try:
                error_data = e.response.json()
            except:
                error_data = {'detail': e.response.text}
            
            raise APIError(
                f"API request failed: {e.response.status_code}",
                status_code=e.response.status_code,
                response_data=error_data
            )
        except httpx.RequestError as e:
            raise APIError(f"Request error: {str(e)}")
    
    def get_health(self) -> bool:
        """Check API health status."""
        try:
            response = self._make_request('GET', 'health')
            return response.get('status') == 'ok'
        except:
            return False
    
    # Assistant API methods
    def chat_with_assistant(self, message: str, conversation_id: Optional[str] = None) -> Dict:
        """Send message to AI assistant."""
        payload = {
            'message': message,
            'conversation_id': conversation_id
        }
        return self._make_request('POST', 'assistant/chat', json_data=payload)
    
    def stream_chat_response(self, message: str, conversation_id: Optional[str] = None):
        """Stream chat response from AI assistant."""
        payload = {
            'message': message,
            'conversation_id': conversation_id,
            'stream': True
        }
        response = self._make_request('POST', 'assistant/stream', json_data=payload, stream=True)
        return response
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Get conversation history."""
        response = self._make_request('GET', f'assistant/conversations/{conversation_id}')
        return response.get('messages', [])
    
    # Platform Events API methods
    def get_platform_events(
        self, 
        event_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get platform events with filters."""
        params = {'limit': limit}
        if event_type:
            params['event_type'] = event_type
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
            
        response = self._make_request('GET', 'platform_events', params=params)
        return response.get('events', [])
    
    def get_authentication_events(self, limit: int = 100) -> List[Dict]:
        """Get authentication events."""
        return self.get_platform_events(event_type='authentication', limit=limit)
    
    def get_failed_login_events(self, limit: int = 100) -> List[Dict]:
        """Get failed login events."""
        return self.get_platform_events(event_type='failed_login', limit=limit)
    
    def get_network_events(self, limit: int = 100) -> List[Dict]:
        """Get network events."""
        return self.get_platform_events(event_type='network', limit=limit)
    
    # Reports API methods
    def generate_report(self, report_type: str, parameters: Dict) -> Dict:
        """Generate a new report."""
        payload = {
            'report_type': report_type,
            'parameters': parameters
        }
        return self._make_request('POST', 'reports/generate', json_data=payload)
    
    def get_reports(self, limit: int = 50) -> List[Dict]:
        """Get list of reports."""
        response = self._make_request('GET', 'reports', params={'limit': limit})
        return response.get('reports', [])
    
    def get_report(self, report_id: str) -> Dict:
        """Get specific report."""
        return self._make_request('GET', f'reports/{report_id}')
    
    def export_report(self, report_id: str, format: str = 'csv') -> Dict:
        """Export report in specified format."""
        params = {'format': format}
        return self._make_request('GET', f'reports/{report_id}/export', params=params)
    
    def schedule_report(self, report_config: Dict) -> Dict:
        """Schedule recurring report."""
        return self._make_request('POST', 'reports/schedule', json_data=report_config)
    
    # Query API methods
    def execute_query(self, query: str, query_type: str = 'natural') -> Dict:
        """Execute a query."""
        payload = {
            'query': query,
            'query_type': query_type
        }
        return self._make_request('POST', 'query/execute', json_data=payload)
    
    def translate_query(self, natural_query: str) -> Dict:
        """Translate natural language to structured query."""
        payload = {'query': natural_query}
        return self._make_request('POST', 'query/translate', json_data=payload)
    
    def get_query_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions."""
        params = {'q': partial_query}
        response = self._make_request('GET', 'query/suggestions', params=params)
        return response.get('suggestions', [])
    
    def optimize_query(self, query: str) -> Dict:
        """Optimize a query for better performance."""
        payload = {'query': query}
        return self._make_request('POST', 'query/optimize', json_data=payload)
    
    def validate_query(self, query: str) -> Dict:
        """Validate query syntax."""
        payload = {'query': query}
        return self._make_request('POST', 'query/validate', json_data=payload)
    
    # Dashboard API methods
    def get_dashboard_metrics(self) -> Dict:
        """Get dashboard metrics."""
        return self._make_request('GET', 'dashboard/metrics')
    
    def get_alerts(self, status: Optional[str] = None) -> List[Dict]:
        """Get alerts with optional status filter."""
        params = {}
        if status:
            params['status'] = status
        response = self._make_request('GET', 'dashboard/alerts', params=params)
        return response.get('alerts', [])
    
    def acknowledge_alert(self, alert_id: str) -> Dict:
        """Acknowledge an alert."""
        return self._make_request('POST', f'dashboard/alerts/{alert_id}/acknowledge')
    
    # Admin API methods
    def get_users(self, limit: int = 100) -> List[Dict]:
        """Get list of users."""
        params = {'limit': limit}
        response = self._make_request('GET', 'admin/users', params=params)
        return response.get('users', [])
    
    def create_user(self, user_data: Dict) -> Dict:
        """Create a new user."""
        return self._make_request('POST', 'admin/users', json_data=user_data)
    
    def update_user(self, user_id: str, user_data: Dict) -> Dict:
        """Update user information."""
        return self._make_request('PUT', f'admin/users/{user_id}', json_data=user_data)
    
    def delete_user(self, user_id: str) -> Dict:
        """Delete a user."""
        return self._make_request('DELETE', f'admin/users/{user_id}')
    
    def get_audit_logs(self, limit: int = 100) -> List[Dict]:
        """Get audit logs."""
        params = {'limit': limit}
        response = self._make_request('GET', 'admin/audit-logs', params=params)
        return response.get('logs', [])
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

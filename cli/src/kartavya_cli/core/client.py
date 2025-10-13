"""
HTTP client for communicating with Kartavya API
Handles authentication, request/response formatting, and error handling
"""

import asyncio
import json
import sys
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin
import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import logging

from .config import get_config, KartavyaConfig

logger = logging.getLogger(__name__)
console = Console()


class APIError(Exception):
    """Custom exception for API errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class KartavyaClient:
    """HTTP client for Kartavya API with authentication and error handling"""
    
    def __init__(self, config: Optional[KartavyaConfig] = None):
        self.config = config or get_config()
        self.client = httpx.AsyncClient(
            timeout=self.config.api_timeout,
            headers=self._get_headers()
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers including authentication"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Kartavya-CLI/1.0.0",
            "Accept": "application/json"
        }
        
        if self.config.api_token:
            headers["Authorization"] = f"Bearer {self.config.api_token}"
        
        return headers
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        return urljoin(self.config.api_url.rstrip('/') + '/', endpoint.lstrip('/'))
    
    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and errors"""
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"message": response.text}
        
        if response.is_success:
            return data
        
        # Handle API errors
        error_message = data.get("detail") or data.get("error") or data.get("message") or "Unknown API error"
        
        if response.status_code == 401:
            error_message = "Authentication failed. Please check your API token."
        elif response.status_code == 403:
            error_message = "Access forbidden. Check your permissions."
        elif response.status_code == 404:
            error_message = "API endpoint not found."
        elif response.status_code == 500:
            error_message = "Internal server error. Please try again later."
        elif response.status_code >= 400:
            error_message = f"API request failed: {error_message}"
        
        raise APIError(error_message, response.status_code, data)
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request"""
        url = self._build_url(endpoint)
        try:
            response = await self.client.get(url, params=params)
            return await self._handle_response(response)
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request"""
        url = self._build_url(endpoint)
        try:
            response = await self.client.post(url, json=data, params=params)
            return await self._handle_response(response)
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request"""
        url = self._build_url(endpoint)
        try:
            response = await self.client.put(url, json=data)
            return await self._handle_response(response)
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        url = self._build_url(endpoint)
        try:
            response = await self.client.delete(url)
            return await self._handle_response(response)
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    async def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PATCH request"""
        url = self._build_url(endpoint)
        try:
            response = await self.client.patch(url, json=data)
            return await self._handle_response(response)
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check if API is accessible"""
        try:
            await self.get("/health")
            return True
        except Exception:
            return False
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def run_async(coro):
    """Run async function in sync context (for CLI commands)"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


async def make_request_with_spinner(
    client: KartavyaClient,
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    description: str = "Making API request..."
) -> Dict[str, Any]:
    """Make API request with a spinner for user feedback"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        progress.add_task(description=description, total=None)
        
        try:
            if method.upper() == "GET":
                return await client.get(endpoint, params=params)
            elif method.upper() == "POST":
                return await client.post(endpoint, data=data, params=params)
            elif method.upper() == "PUT":
                return await client.put(endpoint, data=data)
            elif method.upper() == "DELETE":
                return await client.delete(endpoint)
            elif method.upper() == "PATCH":
                return await client.patch(endpoint, data=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Request failed: {str(e)}")


def get_client() -> KartavyaClient:
    """Get a configured API client"""
    return KartavyaClient()

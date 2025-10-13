from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import time
import os
from typing import Dict, Optional
import asyncio
from datetime import datetime, timedelta

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60, burst_limit: int = 100):
        super().__init__(app)
        self.requests_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", requests_per_minute))
        self.burst_limit = int(os.getenv("RATE_LIMIT_BURST", burst_limit))
        self.client_requests: Dict[str, list] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Start cleanup task
        if not self.cleanup_task:
            self.cleanup_task = asyncio.create_task(self._cleanup_old_requests())
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get real IP from headers (for reverse proxy setups)
        client_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or
            request.headers.get("X-Real-IP", "") or
            request.client.host if request.client else "unknown"
        )
        
        # Include user agent for better uniqueness
        user_agent = request.headers.get("User-Agent", "unknown")
        return f"{client_ip}:{hash(user_agent) % 10000}"
    
    def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited"""
        now = time.time()
        minute_ago = now - 60
        
        # Get or create client request history
        if client_id not in self.client_requests:
            self.client_requests[client_id] = []
        
        # Remove requests older than 1 minute
        self.client_requests[client_id] = [
            timestamp for timestamp in self.client_requests[client_id] 
            if timestamp > minute_ago
        ]
        
        # Check rate limits
        recent_requests = len(self.client_requests[client_id])
        
        # Burst protection: no more than burst_limit requests per minute
        if recent_requests >= self.burst_limit:
            return True
        
        # Normal rate limiting: requests_per_minute average
        if recent_requests >= self.requests_per_minute:
            return True
        
        return False
    
    def _should_skip_rate_limiting(self, request: Request) -> bool:
        """Check if request should skip rate limiting"""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/ping", "/"]:
            return True
        
        # Skip for WebSocket connections
        if request.url.path.startswith("/ws"):
            return True
        
        # Skip in development mode
        if os.getenv("ENVIRONMENT", "demo") == "demo":
            return True
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain requests
        if self._should_skip_rate_limiting(request):
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if self._is_rate_limited(client_id):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.requests_per_minute} requests per minute",
                    "retry_after": 60,
                    "timestamp": datetime.now().isoformat()
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + 60))
                }
            )
        
        # Record this request
        self.client_requests[client_id].append(time.time())
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining = max(0, self.requests_per_minute - len(self.client_requests[client_id]))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
        
        return response
    
    async def _cleanup_old_requests(self):
        """Periodic cleanup of old request records"""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                now = time.time()
                hour_ago = now - 3600  # Keep only last hour
                
                # Clean up old records
                for client_id in list(self.client_requests.keys()):
                    self.client_requests[client_id] = [
                        timestamp for timestamp in self.client_requests[client_id]
                        if timestamp > hour_ago
                    ]
                    
                    # Remove empty client records
                    if not self.client_requests[client_id]:
                        del self.client_requests[client_id]
                        
            except Exception as e:
                print(f"Rate limit cleanup error: {e}")
                continue

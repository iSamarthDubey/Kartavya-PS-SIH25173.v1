"""
Performance Monitoring Middleware for FastAPI
Automatically profiles all API endpoints and integrates with the performance profiler
"""

import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ...core.monitoring.performance_profiler import (
    performance_profiler, 
    QueryType, 
    PerformanceProfiler
)

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically monitor API endpoint performance"""
    
    def __init__(self, app, profiler: Optional[PerformanceProfiler] = None):
        super().__init__(app)
        self.profiler = profiler or performance_profiler
        self.exclude_paths = {
            "/docs", "/redoc", "/openapi.json", 
            "/health", "/metrics", "/favicon.ico"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitor request performance"""
        
        # Skip monitoring for certain paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Generate request ID
        request_id = f"{request.method}_{request.url.path}_{int(time.time() * 1000)}"
        endpoint = f"{request.method} {request.url.path}"
        
        # Extract metadata
        metadata = {
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "content_type": request.headers.get("content-type"),
            "content_length": request.headers.get("content-length")
        }
        
        # Profile the request
        async with self.profiler.profile_request(
            query_type=QueryType.API_ENDPOINT,
            endpoint=endpoint,
            query_id=request_id,
            metadata=metadata
        ):
            response = await call_next(request)
            
            # Add response metadata
            metadata.update({
                "response_status": response.status_code,
                "response_size": response.headers.get("content-length")
            })
        
        # Add performance headers
        if hasattr(response, 'headers'):
            response.headers["X-Request-ID"] = request_id
        
        return response


class PerformanceAPIRoute(APIRoute):
    """Custom API route class that adds performance monitoring to specific endpoints"""
    
    def __init__(self, *args, profiler: Optional[PerformanceProfiler] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profiler = profiler or performance_profiler
    
    def get_route_handler(self) -> Callable:
        """Override route handler to add performance monitoring"""
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request) -> Response:
            # Profile the specific route
            endpoint = f"{request.method} {self.path}"
            request_id = f"{endpoint}_{int(time.time() * 1000)}"
            
            metadata = {
                "route_name": self.name,
                "route_path": self.path,
                "method": request.method,
                "tags": list(self.tags) if self.tags else []
            }
            
            async with self.profiler.profile_request(
                query_type=QueryType.API_ENDPOINT,
                endpoint=endpoint,
                query_id=request_id,
                metadata=metadata
            ):
                return await original_route_handler(request)
        
        return custom_route_handler


# Database query profiling decorator
def profile_database_query(query_type: str = "database"):
    """Decorator to profile database queries"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            endpoint = f"{query_type}_{func.__name__}"
            
            async with performance_profiler.profile_request(
                query_type=QueryType.DATABASE_QUERY,
                endpoint=endpoint,
                metadata={
                    "function": func.__name__,
                    "module": func.__module__,
                    "query_type": query_type
                }
            ):
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Cache operation profiling decorator  
def profile_cache_operation(operation: str = "cache"):
    """Decorator to profile cache operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            endpoint = f"{operation}_{func.__name__}"
            
            async with performance_profiler.profile_request(
                query_type=QueryType.CACHE_OPERATION,
                endpoint=endpoint,
                metadata={
                    "function": func.__name__,
                    "operation": operation
                }
            ):
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# External API profiling decorator
def profile_external_api(service_name: str):
    """Decorator to profile external API calls"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            endpoint = f"external_{service_name}_{func.__name__}"
            
            async with performance_profiler.profile_request(
                query_type=QueryType.EXTERNAL_API,
                endpoint=endpoint,
                metadata={
                    "service": service_name,
                    "function": func.__name__
                }
            ):
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Performance monitoring route handlers
async def get_performance_health(request: Request) -> JSONResponse:
    """Get system performance health status"""
    try:
        health_status = performance_profiler.get_health_status()
        return JSONResponse(content=health_status)
    except Exception as e:
        logger.error(f"Error getting performance health: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get performance health", "details": str(e)}
        )


async def get_performance_summary(request: Request) -> JSONResponse:
    """Get comprehensive performance summary"""
    try:
        # Get time window from query params (default 60 minutes)
        time_window = int(request.query_params.get("window", 60))
        
        summary = performance_profiler.get_performance_summary(time_window)
        return JSONResponse(content=summary)
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get performance summary", "details": str(e)}
        )


async def get_endpoint_details(request: Request) -> JSONResponse:
    """Get detailed performance statistics for a specific endpoint"""
    try:
        endpoint = request.path_params.get("endpoint")
        if not endpoint:
            return JSONResponse(
                status_code=400,
                content={"error": "Endpoint parameter is required"}
            )
        
        # URL decode the endpoint
        import urllib.parse
        endpoint = urllib.parse.unquote(endpoint)
        
        details = performance_profiler.get_endpoint_details(endpoint)
        return JSONResponse(content=details)
    except Exception as e:
        logger.error(f"Error getting endpoint details: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get endpoint details", "details": str(e)}
        )


async def get_performance_alerts(request: Request) -> JSONResponse:
    """Get current performance alerts"""
    try:
        alerts = performance_profiler.get_performance_alerts()
        return JSONResponse(content={"alerts": alerts, "count": len(alerts)})
    except Exception as e:
        logger.error(f"Error getting performance alerts: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get performance alerts", "details": str(e)}
        )


async def reset_performance_stats(request: Request) -> JSONResponse:
    """Reset performance statistics (admin only)"""
    try:
        performance_profiler.reset_stats()
        return JSONResponse(content={"message": "Performance statistics reset successfully"})
    except Exception as e:
        logger.error(f"Error resetting performance stats: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to reset performance stats", "details": str(e)}
        )


# Helper function to add performance monitoring routes
def add_performance_routes(app, prefix: str = "/api/v1/performance"):
    """Add performance monitoring routes to FastAPI app"""
    from fastapi import APIRouter
    
    router = APIRouter(prefix=prefix, tags=["Performance Monitoring"])
    
    router.add_api_route("/health", get_performance_health, methods=["GET"])
    router.add_api_route("/summary", get_performance_summary, methods=["GET"])
    router.add_api_route("/endpoint/{endpoint:path}", get_endpoint_details, methods=["GET"])
    router.add_api_route("/alerts", get_performance_alerts, methods=["GET"])
    router.add_api_route("/reset", reset_performance_stats, methods=["POST"])
    
    app.include_router(router)
    logger.info(f"Performance monitoring routes added with prefix: {prefix}")

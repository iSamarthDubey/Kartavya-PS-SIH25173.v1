"""
Comprehensive API Middleware
Provides request validation, rate limiting, error handling, response formatting, and API versioning
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import traceback
import hashlib
import ipaddress
from functools import wraps

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
import redis
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Standardized error codes"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    QUERY_TIMEOUT = "QUERY_TIMEOUT"
    INVALID_QUERY_SYNTAX = "INVALID_QUERY_SYNTAX"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"


@dataclass
class APIResponse:
    """Standardized API response format"""
    success: bool
    data: Any = None
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str = ""
    request_id: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    window_size: int = 60  # seconds


@dataclass
class ValidationRule:
    """Request validation rule"""
    field: str
    rule_type: str  # "required", "type", "range", "regex", "custom"
    parameters: Dict[str, Any]
    error_message: str


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for input validation and attack prevention"""
    
    def __init__(self, app, config: Optional[Dict[str, Any]] = None):
        super().__init__(app)
        self.config = config or {}
        self.blocked_ips = set()
        self.suspicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'eval\s*\(',
            r'alert\s*\(',
            r'document\.cookie',
            r'window\.location',
            r'exec\s*\(',
            r'system\s*\(',
            r'\.\./',
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from'
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process security checks"""
        try:
            # Check IP blocking
            client_ip = self._get_client_ip(request)
            if client_ip in self.blocked_ips:
                return self._create_error_response(
                    ErrorCode.SECURITY_VIOLATION,
                    "IP address blocked",
                    status.HTTP_403_FORBIDDEN
                )
            
            # Validate content length
            content_length = request.headers.get("content-length", "0")
            if int(content_length) > self.config.get("max_content_length", 10 * 1024 * 1024):  # 10MB
                return self._create_error_response(
                    ErrorCode.VALIDATION_ERROR,
                    "Request payload too large",
                    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                )
            
            # Check for suspicious patterns in headers
            if self._check_headers_for_attacks(request.headers):
                logger.warning(f"Suspicious headers detected from {client_ip}")
                return self._create_error_response(
                    ErrorCode.SECURITY_VIOLATION,
                    "Suspicious request headers",
                    status.HTTP_400_BAD_REQUEST
                )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = "default-src 'self'"
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return self._create_error_response(
                ErrorCode.INTERNAL_SERVER_ERROR,
                "Security check failed",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check X-Forwarded-For header first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to client host
        return request.client.host if request.client else "unknown"
    
    def _check_headers_for_attacks(self, headers) -> bool:
        """Check headers for attack patterns"""
        import re
        
        for name, value in headers.items():
            for pattern in self.suspicious_patterns:
                if re.search(pattern, str(value), re.IGNORECASE):
                    return True
        return False
    
    def _create_error_response(self, error_code: ErrorCode, message: str, status_code: int) -> JSONResponse:
        """Create standardized error response"""
        error_response = APIResponse(
            success=False,
            error={
                "code": error_code.value,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        )
        return JSONResponse(content=asdict(error_response), status_code=status_code)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting middleware with Redis backend"""
    
    def __init__(self, app, redis_client=None, config: Optional[RateLimitConfig] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.config = config or RateLimitConfig()
        self.local_cache = {}  # Fallback for when Redis is unavailable
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting"""
        try:
            client_ip = self._get_client_ip(request)
            endpoint = str(request.url.path)
            
            # Check rate limits
            is_allowed, reset_time = await self._check_rate_limits(client_ip, endpoint)
            
            if not is_allowed:
                return self._create_rate_limit_response(reset_time)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            remaining = await self._get_remaining_requests(client_ip, endpoint)
            response.headers["X-RateLimit-Limit"] = str(self.config.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue processing if rate limiting fails
            return await call_next(request)
    
    async def _check_rate_limits(self, client_ip: str, endpoint: str) -> tuple[bool, int]:
        """Check if request is within rate limits"""
        current_time = int(time.time())
        
        # Create keys for different time windows
        minute_key = f"rate_limit:{client_ip}:{endpoint}:minute:{current_time // 60}"
        hour_key = f"rate_limit:{client_ip}:{endpoint}:hour:{current_time // 3600}"
        day_key = f"rate_limit:{client_ip}:{endpoint}:day:{current_time // 86400}"
        
        if self.redis_client:
            try:
                # Check and increment counters atomically
                pipe = self.redis_client.pipeline()
                pipe.incr(minute_key, 1)
                pipe.expire(minute_key, 60)
                pipe.incr(hour_key, 1)
                pipe.expire(hour_key, 3600)
                pipe.incr(day_key, 1)
                pipe.expire(day_key, 86400)
                results = pipe.execute()
                
                minute_count = results[0]
                hour_count = results[2]
                day_count = results[4]
                
            except Exception as e:
                logger.warning(f"Redis rate limiting failed, using local cache: {e}")
                return await self._check_local_rate_limits(client_ip, endpoint, current_time)
        else:
            return await self._check_local_rate_limits(client_ip, endpoint, current_time)
        
        # Check limits
        if minute_count > self.config.requests_per_minute:
            return False, (current_time // 60 + 1) * 60
        if hour_count > self.config.requests_per_hour:
            return False, (current_time // 3600 + 1) * 3600
        if day_count > self.config.requests_per_day:
            return False, (current_time // 86400 + 1) * 86400
        
        return True, (current_time // 60 + 1) * 60
    
    async def _check_local_rate_limits(self, client_ip: str, endpoint: str, current_time: int) -> tuple[bool, int]:
        """Fallback rate limiting using local cache"""
        key = f"{client_ip}:{endpoint}"
        
        if key not in self.local_cache:
            self.local_cache[key] = {
                "minute": {"count": 0, "window": current_time // 60},
                "hour": {"count": 0, "window": current_time // 3600},
                "day": {"count": 0, "window": current_time // 86400}
            }
        
        cache_entry = self.local_cache[key]
        
        # Reset counters if windows have passed
        minute_window = current_time // 60
        if cache_entry["minute"]["window"] < minute_window:
            cache_entry["minute"] = {"count": 0, "window": minute_window}
        
        hour_window = current_time // 3600
        if cache_entry["hour"]["window"] < hour_window:
            cache_entry["hour"] = {"count": 0, "window": hour_window}
        
        day_window = current_time // 86400
        if cache_entry["day"]["window"] < day_window:
            cache_entry["day"] = {"count": 0, "window": day_window}
        
        # Check limits
        if cache_entry["minute"]["count"] >= self.config.requests_per_minute:
            return False, (minute_window + 1) * 60
        if cache_entry["hour"]["count"] >= self.config.requests_per_hour:
            return False, (hour_window + 1) * 3600
        if cache_entry["day"]["count"] >= self.config.requests_per_day:
            return False, (day_window + 1) * 86400
        
        # Increment counters
        cache_entry["minute"]["count"] += 1
        cache_entry["hour"]["count"] += 1
        cache_entry["day"]["count"] += 1
        
        return True, (minute_window + 1) * 60
    
    async def _get_remaining_requests(self, client_ip: str, endpoint: str) -> int:
        """Get remaining requests for current minute"""
        current_time = int(time.time())
        minute_key = f"rate_limit:{client_ip}:{endpoint}:minute:{current_time // 60}"
        
        if self.redis_client:
            try:
                current_count = self.redis_client.get(minute_key) or 0
                return max(0, self.config.requests_per_minute - int(current_count))
            except:
                pass
        
        # Fallback to local cache
        key = f"{client_ip}:{endpoint}"
        if key in self.local_cache:
            return max(0, self.config.requests_per_minute - self.local_cache[key]["minute"]["count"])
        
        return self.config.requests_per_minute
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _create_rate_limit_response(self, reset_time: int) -> JSONResponse:
        """Create rate limit exceeded response"""
        error_response = APIResponse(
            success=False,
            error={
                "code": ErrorCode.RATE_LIMIT_EXCEEDED.value,
                "message": "Rate limit exceeded. Please try again later.",
                "reset_time": reset_time
            }
        )
        return JSONResponse(content=asdict(error_response), status_code=429)


class ValidationMiddleware(BaseHTTPMiddleware):
    """Request validation middleware"""
    
    def __init__(self, app, validation_rules: Optional[Dict[str, List[ValidationRule]]] = None):
        super().__init__(app)
        self.validation_rules = validation_rules or {}
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate requests"""
        try:
            endpoint = str(request.url.path)
            method = request.method.lower()
            
            # Get validation rules for this endpoint
            rules_key = f"{method}:{endpoint}"
            rules = self.validation_rules.get(rules_key, [])
            
            if rules and request.method in ["POST", "PUT", "PATCH"]:
                # Validate request body
                try:
                    body = await request.body()
                    if body:
                        data = json.loads(body.decode())
                        validation_errors = await self._validate_data(data, rules)
                        if validation_errors:
                            return self._create_validation_error_response(validation_errors)
                except json.JSONDecodeError:
                    return self._create_validation_error_response(["Invalid JSON format"])
            
            # Process request
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Validation middleware error: {e}")
            return await call_next(request)
    
    async def _validate_data(self, data: Dict[str, Any], rules: List[ValidationRule]) -> List[str]:
        """Validate data against rules"""
        errors = []
        
        for rule in rules:
            field_value = data.get(rule.field)
            
            if rule.rule_type == "required" and field_value is None:
                errors.append(rule.error_message)
            elif rule.rule_type == "type" and field_value is not None:
                expected_type = rule.parameters.get("type")
                if not isinstance(field_value, expected_type):
                    errors.append(rule.error_message)
            elif rule.rule_type == "range" and field_value is not None:
                min_val = rule.parameters.get("min")
                max_val = rule.parameters.get("max")
                if min_val is not None and field_value < min_val:
                    errors.append(rule.error_message)
                if max_val is not None and field_value > max_val:
                    errors.append(rule.error_message)
            elif rule.rule_type == "regex" and field_value is not None:
                import re
                pattern = rule.parameters.get("pattern")
                if pattern and not re.match(pattern, str(field_value)):
                    errors.append(rule.error_message)
        
        return errors
    
    def _create_validation_error_response(self, errors: List[str]) -> JSONResponse:
        """Create validation error response"""
        error_response = APIResponse(
            success=False,
            error={
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message": "Request validation failed",
                "details": errors
            }
        )
        return JSONResponse(content=asdict(error_response), status_code=400)


class ResponseFormattingMiddleware(BaseHTTPMiddleware):
    """Response formatting and standardization middleware"""
    
    def __init__(self, app, include_metadata: bool = True):
        super().__init__(app)
        self.include_metadata = include_metadata
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Format responses"""
        start_time = time.time()
        request_id = self._generate_request_id(request)
        
        try:
            # Add request ID to request state
            request.state.request_id = request_id
            
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Add standard headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
            
            # Format response if it's JSON
            if response.headers.get("content-type", "").startswith("application/json"):
                response = await self._format_json_response(response, request_id, processing_time)
            
            return response
            
        except HTTPException as e:
            # Handle HTTP exceptions
            error_response = APIResponse(
                success=False,
                error={
                    "code": self._get_error_code_from_status(e.status_code),
                    "message": e.detail,
                    "status_code": e.status_code
                },
                request_id=request_id
            )
            return JSONResponse(content=asdict(error_response), status_code=e.status_code)
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error processing request {request_id}: {e}", exc_info=True)
            error_response = APIResponse(
                success=False,
                error={
                    "code": ErrorCode.INTERNAL_SERVER_ERROR.value,
                    "message": "An unexpected error occurred",
                    "request_id": request_id
                },
                request_id=request_id
            )
            return JSONResponse(content=asdict(error_response), status_code=500)
    
    async def _format_json_response(self, response: Response, request_id: str, processing_time: float) -> Response:
        """Format JSON response with standard structure"""
        try:
            # Read response content
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Parse existing content
            if response_body:
                existing_data = json.loads(response_body.decode())
                
                # Check if already formatted
                if isinstance(existing_data, dict) and "success" in existing_data:
                    return response
                
                # Format response
                formatted_response = APIResponse(
                    success=response.status_code < 400,
                    data=existing_data,
                    metadata={
                        "request_id": request_id,
                        "processing_time": f"{processing_time:.3f}s",
                        "timestamp": datetime.now().isoformat()
                    } if self.include_metadata else None,
                    request_id=request_id
                )
                
                # Create new response
                new_content = json.dumps(asdict(formatted_response), default=str)
                return Response(
                    content=new_content,
                    status_code=response.status_code,
                    headers=response.headers,
                    media_type="application/json"
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return response
    
    def _generate_request_id(self, request: Request) -> str:
        """Generate unique request ID"""
        timestamp = str(int(time.time() * 1000))
        client_ip = request.client.host if request.client else "unknown"
        path = str(request.url.path)
        
        unique_string = f"{timestamp}:{client_ip}:{path}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def _get_error_code_from_status(self, status_code: int) -> str:
        """Map HTTP status codes to error codes"""
        mapping = {
            400: ErrorCode.VALIDATION_ERROR.value,
            401: ErrorCode.AUTHENTICATION_FAILED.value,
            403: ErrorCode.AUTHORIZATION_FAILED.value,
            404: ErrorCode.RESOURCE_NOT_FOUND.value,
            429: ErrorCode.RATE_LIMIT_EXCEEDED.value,
            500: ErrorCode.INTERNAL_SERVER_ERROR.value,
            502: ErrorCode.EXTERNAL_SERVICE_ERROR.value,
            503: ErrorCode.EXTERNAL_SERVICE_ERROR.value,
            504: ErrorCode.QUERY_TIMEOUT.value
        }
        return mapping.get(status_code, ErrorCode.INTERNAL_SERVER_ERROR.value)


class APIVersioningMiddleware(BaseHTTPMiddleware):
    """API versioning middleware"""
    
    def __init__(self, app, default_version: str = "v1", supported_versions: Optional[List[str]] = None):
        super().__init__(app)
        self.default_version = default_version
        self.supported_versions = supported_versions or ["v1"]
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle API versioning"""
        try:
            # Extract version from header or path
            version = self._extract_version(request)
            
            # Validate version
            if version not in self.supported_versions:
                return self._create_unsupported_version_response(version)
            
            # Add version to request state
            request.state.api_version = version
            
            # Process request
            response = await call_next(request)
            
            # Add version header to response
            response.headers["X-API-Version"] = version
            
            return response
            
        except Exception as e:
            logger.error(f"API versioning error: {e}")
            return await call_next(request)
    
    def _extract_version(self, request: Request) -> str:
        """Extract API version from request"""
        # Check header first
        version_header = request.headers.get("X-API-Version")
        if version_header and version_header in self.supported_versions:
            return version_header
        
        # Check path
        path_parts = str(request.url.path).strip("/").split("/")
        if path_parts and path_parts[0].startswith("v") and path_parts[0] in self.supported_versions:
            return path_parts[0]
        
        # Default version
        return self.default_version
    
    def _create_unsupported_version_response(self, version: str) -> JSONResponse:
        """Create unsupported version response"""
        error_response = APIResponse(
            success=False,
            error={
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message": f"Unsupported API version: {version}",
                "supported_versions": self.supported_versions
            }
        )
        return JSONResponse(content=asdict(error_response), status_code=400)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Performance monitoring and metrics collection middleware"""
    
    def __init__(self, app, metrics_collector=None):
        super().__init__(app)
        self.metrics_collector = metrics_collector
        self.slow_request_threshold = 5.0  # seconds
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitor performance metrics"""
        start_time = time.time()
        endpoint = str(request.url.path)
        method = request.method
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate metrics
            processing_time = time.time() - start_time
            
            # Log slow requests
            if processing_time > self.slow_request_threshold:
                logger.warning(f"Slow request detected: {method} {endpoint} took {processing_time:.3f}s")
            
            # Collect metrics
            if self.metrics_collector:
                await self._collect_metrics(endpoint, method, processing_time, response.status_code)
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Request failed: {method} {endpoint} after {processing_time:.3f}s: {e}")
            
            # Collect error metrics
            if self.metrics_collector:
                await self._collect_metrics(endpoint, method, processing_time, 500, error=str(e))
            
            raise
    
    async def _collect_metrics(self, endpoint: str, method: str, processing_time: float, status_code: int, error: Optional[str] = None):
        """Collect performance metrics"""
        try:
            metrics = {
                "endpoint": endpoint,
                "method": method,
                "processing_time": processing_time,
                "status_code": status_code,
                "timestamp": datetime.now().isoformat(),
                "error": error
            }
            
            # Send to metrics collector (could be StatsD, Prometheus, etc.)
            await self.metrics_collector.record_request_metrics(metrics)
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")


# Utility functions for creating validation rules
def create_validation_rules() -> Dict[str, List[ValidationRule]]:
    """Create validation rules for API endpoints"""
    return {
        "post:/api/assistant/chat": [
            ValidationRule(
                field="query",
                rule_type="required",
                parameters={},
                error_message="Query field is required"
            ),
            ValidationRule(
                field="query",
                rule_type="type",
                parameters={"type": str},
                error_message="Query must be a string"
            ),
            ValidationRule(
                field="limit",
                rule_type="range",
                parameters={"min": 1, "max": 1000},
                error_message="Limit must be between 1 and 1000"
            )
        ],
        "post:/api/query/execute": [
            ValidationRule(
                field="query",
                rule_type="required",
                parameters={},
                error_message="Query field is required"
            ),
            ValidationRule(
                field="params",
                rule_type="type",
                parameters={"type": dict},
                error_message="Params must be an object"
            )
        ]
    }


# Factory function to create middleware stack
def create_middleware_stack(app, config: Optional[Dict[str, Any]] = None):
    """Create complete middleware stack"""
    config = config or {}
    
    # Performance monitoring
    if config.get("enable_performance_monitoring", True):
        app.add_middleware(PerformanceMonitoringMiddleware)
    
    # Response formatting
    if config.get("enable_response_formatting", True):
        app.add_middleware(
            ResponseFormattingMiddleware,
            include_metadata=config.get("include_response_metadata", True)
        )
    
    # API versioning
    if config.get("enable_api_versioning", True):
        app.add_middleware(
            APIVersioningMiddleware,
            default_version=config.get("default_api_version", "v1"),
            supported_versions=config.get("supported_api_versions", ["v1"])
        )
    
    # Request validation
    if config.get("enable_validation", True):
        validation_rules = create_validation_rules()
        app.add_middleware(ValidationMiddleware, validation_rules=validation_rules)
    
    # Rate limiting
    if config.get("enable_rate_limiting", True):
        rate_limit_config = RateLimitConfig(
            requests_per_minute=config.get("rate_limit_per_minute", 60),
            requests_per_hour=config.get("rate_limit_per_hour", 1000),
            requests_per_day=config.get("rate_limit_per_day", 10000)
        )
        app.add_middleware(RateLimitMiddleware, config=rate_limit_config)
    
    # Security middleware
    if config.get("enable_security", True):
        security_config = {
            "max_content_length": config.get("max_content_length", 10 * 1024 * 1024)
        }
        app.add_middleware(SecurityMiddleware, config=security_config)
    
    logger.info("Middleware stack configured successfully")

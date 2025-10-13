"""
Platform-Aware Event Routes
Dynamic API routes using universal query builder and platform detection.
NO HARDCODED VALUES - COMPLETELY DYNAMIC.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ...core.services.platform_aware_api import PlatformAwareAPIService
# Auth will be handled at the route level for now
def get_current_user():
    """Placeholder for authentication - to be integrated with actual auth system"""
    return {"username": "system", "role": "admin"}

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/events", tags=["platform-events"])

# Pydantic models
class EventQuery(BaseModel):
    query: str = ""
    time_range: str = "1h"  # 1h, 24h, 7d, etc.
    limit: int = 100

class EventResponse(BaseModel):
    success: bool
    intent: str
    query_info: Dict[str, Any]
    platform_info: Dict[str, Any]
    results: Dict[str, Any]
    total_hits: int
    has_more: bool
    error: Optional[str] = None

# Global platform-aware service (initialized in main.py)
_platform_service: PlatformAwareAPIService = None

def get_platform_service():
    """Get the platform-aware service instance"""
    if _platform_service is None:
        raise HTTPException(status_code=500, detail="Platform service not initialized")
    return _platform_service

def set_platform_service(service: PlatformAwareAPIService):
    """Set the platform-aware service instance (called from main.py)"""
    global _platform_service
    _platform_service = service

@router.get("/capabilities")
async def get_capabilities():
    """Get platform capabilities and available features"""
    try:
        service = get_platform_service()
        capabilities = await service.get_platform_capabilities()
        
        return {
            "success": True,
            "capabilities": capabilities,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/authentication", response_model=EventResponse)
async def get_authentication_events(
    request: EventQuery,
    current_user: dict = Depends(get_current_user)
):
    """Get authentication events using dynamic platform detection"""
    try:
        service = get_platform_service()
        
        logger.info(f"Authentication events query by {current_user.get('username', 'unknown')}")
        
        result = await service.get_authentication_events(
            query=request.query,
            time_range=request.time_range,
            limit=request.limit
        )
        
        return EventResponse(**result)
    
    except Exception as e:
        logger.error(f"Authentication events query failed: {e}")
        return EventResponse(
            success=False,
            intent="authentication_events",
            query_info={"query_text": request.query},
            platform_info={},
            results={"events": [], "aggregations": {}},
            total_hits=0,
            has_more=False,
            error=str(e)
        )

@router.post("/failed-logins", response_model=EventResponse)
async def get_failed_logins(
    request: EventQuery,
    current_user: dict = Depends(get_current_user)
):
    """Get failed login attempts using platform-aware queries"""
    try:
        service = get_platform_service()
        
        result = await service.get_failed_logins(
            query=request.query,
            time_range=request.time_range,
            limit=request.limit
        )
        
        return EventResponse(**result)
    
    except Exception as e:
        logger.error(f"Failed logins query failed: {e}")
        return EventResponse(
            success=False,
            intent="failed_logins",
            query_info={"query_text": request.query},
            platform_info={},
            results={"events": [], "aggregations": {}},
            total_hits=0,
            has_more=False,
            error=str(e)
        )

@router.post("/successful-logins", response_model=EventResponse)
async def get_successful_logins(
    request: EventQuery,
    current_user: dict = Depends(get_current_user)
):
    """Get successful logins using platform-aware queries"""
    try:
        service = get_platform_service()
        
        result = await service.get_successful_logins(
            query=request.query,
            time_range=request.time_range,
            limit=request.limit
        )
        
        return EventResponse(**result)
    
    except Exception as e:
        logger.error(f"Successful logins query failed: {e}")
        return EventResponse(
            success=False,
            intent="successful_logins",
            query_info={"query_text": request.query},
            platform_info={},
            results={"events": [], "aggregations": {}},
            total_hits=0,
            has_more=False,
            error=str(e)
        )

@router.post("/system-metrics", response_model=EventResponse)
async def get_system_metrics(
    request: EventQuery,
    current_user: dict = Depends(get_current_user)
):
    """Get system metrics using platform-aware queries"""
    try:
        service = get_platform_service()
        
        result = await service.get_system_metrics(
            query=request.query,
            time_range=request.time_range,
            limit=request.limit
        )
        
        return EventResponse(**result)
    
    except Exception as e:
        logger.error(f"System metrics query failed: {e}")
        return EventResponse(
            success=False,
            intent="system_metrics",
            query_info={"query_text": request.query},
            platform_info={},
            results={"events": [], "aggregations": {}},
            total_hits=0,
            has_more=False,
            error=str(e)
        )

@router.post("/network-activity", response_model=EventResponse)
async def get_network_activity(
    request: EventQuery,
    current_user: dict = Depends(get_current_user)
):
    """Get network activity using platform-aware queries"""
    try:
        service = get_platform_service()
        
        result = await service.get_network_activity(
            query=request.query,
            time_range=request.time_range,
            limit=request.limit
        )
        
        return EventResponse(**result)
    
    except Exception as e:
        logger.error(f"Network activity query failed: {e}")
        return EventResponse(
            success=False,
            intent="network_activity",
            query_info={"query_text": request.query},
            platform_info={},
            results={"events": [], "aggregations": {}},
            total_hits=0,
            has_more=False,
            error=str(e)
        )

@router.post("/process-activity", response_model=EventResponse)
async def get_process_activity(
    request: EventQuery,
    current_user: dict = Depends(get_current_user)
):
    """Get process activity using platform-aware queries"""
    try:
        service = get_platform_service()
        
        result = await service.get_process_activity(
            query=request.query,
            time_range=request.time_range,
            limit=request.limit
        )
        
        return EventResponse(**result)
    
    except Exception as e:
        logger.error(f"Process activity query failed: {e}")
        return EventResponse(
            success=False,
            intent="process_activity",
            query_info={"query_text": request.query},
            platform_info={},
            results={"events": [], "aggregations": {}},
            total_hits=0,
            has_more=False,
            error=str(e)
        )

@router.post("/user-activity", response_model=EventResponse)
async def get_user_activity(
    request: EventQuery,
    current_user: dict = Depends(get_current_user)
):
    """Get user activity using platform-aware queries"""
    try:
        service = get_platform_service()
        
        result = await service.get_user_activity(
            query=request.query,
            time_range=request.time_range,
            limit=request.limit
        )
        
        return EventResponse(**result)
    
    except Exception as e:
        logger.error(f"User activity query failed: {e}")
        return EventResponse(
            success=False,
            intent="user_activity",
            query_info={"query_text": request.query},
            platform_info={},
            results={"events": [], "aggregations": {}},
            total_hits=0,
            has_more=False,
            error=str(e)
        )

@router.post("/security-alerts", response_model=EventResponse)
async def get_security_alerts(
    request: EventQuery,
    current_user: dict = Depends(get_current_user)
):
    """Get security alerts using platform-aware queries"""
    try:
        service = get_platform_service()
        
        result = await service.get_security_alerts(
            query=request.query,
            time_range=request.time_range,
            limit=request.limit
        )
        
        return EventResponse(**result)
    
    except Exception as e:
        logger.error(f"Security alerts query failed: {e}")
        return EventResponse(
            success=False,
            intent="security_alerts",
            query_info={"query_text": request.query},
            platform_info={},
            results={"events": [], "aggregations": {}},
            total_hits=0,
            has_more=False,
            error=str(e)
        )

@router.post("/search", response_model=EventResponse)
async def generic_search(
    request: EventQuery,
    current_user: dict = Depends(get_current_user)
):
    """Perform generic search using platform-aware queries"""
    try:
        service = get_platform_service()
        
        result = await service.generic_search(
            query=request.query,
            time_range=request.time_range,
            limit=request.limit
        )
        
        return EventResponse(**result)
    
    except Exception as e:
        logger.error(f"Generic search failed: {e}")
        return EventResponse(
            success=False,
            intent="generic_search",
            query_info={"query_text": request.query},
            platform_info={},
            results={"events": [], "aggregations": {}},
            total_hits=0,
            has_more=False,
            error=str(e)
        )

# Legacy compatibility routes (GET methods)
@router.get("/authentication")
async def get_authentication_events_get(
    query: str = Query("", description="Search query"),
    time_range: str = Query("1h", description="Time range (1h, 24h, 7d)"),
    limit: int = Query(100, description="Result limit"),
    current_user: dict = Depends(get_current_user)
):
    """Get authentication events (GET compatibility)"""
    request = EventQuery(query=query, time_range=time_range, limit=limit)
    return await get_authentication_events(request, current_user)

@router.get("/failed-logins")
async def get_failed_logins_get(
    query: str = Query("", description="Search query"),
    time_range: str = Query("1h", description="Time range (1h, 24h, 7d)"),
    limit: int = Query(100, description="Result limit"),
    current_user: dict = Depends(get_current_user)
):
    """Get failed logins (GET compatibility)"""
    request = EventQuery(query=query, time_range=time_range, limit=limit)
    return await get_failed_logins(request, current_user)

@router.get("/successful-logins")
async def get_successful_logins_get(
    query: str = Query("", description="Search query"),
    time_range: str = Query("1h", description="Time range (1h, 24h, 7d)"),
    limit: int = Query(100, description="Result limit"),
    current_user: dict = Depends(get_current_user)
):
    """Get successful logins (GET compatibility)"""
    request = EventQuery(query=query, time_range=time_range, limit=limit)
    return await get_successful_logins(request, current_user)

@router.get("/system-metrics")
async def get_system_metrics_get(
    query: str = Query("", description="Search query"),
    time_range: str = Query("1h", description="Time range (1h, 24h, 7d)"),
    limit: int = Query(100, description="Result limit"),
    current_user: dict = Depends(get_current_user)
):
    """Get system metrics (GET compatibility)"""
    request = EventQuery(query=query, time_range=time_range, limit=limit)
    return await get_system_metrics(request, current_user)

@router.get("/network-activity")
async def get_network_activity_get(
    query: str = Query("", description="Search query"),
    time_range: str = Query("1h", description="Time range (1h, 24h, 7d)"),
    limit: int = Query(100, description="Result limit"),
    current_user: dict = Depends(get_current_user)
):
    """Get network activity (GET compatibility)"""
    request = EventQuery(query=query, time_range=time_range, limit=limit)
    return await get_network_activity(request, current_user)

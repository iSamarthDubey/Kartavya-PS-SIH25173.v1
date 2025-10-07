"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class QueryIntent(str, Enum):
    SEARCH_LOGS = "search_logs"
    AUTHENTICATION = "authentication"
    NETWORK_SECURITY = "network_security"
    MALWARE_DETECTION = "malware_detection"
    USER_ACTIVITY = "user_activity"
    SYSTEM_HEALTH = "system_health"
    THREAT_HUNTING = "threat_hunting"
    COMPLIANCE_CHECK = "compliance_check"
    INCIDENT_INVESTIGATION = "incident_investigation"
    REPORT_GENERATION = "report_generation"

class QueryRequest(BaseModel):
    """Natural language query request"""
    query: str = Field(..., description="Natural language query")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    time_range: Optional[str] = Field(None, description="Time range for query")
    
class Entity(BaseModel):
    """Extracted entity from query"""
    type: str
    value: str
    confidence: float = Field(ge=0, le=1)
    
class QueryResponse(BaseModel):
    """Query response model"""
    success: bool
    query: str
    intent: QueryIntent
    entities: List[Entity]
    results: Dict[str, Any]
    summary: Optional[str] = None
    charts: Optional[List[Dict]] = None
    dsl_query: Optional[Dict] = None
    execution_time_ms: Optional[int] = None
    
class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    elasticsearch_connected: bool
    timestamp: datetime
    
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

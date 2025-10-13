"""
Investigations API Routes - Complete CRUD implementation
Handles investigation lifecycle management for SIEM analysts
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(tags=["investigations"])

# In-memory storage for demo - replace with proper database in production
investigations_store: Dict[str, Dict[str, Any]] = {}

# Request/Response Models
class TimelineEntry(BaseModel):
    """Timeline entry for investigation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    type: str = Field(..., description="Type: query, finding, note, action")
    title: str
    content: str
    user: str
    metadata: Optional[Dict[str, Any]] = None

class InvestigationCreate(BaseModel):
    """Create investigation request"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    tags: List[str] = Field(default_factory=list)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class InvestigationUpdate(BaseModel):
    """Update investigation request"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(open|in_progress|closed)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    tags: Optional[List[str]] = None

class Investigation(BaseModel):
    """Complete investigation model"""
    id: str
    title: str
    status: str = "open"
    priority: str = "medium"
    created_by: str
    created_at: str
    updated_at: str
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    timeline: List[TimelineEntry] = Field(default_factory=list)

class InvestigationList(BaseModel):
    """Paginated investigation list"""
    items: List[Investigation]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

# CRUD Operations
@router.get("/", response_model=InvestigationList)
async def list_investigations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, pattern="^(open|in_progress|closed)$"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high|critical)$"),
    tag: Optional[str] = Query(None, description="Filter by tag")
):
    """
    List investigations with pagination and filtering
    """
    try:
        logger.info(f"Listing investigations: page={page}, limit={limit}, status={status}")
        
        # Filter investigations
        filtered_investigations = []
        for inv_data in investigations_store.values():
            if status and inv_data["status"] != status:
                continue
            if priority and inv_data["priority"] != priority:
                continue
            if tag and tag not in inv_data.get("tags", []):
                continue
            filtered_investigations.append(Investigation(**inv_data))
        
        # Sort by created_at (newest first)
        filtered_investigations.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        total = len(filtered_investigations)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        items = filtered_investigations[start_idx:end_idx]
        
        return InvestigationList(
            items=items,
            total=total,
            page=page,
            per_page=limit,
            has_next=end_idx < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error listing investigations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list investigations: {str(e)}")

@router.get("/{investigation_id}", response_model=Investigation)
async def get_investigation(investigation_id: str):
    """
    Get a specific investigation by ID
    """
    try:
        if investigation_id not in investigations_store:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        investigation_data = investigations_store[investigation_id]
        return Investigation(**investigation_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting investigation {investigation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get investigation: {str(e)}")

@router.post("/", response_model=Investigation)
async def create_investigation(request: InvestigationCreate):
    """
    Create a new investigation
    """
    try:
        investigation_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Create initial timeline entry
        initial_entry = TimelineEntry(
            type="note",
            title="Investigation Created",
            content=f"Investigation '{request.title}' was created",
            user="system"  # In production, get from auth context
        )
        
        investigation_data = {
            "id": investigation_id,
            "title": request.title,
            "status": "open",
            "priority": request.priority,
            "created_by": "current_user",  # In production, get from auth context
            "created_at": now,
            "updated_at": now,
            "description": request.description,
            "tags": request.tags,
            "context": request.context,
            "timeline": [initial_entry.dict()]
        }
        
        investigations_store[investigation_id] = investigation_data
        
        logger.info(f"Created investigation {investigation_id}: {request.title}")
        return Investigation(**investigation_data)
        
    except Exception as e:
        logger.error(f"Error creating investigation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create investigation: {str(e)}")

@router.put("/{investigation_id}", response_model=Investigation)
async def update_investigation(investigation_id: str, request: InvestigationUpdate):
    """
    Update an existing investigation
    """
    try:
        if investigation_id not in investigations_store:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        investigation_data = investigations_store[investigation_id]
        
        # Update fields if provided
        if request.title is not None:
            investigation_data["title"] = request.title
        if request.description is not None:
            investigation_data["description"] = request.description
        if request.status is not None:
            investigation_data["status"] = request.status
        if request.priority is not None:
            investigation_data["priority"] = request.priority
        if request.tags is not None:
            investigation_data["tags"] = request.tags
            
        investigation_data["updated_at"] = datetime.now().isoformat()
        
        # Add timeline entry for significant changes
        if request.status is not None:
            status_entry = TimelineEntry(
                type="action",
                title=f"Status Changed",
                content=f"Status changed to '{request.status}'",
                user="current_user"
            )
            investigation_data["timeline"].append(status_entry.dict())
        
        investigations_store[investigation_id] = investigation_data
        
        logger.info(f"Updated investigation {investigation_id}")
        return Investigation(**investigation_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating investigation {investigation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update investigation: {str(e)}")

@router.delete("/{investigation_id}")
async def delete_investigation(investigation_id: str):
    """
    Delete an investigation
    """
    try:
        if investigation_id not in investigations_store:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        investigation_title = investigations_store[investigation_id]["title"]
        del investigations_store[investigation_id]
        
        logger.info(f"Deleted investigation {investigation_id}: {investigation_title}")
        return {"status": "success", "message": f"Investigation '{investigation_title}' deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting investigation {investigation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete investigation: {str(e)}")

@router.post("/{investigation_id}/timeline", response_model=Investigation)
async def add_timeline_entry(
    investigation_id: str, 
    entry: TimelineEntry
):
    """
    Add a timeline entry to an investigation
    """
    try:
        if investigation_id not in investigations_store:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        investigation_data = investigations_store[investigation_id]
        investigation_data["timeline"].append(entry.dict())
        investigation_data["updated_at"] = datetime.now().isoformat()
        
        investigations_store[investigation_id] = investigation_data
        
        logger.info(f"Added timeline entry to investigation {investigation_id}")
        return Investigation(**investigation_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding timeline entry: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add timeline entry: {str(e)}")

@router.get("/{investigation_id}/timeline", response_model=List[TimelineEntry])
async def get_timeline(investigation_id: str):
    """
    Get timeline for an investigation
    """
    try:
        if investigation_id not in investigations_store:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        investigation_data = investigations_store[investigation_id]
        timeline = [TimelineEntry(**entry) for entry in investigation_data.get("timeline", [])]
        
        return timeline
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get timeline: {str(e)}")

# Initialize with sample data for demo
def initialize_sample_investigations():
    """Initialize with sample investigations for demo purposes"""
    if not investigations_store:  # Only initialize if empty
        sample_investigations = [
            {
                "title": "Suspicious Login Activity - Admin Account",
                "description": "Multiple failed login attempts detected on admin account from unusual locations",
                "priority": "high",
                "tags": ["authentication", "admin", "suspicious"],
                "context": {"session_id": "session_123", "source_ip": "192.168.1.100"}
            },
            {
                "title": "Potential Malware Detection on Server-01",
                "description": "Antivirus detected potential malware on critical server",
                "priority": "critical",
                "tags": ["malware", "server", "critical"],
                "context": {"hostname": "server-01", "threat_name": "Trojan.Generic"}
            },
            {
                "title": "Unusual Network Traffic Pattern",
                "description": "Detected abnormal data exfiltration patterns during off-hours",
                "priority": "medium",
                "tags": ["network", "exfiltration", "anomaly"],
                "context": {"traffic_volume": "500GB", "time_range": "02:00-04:00"}
            }
        ]
        
        for sample in sample_investigations:
            investigation_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            initial_entry = TimelineEntry(
                type="note",
                title="Investigation Created",
                content=f"Investigation '{sample['title']}' was created",
                user="system"
            )
            
            investigation_data = {
                "id": investigation_id,
                "title": sample["title"],
                "status": "open",
                "priority": sample["priority"],
                "created_by": "system",
                "created_at": now,
                "updated_at": now,
                "description": sample["description"],
                "tags": sample["tags"],
                "context": sample["context"],
                "timeline": [initial_entry.dict()]
            }
            
            investigations_store[investigation_id] = investigation_data
        
        logger.info(f"Initialized {len(sample_investigations)} sample investigations")

# Initialize sample data when module is imported
initialize_sample_investigations()

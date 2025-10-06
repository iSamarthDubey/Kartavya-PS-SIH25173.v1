"""
FastAPI Application for Conversational Assistant
Provides REST API endpoints for the SIEM NLP Assistant chatbot interface.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ASSISTANT_HOST = os.environ.get("ASSISTANT_HOST", "0.0.0.0")
try:
    ASSISTANT_PORT = int(os.environ.get("ASSISTANT_PORT", "8001"))
except ValueError:
    ASSISTANT_PORT = 8001

import assistant.security as security_module
from src.security.session_manager import Session

try:
    from .pipeline import ConversationalPipeline
    from .router import assistant_router
except ImportError:
    from assistant.pipeline import ConversationalPipeline
    from assistant.router import assistant_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global pipeline instance
pipeline: Optional[ConversationalPipeline] = None


def _refresh_security_context_if_env_changed() -> security_module.SecurityContext:
    """Rebuild the security context when environment-backed paths change."""

    target_store = Path(os.environ.get("ASSISTANT_USER_STORE", "config/security_users.json"))
    current_store = security_module.security_context.auth_manager.user_store_path

    def _normalize(path: Path) -> Path:
        try:
            return path.resolve(strict=False)
        except Exception:
            return path

    current_path = current_store if current_store else Path("config/security_users.json")

    if _normalize(current_path) != _normalize(target_store):
        security_module.security_context = security_module.SecurityContext.build_from_env()

    return security_module.security_context


security_context = _refresh_security_context_if_env_changed()
require_session = security_module.require_session
require_permission = security_module.require_permission
require_rate_limited_permission = security_module.require_rate_limited_permission


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    global pipeline

    logger.info("Starting SIEM NLP Conversational Assistant...")
    if pipeline is None:
        try:
            pipeline = ConversationalPipeline()
            await pipeline.initialize()
            logger.info("✅ Conversational Assistant initialized successfully!")
        except Exception as exc:
            logger.error("❌ Failed to initialize Conversational Assistant: %s", exc)

    try:
        yield
    finally:
        logger.info("Shutting down Conversational Assistant...")

# Initialize FastAPI app
app = FastAPI(
    title="SIEM NLP Conversational Assistant",
    description="Natural language interface for SIEM data analysis and querying",
    version="1.0.0",
    docs_url="/assistant/docs",
    redoc_url="/assistant/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],  # Streamlit and Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class QueryRequest(BaseModel):
    """Request model for conversational queries."""
    query: str = Field(..., description="Natural language query", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Additional user context")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional UI filters (e.g., time_range, severity)")
    limit: Optional[int] = Field(None, description="Max results to return (capped server-side)")
    offset: Optional[int] = Field(None, description="Pagination offset")
    force_intent: Optional[str] = Field(None, description="Override detected intent (advanced)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "Show me failed login attempts in the last hour",
                "conversation_id": "conv_12345",
                "user_context": {"user_role": "security_analyst"},
                "filters": {"time_range": "Last 24 hours", "severity": "High"},
                "limit": 100,
                "offset": 0,
                "force_intent": "show_failed_logins"
            }
        }
    )

class QueryResponse(BaseModel):
    """Response model for conversational queries."""
    conversation_id: str
    user_query: str
    intent: str
    entities: List[Dict[str, Any]]
    query_type: str
    siem_query: Dict[str, Any]  # Changed from str to Dict - Elasticsearch DSL query
    results: List[Dict[str, Any]]
    visualizations: List[Dict[str, Any]]
    summary: str
    metadata: Dict[str, Any]
    status: str
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    components: Dict[str, bool]
    health_score: str
    is_initialized: bool
    timestamp: str

class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history."""
    conversation_id: str
    history: List[Dict[str, Any]]
    total_messages: int


class LoginRequest(BaseModel):
    """Request payload for user login."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Response payload for successful login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    expires_at: str
    role: str


class RegisterRequest(BaseModel):
    """Request payload for registering a new user."""

    username: str
    password: str
    role: str


class SessionInfoResponse(BaseModel):
    """Details about the current authenticated session."""

    username: str
    role: str
    expires_at: str
    metadata: Dict[str, Any]

# Dependency to get pipeline instance
async def get_pipeline() -> ConversationalPipeline:
    """Dependency to get the initialized pipeline instance."""
    global pipeline
    if not pipeline:
        pipeline = ConversationalPipeline()
        await pipeline.initialize()
    return pipeline


@app.get("/health")
async def public_health_check() -> Dict[str, Any]:
    """Unauthenticated health check used by local tooling and the UI."""

    global pipeline

    is_ready = bool(pipeline and getattr(pipeline, "is_initialized", False))
    health_payload: Dict[str, Any] = {
        "status": "ok" if is_ready else "initializing",
        "is_initialized": is_ready,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if pipeline and hasattr(pipeline, "get_health_status"):
        try:
            detailed = pipeline.get_health_status()
            health_payload["components"] = detailed.get("components", {})
            health_payload["pipeline_status"] = detailed.get("status")
        except Exception as exc:  # pragma: no cover - best effort detail
            logger.debug("Detailed health status unavailable: %s", exc)

    return health_payload


@app.post("/assistant/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate a user and issue a bearer token."""

    username = request.username.strip()
    login_limit, login_window = security_context.login_rate
    security_context.enforce_rate_limit(
        key=f"login:{username}",
        limit=login_limit,
        window_seconds=login_window,
        detail="Too many login attempts. Please retry later.",
    )

    if not security_context.auth_manager.authenticate(username, request.password):
        security_context.audit_logger.log_event(username or "anonymous", "auth.login", "failed")
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = security_context.auth_manager.get_role(username)
    if not role:
        security_context.audit_logger.log_event(username, "auth.login", "failed", reason="role_missing")
        raise HTTPException(status_code=403, detail="User has no assigned role")

    session_record = security_context.create_session(username=username, role=role, metadata={"source": "api"})
    security_context.audit_logger.log_event(username, "auth.login", "success", role=role)

    return LoginResponse(
        access_token=session_record.token,
        expires_in=security_context.token_ttl,
        expires_at=session_record.expires_at.isoformat(),
        role=role,
    )


@app.post("/assistant/auth/logout")
async def logout(session: Session = Depends(require_session)):
    """Invalidate the caller's active session."""

    security_context.revoke_session(session.token)
    security_context.audit_logger.log_event(session.username, "auth.logout", "success")
    return {"message": "Logout successful"}


@app.post("/assistant/auth/register")
async def register_user(
    request: RegisterRequest,
    session: Session = Depends(require_permission("users:create")),
):
    """Create a new user account (admin-only)."""

    try:
        record = security_context.auth_manager.register_user(request.username, request.password, request.role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    security_context.audit_logger.log_event(
        session.username,
        "users.create",
        "success",
        target=record.username,
        role=record.role,
    )
    return {"message": f"User {record.username} created", "role": record.role}


@app.get("/assistant/auth/me", response_model=SessionInfoResponse)
async def current_session(session: Session = Depends(require_session)):
    """Return metadata about the active session."""

    return SessionInfoResponse(
        username=session.username,
        role=session.role,
        expires_at=session.expires_at.isoformat(),
        metadata=session.metadata,
    )

@app.get("/assistant/health", response_model=HealthResponse)
async def health_check(
    pipeline: ConversationalPipeline = Depends(get_pipeline),
    _session: Session = Depends(require_permission("audit:view")),
):
    """
    Check the health status of the conversational assistant pipeline.
    Returns status of all components and overall health score.
    """
    try:
        health_status = pipeline.get_health_status()
        return HealthResponse(
            status=health_status['status'],
            components=health_status['components'],
            health_score=health_status['health_score'],
            is_initialized=health_status['is_initialized'],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/assistant/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    session: Session = Depends(require_rate_limited_permission("queries:run")),
    pipeline: ConversationalPipeline = Depends(get_pipeline),
):
    """
    Process a natural language query through the conversational assistant pipeline.
    
    This endpoint:
    1. Analyzes the natural language input
    2. Generates appropriate SIEM queries
    3. Executes queries against available SIEM platforms
    4. Formats and summarizes the results
    5. Updates conversation context
    """
    try:
        logger.info(f"Processing query for user=%s", session.username)

        sanitized_query = security_context.sanitize_or_reject(request.query, session.username)

        merged_context = {"actor": session.username, "role": session.role}
        if request.user_context:
            merged_context.update(request.user_context)
        # Include filters and pagination/control hints
        if request.filters:
            merged_context.update({"filters": request.filters})
        if request.limit is not None:
            merged_context["limit"] = int(request.limit)
        if request.offset is not None:
            merged_context["offset"] = int(request.offset)
        if request.force_intent:
            merged_context["force_intent"] = request.force_intent

        result = await pipeline.process_query(
            user_input=sanitized_query,
            conversation_id=request.conversation_id,
            user_context=merged_context,
        )
        
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
        result.setdefault('metadata', {})
        result['metadata'].update({
            'original_query': request.query,
            'sanitized_query': sanitized_query,
            'actor': session.username,
        })

        security_context.audit_logger.log_event(
            session.username,
            "query.submit",
            "success",
            conversation_id=result.get('conversation_id', request.conversation_id or ''),
        )

        return QueryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        security_context.audit_logger.log_event(
            session.username,
            "query.submit",
            "failed",
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/assistant/conversation/{conversation_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    pipeline: ConversationalPipeline = Depends(get_pipeline),
    _session: Session = Depends(require_permission("queries:run")),
):
    """
    Retrieve the conversation history for a given conversation ID.
    Useful for maintaining context across multiple queries.
    """
    try:
        history = await pipeline.get_conversation_history(conversation_id)
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            history=history,
            total_messages=len(history)
        )
    except Exception as e:
        logger.error(f"Failed to retrieve conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation history: {str(e)}")

@app.delete("/assistant/conversation/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    pipeline: ConversationalPipeline = Depends(get_pipeline),
    session: Session = Depends(require_permission("cases:update")),
):
    """
    Clear the conversation history for a given conversation ID.
    """
    try:
        # This would need to be implemented in the context manager
        if hasattr(pipeline.context_manager, 'clear_conversation'):
            await pipeline.context_manager.clear_conversation(conversation_id)
            security_context.audit_logger.log_event(
                session.username,
                "conversation.clear",
                "success",
                conversation_id=conversation_id,
            )
        
        return {"message": f"Conversation {conversation_id} cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear conversation: {e}")
        security_context.audit_logger.log_event(
            session.username,
            "conversation.clear",
            "failed",
            conversation_id=conversation_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation: {str(e)}")

@app.get("/assistant/ping")
async def ping():
    """Unauthenticated liveness endpoint for orchestration and health checks."""
    return {
        "service": "SIEM NLP Conversational Assistant",
        "status": "ok",
        "version": "1.0.0"
    }


@app.get("/assistant/")
async def root():
    """Root endpoint for the conversational assistant."""
    return {
        "message": "SIEM NLP Conversational Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "ping": "/assistant/ping",
            "health": "/assistant/health",
            "ask": "/assistant/ask",
            "history": "/assistant/conversation/{conversation_id}/history",
            "docs": "/assistant/docs"
        }
    }

# Include the router for additional endpoints
app.include_router(
    assistant_router,
    prefix="/assistant",
    dependencies=[Depends(require_session)],
)

if __name__ == "__main__":
    import uvicorn

    logger.info(
        "Launching assistant API on %s:%s (override with ASSISTANT_HOST / ASSISTANT_PORT)",
        ASSISTANT_HOST,
        ASSISTANT_PORT,
    )

    uvicorn.run(
        app,  # Pass app directly instead of string
        host=ASSISTANT_HOST,
        port=ASSISTANT_PORT,
        reload=False,  # Disable reload for stability
        log_level="info"
    )
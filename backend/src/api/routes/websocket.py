"""
WebSocket Routes for Real-time Chat
Handles streaming chat responses and live updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import Dict, List, Any, Optional
import json
import logging
import asyncio
from datetime import datetime
import uuid

from ...core.pipeline import ConversationalPipeline
from ...connectors.base import BaseSIEMConnector
from ...core.context.manager import ContextManager
from ...core.nlp.schema_mapper import SchemaMapper

logger = logging.getLogger(__name__)
router = APIRouter()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, str] = {}  # session_id -> user_id
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept WebSocket connection and store it"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")
        
        # Send connection confirmation
        await self.send_message(session_id, {
            "type": "connection_established",
            "data": {"session_id": session_id},
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.user_sessions:
            del self.user_sessions[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to specific WebSocket connection"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Failed to send WebSocket message to {session_id}: {e}")
                self.disconnect(session_id)
                return False
        return False
    
    async def broadcast(self, message: Dict[str, Any], exclude_session: Optional[str] = None):
        """Broadcast message to all connected clients"""
        disconnected = []
        for session_id, websocket in self.active_connections.items():
            if session_id == exclude_session:
                continue
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to broadcast to {session_id}: {e}")
                disconnected.append(session_id)
        
        # Clean up disconnected clients
        for session_id in disconnected:
            self.disconnect(session_id)

# Global connection manager
connection_manager = ConnectionManager()

@router.websocket("/ws/chat")
async def websocket_chat_simple(
    websocket: WebSocket
):
    """
    Simple WebSocket endpoint without session_id requirement
    Auto-generates session_id for compatibility
    """
    # Generate a session ID automatically
    session_id = f"auto_{uuid.uuid4().hex[:8]}"
    await websocket_chat_endpoint_impl(websocket, session_id)

@router.websocket("/ws/chat/{session_id}")
async def websocket_chat_with_session(
    websocket: WebSocket,
    session_id: str
):
    """
    WebSocket endpoint with explicit session_id
    """
    await websocket_chat_endpoint_impl(websocket, session_id)

async def websocket_chat_endpoint_impl(
    websocket: WebSocket,
    session_id: str
):
    """
    WebSocket endpoint for real-time chat communication
    Supports streaming responses and live updates
    """
    await connection_manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received WebSocket message from {session_id}: {message.get('type', 'unknown')}")
            
            # Handle different message types
            if message.get("type") == "chat_message":
                await handle_chat_message(session_id, message)
            elif message.get("type") == "ping":
                await handle_ping(session_id)
            elif message.get("type") == "typing":
                await handle_typing_indicator(session_id, message)
            else:
                logger.warning(f"Unknown WebSocket message type: {message.get('type')}")
                
    except WebSocketDisconnect:
        connection_manager.disconnect(session_id)
        logger.info(f"WebSocket client {session_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        connection_manager.disconnect(session_id)

async def handle_chat_message(session_id: str, message: Dict[str, Any]):
    """Handle incoming chat message and process through pipeline"""
    try:
        # Extract query data
        query = message.get("data", {}).get("query", "")
        conversation_id = message.get("data", {}).get("conversation_id", session_id)
        context = message.get("data", {}).get("context", {})
        
        if not query:
            await connection_manager.send_message(session_id, {
                "type": "error",
                "data": {"message": "Empty query received"},
                "timestamp": datetime.now().isoformat()
            })
            return
        
        logger.info(f"Processing chat query from {session_id}: {query[:100]}...")
        
        # Send acknowledgment that we're processing
        await connection_manager.send_message(session_id, {
            "type": "processing_started",
            "data": {
                "query": query,
                "conversation_id": conversation_id,
                "message_id": str(uuid.uuid4())
            },
            "timestamp": datetime.now().isoformat()
        })
        
        # Import dependencies (avoid circular imports)
        from ...api.main import get_pipeline, get_siem_connector, get_context_manager, get_schema_mapper
        
        # Get pipeline components
        pipeline = get_pipeline()
        siem_connector = get_siem_connector()
        context_manager = get_context_manager()
        schema_mapper = get_schema_mapper()
        
        # Get conversation context
        conv_context = await context_manager.get_context(conversation_id)
        
        # Process through pipeline with streaming
        await process_query_with_streaming(
            session_id=session_id,
            query=query,
            conversation_id=conversation_id,
            context=conv_context,
            pipeline=pipeline,
            siem_connector=siem_connector,
            schema_mapper=schema_mapper
        )
        
    except Exception as e:
        logger.error(f"Error handling chat message from {session_id}: {e}")
        await connection_manager.send_message(session_id, {
            "type": "error", 
            "data": {
                "message": f"Failed to process query: {str(e)}",
                "query": message.get("data", {}).get("query", "")
            },
            "timestamp": datetime.now().isoformat()
        })

async def process_query_with_streaming(
    session_id: str,
    query: str,
    conversation_id: str,
    context: Any,
    pipeline: ConversationalPipeline,
    siem_connector: BaseSIEMConnector,
    schema_mapper: SchemaMapper
):
    """Process query through pipeline with streaming responses"""
    message_id = str(uuid.uuid4())
    
    try:
        # Step 1: Send processing status
        await connection_manager.send_message(session_id, {
            "type": "chat_response",
            "data": {
                "id": message_id,
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": "🔍 Analyzing your query...",
                "status": "processing",
                "stage": "nlp_processing"
            },
            "timestamp": datetime.now().isoformat()
        })
        
        # Step 2: Process through NLP pipeline
        result = await pipeline.process(
            query=query,
            context=context,
            user_context={},
            filters={}
        )
        
        if result.get("error"):
            raise Exception(result["error"])
        
        # Step 3: Send NLP results
        await connection_manager.send_message(session_id, {
            "type": "chat_response",
            "data": {
                "id": message_id,
                "conversation_id": conversation_id,
                "role": "assistant", 
                "content": f"✅ Intent: {result.get('intent', 'unknown')} (confidence: {result.get('confidence', 0):.2f})",
                "status": "processing",
                "stage": "query_building",
                "metadata": {
                    "intent": result.get('intent'),
                    "confidence": result.get('confidence'),
                    "entities": result.get('entities', [])
                }
            },
            "timestamp": datetime.now().isoformat()
        })
        
        # Step 4: Build and execute query
        if result.get("siem_query"):
            await connection_manager.send_message(session_id, {
                "type": "chat_response",
                "data": {
                    "id": message_id,
                    "conversation_id": conversation_id,
                    "role": "assistant",
                    "content": "🔎 Searching SIEM data...",
                    "status": "processing",
                    "stage": "siem_query"
                },
                "timestamp": datetime.now().isoformat()
            })
            
            # Execute SIEM query
            search_results = await siem_connector.execute_query(
                query=result["siem_query"],
                size=100
            )
            
            # Format results
            formatted_results = await pipeline.format_results(
                results=search_results,
                query_type=result.get("intent", "unknown")
            )
            
            # Generate summary
            summary = await pipeline.generate_summary(
                results=formatted_results,
                query=query,
                intent=result.get("intent", "unknown")
            )
            
            # Step 5: Send final results
            await connection_manager.send_message(session_id, {
                "type": "chat_response",
                "data": {
                    "id": message_id,
                    "conversation_id": conversation_id,
                    "role": "assistant",
                    "content": summary,
                    "status": "success",
                    "stage": "complete",
                    "metadata": {
                        "intent": result.get('intent'),
                        "confidence": result.get('confidence'),
                        "entities": result.get('entities', []),
                        "results_count": len(formatted_results),
                        "processing_time": result.get('processing_time', 0)
                    },
                    "visual_payload": {
                        "type": "composite",
                        "cards": await generate_visual_cards(formatted_results, result.get("intent"))
                    } if formatted_results else None
                },
                "timestamp": datetime.now().isoformat()
            })
            
        else:
            # No query generated - clarification needed
            await connection_manager.send_message(session_id, {
                "type": "chat_response",
                "data": {
                    "id": message_id,
                    "conversation_id": conversation_id,
                    "role": "assistant",
                    "content": "I need more information to help you. Could you please clarify your request?",
                    "status": "clarification_needed",
                    "stage": "complete"
                },
                "timestamp": datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"Error processing query with streaming: {e}")
        await connection_manager.send_message(session_id, {
            "type": "chat_response",
            "data": {
                "id": message_id,
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": f"I encountered an error processing your request: {str(e)}",
                "status": "error",
                "stage": "error"
            },
            "timestamp": datetime.now().isoformat()
        })

async def generate_visual_cards(results: List[Dict], intent: str) -> List[Dict]:
    """Generate visual cards for results"""
    cards = []
    
    if not results:
        return cards
    
    # Summary card
    cards.append({
        "type": "summary_card",
        "title": f"Results Found",
        "value": len(results)
    })
    
    # Sample data for chart if we have numeric data
    if len(results) > 1 and intent in ["failed_login", "malware", "network"]:
        # Create time series data
        time_data = []
        for i, result in enumerate(results[:10]):  # Limit to 10 points
            time_data.append({
                "x": result.get("@timestamp", f"Point {i+1}"),
                "y": 1
            })
        
        cards.append({
            "type": "chart",
            "chart_type": "line",
            "title": f"{intent.replace('_', ' ').title()} Over Time",
            "data": time_data
        })
    
    # Table card with first few results
    if results:
        table_columns = [
            {"key": "timestamp", "label": "Time"},
            {"key": "message", "label": "Message"},
            {"key": "source", "label": "Source"}
        ]
        
        table_rows = []
        for result in results[:5]:  # First 5 results
            table_rows.append([
                result.get("@timestamp", "Unknown"),
                result.get("message", result.get("event", {}).get("action", "No message")),
                result.get("host", {}).get("name", result.get("source", {}).get("ip", "Unknown"))
            ])
        
        cards.append({
            "type": "table",
            "title": "Recent Events",
            "columns": table_columns,
            "rows": table_rows
        })
    
    return cards

async def handle_ping(session_id: str):
    """Handle ping message - respond with pong"""
    await connection_manager.send_message(session_id, {
        "type": "pong",
        "data": {},
        "timestamp": datetime.now().isoformat()
    })

async def handle_typing_indicator(session_id: str, message: Dict[str, Any]):
    """Handle typing indicator - broadcast to other users if needed"""
    # For now, just acknowledge
    await connection_manager.send_message(session_id, {
        "type": "typing_ack",
        "data": {"typing": message.get("data", {}).get("typing", False)},
        "timestamp": datetime.now().isoformat()
    })

# Health check for WebSocket
@router.get("/ws/health")
async def websocket_health():
    """WebSocket health check endpoint"""
    return {
        "status": "healthy",
        "active_connections": len(connection_manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }

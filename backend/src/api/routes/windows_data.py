"""
Simple Windows data endpoint for dashboard
Bypasses complex query builders and provides direct Elasticsearch access
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from elasticsearch import Elasticsearch
import os
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/windows", tags=["Windows Data"])


def get_elasticsearch_client():
    """Get Elasticsearch client"""
    try:
        host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
        port = int(os.getenv('ELASTICSEARCH_PORT', 9200))
        
        client = Elasticsearch(
            [f'http://{host}:{port}'],
            request_timeout=10,
            max_retries=2,
            retry_on_timeout=True,
            headers={'Accept': 'application/json'}
        )
        
        if not client.ping():
            raise Exception("Cannot connect to Elasticsearch")
        
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        raise HTTPException(status_code=503, detail="Elasticsearch unavailable")


@router.get("/dashboard-summary")
async def get_dashboard_summary(client: Elasticsearch = Depends(get_elasticsearch_client)):
    """Get Windows dashboard summary with real data"""
    try:
        # Get recent events count
        recent_events_query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {"gte": "now-1h"}}},
                        {"match": {"beat.name": "winlogbeat"}}
                    ]
                }
            }
        }
        
        # Get system metrics
        system_metrics_query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {"gte": "now-5m"}}},
                        {"match": {"beat.name": "metricbeat"}},
                        {"exists": {"field": "system.cpu.total.pct"}}
                    ]
                }
            },
            "size": 1,
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        # Execute queries
        events_result = client.search(
            index=".ds-winlogbeat-*",
            body=recent_events_query,
            size=0  # Count only
        )
        
        metrics_result = client.search(
            index=".ds-metricbeat-*", 
            body=system_metrics_query
        )
        
        # Extract data
        recent_events_count = events_result['hits']['total']['value']
        
        system_data = {}
        if metrics_result['hits']['hits']:
            source = metrics_result['hits']['hits'][0]['_source']
            system_data = {
                'cpu_percent': round(source.get('system', {}).get('cpu', {}).get('total', {}).get('pct', 0) * 100, 1),
                'memory_percent': round(source.get('system', {}).get('memory', {}).get('used', {}).get('pct', 0) * 100, 1),
                'hostname': source.get('host', {}).get('name', 'Unknown')
            }
        
        return {
            "success": True,
            "data": {
                "summary_cards": [
                    {
                        "title": "Recent Events",
                        "value": recent_events_count,
                        "change": {"value": 0, "trend": "stable", "period": "last hour"},
                        "status": "normal",
                        "color": "primary"
                    },
                    {
                        "title": "CPU Usage", 
                        "value": f"{system_data.get('cpu_percent', 0)}%",
                        "change": {"value": 0, "trend": "stable", "period": "current"},
                        "status": "normal" if system_data.get('cpu_percent', 0) < 80 else "warning",
                        "color": "accent"
                    },
                    {
                        "title": "Memory Usage",
                        "value": f"{system_data.get('memory_percent', 0)}%", 
                        "change": {"value": 0, "trend": "stable", "period": "current"},
                        "status": "normal" if system_data.get('memory_percent', 0) < 80 else "warning",
                        "color": "primary"
                    },
                    {
                        "title": "System Host",
                        "value": system_data.get('hostname', 'Unknown'),
                        "change": {"value": 0, "trend": "stable", "period": "current"}, 
                        "status": "normal",
                        "color": "primary"
                    }
                ],
                "system_health": {
                    "health_score": "excellent" if system_data.get('cpu_percent', 0) < 50 else "good",
                    "services": {
                        "elasticsearch": True,
                        "winlogbeat": True,
                        "metricbeat": True
                    }
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Dashboard summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-events")
async def get_recent_events(
    limit: int = 10,
    client: Elasticsearch = Depends(get_elasticsearch_client)
):
    """Get recent Windows events"""
    try:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {"gte": "now-1h"}}},
                        {"match": {"beat.name": "winlogbeat"}}
                    ]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": limit
        }
        
        result = client.search(index=".ds-winlogbeat-*", body=query)
        
        events = []
        for hit in result['hits']['hits']:
            source = hit['_source']
            events.append({
                "timestamp": source.get('@timestamp'),
                "event_id": source.get('event', {}).get('code', 'Unknown'),
                "message": source.get('message', 'Windows event'),
                "host": source.get('host', {}).get('name', 'Unknown'),
                "source": source
            })
        
        return {
            "success": True,
            "data": {
                "events": events,
                "total": result['hits']['total']['value']
            }
        }
        
    except Exception as e:
        logger.error(f"Recent events query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-metrics")
async def get_system_metrics(
    time_range: str = "1h",
    client: Elasticsearch = Depends(get_elasticsearch_client)
):
    """Get Windows system metrics over time"""
    try:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {"gte": f"now-{time_range}"}}},
                        {"match": {"beat.name": "metricbeat"}},
                        {"exists": {"field": "system.cpu.total.pct"}}
                    ]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": 100
        }
        
        result = client.search(index=".ds-metricbeat-*", body=query)
        
        metrics = []
        for hit in result['hits']['hits']:
            source = hit['_source']
            metrics.append({
                "timestamp": source.get('@timestamp'),
                "cpu_percent": round(source.get('system', {}).get('cpu', {}).get('total', {}).get('pct', 0) * 100, 1),
                "memory_percent": round(source.get('system', {}).get('memory', {}).get('used', {}).get('pct', 0) * 100, 1),
                "host": source.get('host', {}).get('name', 'Unknown')
            })
        
        return {
            "success": True,
            "data": {
                "metrics": metrics,
                "total": result['hits']['total']['value']
            }
        }
        
    except Exception as e:
        logger.error(f"System metrics query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simple-chat")
async def simple_chat(
    request: Dict[str, Any],
    client: Elasticsearch = Depends(get_elasticsearch_client)
):
    """Simple chat interface that works with real data"""
    try:
        query_text = request.get("query", "").lower()
        
        # Simple keyword-based routing
        if "event" in query_text or "log" in query_text or "recent" in query_text:
            # Get recent events
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"range": {"@timestamp": {"gte": "now-1h"}}},
                            {"match": {"beat.name": "winlogbeat"}}
                        ]
                    }
                },
                "sort": [{"@timestamp": {"order": "desc"}}],
                "size": 5
            }
            
            result = client.search(index=".ds-winlogbeat-*", body=query)
            
            events = []
            for hit in result['hits']['hits']:
                source = hit['_source']
                events.append({
                    "timestamp": source.get('@timestamp'),
                    "message": source.get('message', 'Windows event'),
                    "host": source.get('host', {}).get('name', 'Unknown')
                })
            
            return {
                "conversation_id": "simple-chat",
                "query": query_text,
                "intent": "show_events",
                "confidence": 0.9,
                "entities": [],
                "siem_query": query,
                "results": {"events": events},
                "summary": f"Found {len(events)} recent Windows events from your system.",
                "visualizations": [],
                "suggestions": ["Show me system metrics", "What are the latest hardware events?"],
                "metadata": {"timestamp": "2025-10-11T16:20:00Z"},
                "status": "success"
            }
            
        elif "cpu" in query_text or "memory" in query_text or "metric" in query_text or "system" in query_text:
            # Get system metrics
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"range": {"@timestamp": {"gte": "now-5m"}}},
                            {"match": {"beat.name": "metricbeat"}},
                            {"exists": {"field": "system.cpu.total.pct"}}
                        ]
                    }
                },
                "sort": [{"@timestamp": {"order": "desc"}}],
                "size": 1
            }
            
            result = client.search(index=".ds-metricbeat-*", body=query)
            
            if result['hits']['hits']:
                source = result['hits']['hits'][0]['_source']
                cpu = round(source.get('system', {}).get('cpu', {}).get('total', {}).get('pct', 0) * 100, 1)
                memory = round(source.get('system', {}).get('memory', {}).get('used', {}).get('pct', 0) * 100, 1)
                host = source.get('host', {}).get('name', 'Unknown')
                
                return {
                    "conversation_id": "simple-chat",
                    "query": query_text,
                    "intent": "show_metrics",
                    "confidence": 0.9,
                    "entities": [],
                    "siem_query": query,
                    "results": {"cpu": cpu, "memory": memory, "host": host},
                    "summary": f"Current system metrics for {host}: CPU {cpu}%, Memory {memory}%",
                    "visualizations": [],
                    "suggestions": ["Show me recent events", "What hardware issues occurred today?"],
                    "metadata": {"timestamp": "2025-10-11T16:20:00Z"},
                    "status": "success"
                }
        
        # Default fallback
        return {
            "conversation_id": "simple-chat",
            "query": query_text,
            "intent": "general",
            "confidence": 0.5,
            "entities": [],
            "siem_query": {},
            "results": {},
            "summary": "I can help you with Windows events and system metrics. Try asking about 'recent events' or 'system metrics'.",
            "visualizations": [],
            "suggestions": ["Show me recent Windows events", "What are the current system metrics?"],
            "metadata": {"timestamp": "2025-10-11T16:20:00Z"},
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Simple chat failed: {e}")
        return {
            "conversation_id": "error",
            "query": request.get("query", ""),
            "intent": "error",
            "confidence": 0.0,
            "entities": [],
            "siem_query": {},
            "results": {},
            "summary": f"Sorry, there was an error: {str(e)}",
            "visualizations": [],
            "suggestions": [],
            "metadata": {"timestamp": "2025-10-11T16:20:00Z"},
            "status": "error",
            "error": str(e)
        }

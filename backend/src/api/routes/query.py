
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
	query: str
	params: Dict[str, Any] = {}
	context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
	success: bool
	data: Any = None
	error: str = ""
	metadata: Optional[Dict[str, Any]] = None


@router.post("/execute", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
	"""
	Execute a SIEM query using the complete pipeline with proper formatting
	"""
	try:
		# Import dependencies from main app
		from ..main import get_pipeline, get_siem_connector
		pipeline = get_pipeline()
		siem_connector = get_siem_connector()

		# Process the query through the pipeline
		result = await pipeline.process(query=request.query)

		# If query is invalid, return error
		if not result.get("query_valid", False):
			return QueryResponse(
				success=False, 
				error=result.get("validation_error", "Query invalid"),
				metadata={"query": request.query}
			)

		# Execute the SIEM query using the connector
		siem_query = result.get("siem_query", {})
		intent = result.get("intent", "general")
		entities = result.get("entities", [])
		
		# Get raw results from connector
		raw_results = await siem_connector.execute_query(
			query=siem_query, 
			size=request.params.get("size", 100)
		)

		# Format results for frontend consumption
		formatted_results = await pipeline.format_results(raw_results, intent)
		
		# Generate human-readable summary
		summary = await pipeline.generate_summary(formatted_results, request.query, intent)
		
		# Create visualizations
		visualizations = await pipeline.create_visualizations(formatted_results, intent)
		
		# Generate follow-up suggestions
		suggestions = await pipeline.generate_suggestions(
			request.query, 
			formatted_results, 
			request.context
		)

		# Prepare comprehensive response
		response_data = {
			"query": request.query,
			"intent": intent,
			"entities": entities,
			"summary": summary,
			"results": formatted_results,
			"visualizations": visualizations,
			"suggestions": suggestions,
			"total_count": len(formatted_results),
			"query_performance": {
				"execution_time_ms": result.get("execution_time_ms", 0),
				"data_sources": ["dataset"]  # Could be extended to include Elasticsearch, Wazuh etc.
			}
		}
		
		metadata = {
			"timestamp": result.get("timestamp"),
			"session_id": request.params.get("session_id"),
			"siem_query": siem_query  # For debugging purposes
		}

		return QueryResponse(
			success=True, 
			data=response_data,
			metadata=metadata
		)
		
	except Exception as e:
		logger.error(f"Query execution failed: {str(e)}")
		return QueryResponse(
			success=False, 
			error=f"Query execution failed: {str(e)}",
			metadata={"query": request.query}
		)

@router.post("/translate", response_model=QueryResponse)
async def translate_query(request: QueryRequest):
	"""
	Translate natural language query to SIEM query using NLP pipeline
	"""
	try:
		from ..main import get_pipeline
		pipeline = get_pipeline()
		
		# Process query to get intent and entities
		result = await pipeline.process(query=request.query)
		
		if not result.get("query_valid", False):
			return QueryResponse(
				success=False, 
				error=result.get("validation_error", "Query could not be translated")
			)
		
		translation_data = {
			"original_query": request.query,
			"intent": result.get("intent"),
			"entities": result.get("entities"),
			"siem_query": result.get("siem_query"),
			"confidence": result.get("confidence", 0.8)
		}
		
		return QueryResponse(success=True, data=translation_data)
		
	except Exception as e:
		logger.error(f"Query translation failed: {str(e)}")
		return QueryResponse(success=False, error=f"Translation failed: {str(e)}")


@router.get("/suggestions", response_model=QueryResponse)
async def get_suggestions():
	"""
	Provide intelligent query suggestions based on common SIEM use cases
	"""
	try:
		# Comprehensive suggestion categories
		suggestions = {
			"security_events": [
				"Show failed login attempts from the last hour",
				"Find malware alerts from today",
				"Show high severity security events",
				"Display network intrusion attempts",
				"Find suspicious file downloads"
			],
			"user_activity": [
				"Show user login activity for today",
				"Find privileged user actions",
				"Display after-hours access attempts",
				"Show account lockout events"
			],
			"network_analysis": [
				"Analyze network traffic patterns",
				"Show blocked connection attempts",
				"Find port scan attempts",
				"Display bandwidth anomalies"
			],
			"system_monitoring": [
				"Show system performance metrics",
				"Find system uptime statistics",
				"Display resource utilization trends",
				"Show system error events"
			]
		}
		
		return QueryResponse(success=True, data=suggestions)
		
	except Exception as e:
		logger.error(f"Failed to get suggestions: {str(e)}")
		return QueryResponse(success=False, error="Failed to retrieve suggestions")


@router.post("/optimize", response_model=QueryResponse)
async def optimize_query(request: QueryRequest):
	"""
	Optimize query for better performance and more relevant results
	"""
	try:
		from ..main import get_pipeline
		pipeline = get_pipeline()
		
		# Process original query
		result = await pipeline.process(query=request.query)
		
		if not result.get("query_valid", False):
			return QueryResponse(
				success=False, 
				error="Cannot optimize invalid query"
			)
		
		# Generate optimization suggestions
		optimizations = []
		original_query = request.query.lower()
		
		# Add time range if missing
		if not any(time_word in original_query for time_word in ['hour', 'day', 'week', 'minute', 'today', 'yesterday']):
			optimizations.append("Consider adding a time range (e.g., 'from last 24 hours')")
		
		# Add severity filter suggestion
		if 'severity' not in original_query and 'critical' not in original_query:
			optimizations.append("Consider filtering by severity level for focused results")
		
		# Suggest more specific terms
		if len(original_query.split()) < 3:
			optimizations.append("Try using more specific keywords for better results")
		
		# Generate optimized query suggestion
		intent = result.get("intent", "")
		entities = result.get("entities", [])
		
		optimized_suggestion = request.query
		if intent == "failed_login":
			optimized_suggestion += " with high severity from last 24 hours"
		elif intent == "malware":
			optimized_suggestion += " detected in the last 6 hours"
		elif intent == "network":
			optimized_suggestion += " showing blocked connections"
		
		optimization_data = {
			"original_query": request.query,
			"optimized_query": optimized_suggestion,
			"suggestions": optimizations,
			"performance_tips": [
				"Limit time ranges for faster queries",
				"Use specific field filters when possible",
				"Consider using wildcards (*) for broader matches"
			],
			"estimated_improvement": "20-40% faster execution" if optimizations else "Query already well optimized"
		}
		
		return QueryResponse(success=True, data=optimization_data)
		
	except Exception as e:
		logger.error(f"Query optimization failed: {str(e)}")
		return QueryResponse(success=False, error=f"Optimization failed: {str(e)}")

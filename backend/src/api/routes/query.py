
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter()

class QueryRequest(BaseModel):
	query: str
	params: Dict[str, Any] = {}

class QueryResponse(BaseModel):
	success: bool
	data: Any = None
	error: str = ""


@router.post("/execute", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
	"""
	Execute a SIEM query using the real pipeline and connector
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
			return QueryResponse(success=False, error=result.get("validation_error", "Query invalid"))

		# Execute the SIEM query using the connector
		siem_query = result.get("siem_query", {})
		search_results = await siem_connector.execute_query(query=siem_query, size=request.params.get("size", 100))

		return QueryResponse(success=True, data={
			"query": request.query,
			"intent": result.get("intent"),
			"entities": result.get("entities"),
			"siem_query": siem_query,
			"results": search_results
		})
	except Exception as e:
		return QueryResponse(success=False, error=str(e))

@router.post("/translate", response_model=QueryResponse)
async def translate_query(request: QueryRequest):
	# TODO: Integrate with NLP pipeline
	return QueryResponse(success=True, data={"translated_query": f"Translated: {request.query}"})

@router.get("/suggestions", response_model=QueryResponse)
async def get_suggestions():
	# TODO: Provide real suggestions
	return QueryResponse(success=True, data=["Show failed logins", "Find malware alerts"])

@router.post("/optimize", response_model=QueryResponse)
async def optimize_query(request: QueryRequest):
	# TODO: Integrate with query optimizer
	return QueryResponse(success=True, data={"optimized_query": f"Optimized: {request.query}"})

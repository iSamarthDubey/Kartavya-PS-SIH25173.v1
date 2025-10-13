"""
Query commands for SIEM query execution and optimization
Interfaces with the Kartavya query processing API endpoints
"""

from typing import Optional, Dict, Any
import typer
import json

from ..core.client import get_client, run_async, APIError, make_request_with_spinner
from ..core.output import print_output, print_error, print_success, print_info

app = typer.Typer(help="🔎 Execute and optimize SIEM queries")


@app.command("execute")
def execute_query(
    query: str = typer.Argument(..., help="Natural language or SIEM query to execute"),
    params: Optional[str] = typer.Option(None, "--params", "-p", help="JSON parameters for query"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="JSON context for query"),
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Session ID for context"),
    size: int = typer.Option(100, "--size", help="Maximum number of results to return"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)"),
    save_results: Optional[str] = typer.Option(None, "--save", help="Save results to file"),
):
    """Execute a SIEM query using the NLP pipeline"""
    
    async def run_query():
        # Parse parameters if provided
        query_params = {"size": size}
        if params:
            try:
                additional_params = json.loads(params)
                query_params.update(additional_params)
            except json.JSONDecodeError:
                print_error("Invalid JSON in parameters")
                return
        
        # Parse context if provided
        query_context = {}
        if context:
            try:
                query_context = json.loads(context)
            except json.JSONDecodeError:
                print_error("Invalid JSON in context")
                return
        
        # Add session ID to context if provided
        if session_id:
            query_context["session_id"] = session_id
        
        request_data = {
            "query": query,
            "params": query_params,
            "context": query_context or None
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/query/execute",
                    data=request_data,
                    description=f"Executing query: {query[:50]}..."
                )
                
                if save_results:
                    # Save results to file
                    try:
                        with open(save_results, 'w', encoding='utf-8') as f:
                            if output_format == "json" or save_results.endswith('.json'):
                                json.dump(response, f, indent=2)
                            elif save_results.endswith('.csv'):
                                # Extract results for CSV
                                results = response.get('data', {}).get('results', [])
                                if results:
                                    import csv
                                    if isinstance(results[0], dict):
                                        fieldnames = results[0].keys()
                                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                                        writer.writeheader()
                                        writer.writerows(results)
                                    else:
                                        writer = csv.writer(f)
                                        for result in results:
                                            writer.writerow([result])
                            else:
                                f.write(str(response.get('data', response)))
                        
                        print_success(f"Query results saved to {save_results}")
                    except Exception as e:
                        print_error(f"Failed to save results: {e}")
                
                print_output(response, f"Query Results: {query}", output_format)
                
            except APIError as e:
                print_error(f"Query execution failed: {e}")
    
    run_async(run_query())


@app.command("translate")
def translate_query(
    query: str = typer.Argument(..., help="Natural language query to translate"),
    target_format: Optional[str] = typer.Option(None, "--format", "-f", help="Target query format"),
    show_confidence: bool = typer.Option(True, "--confidence/--no-confidence", help="Show confidence scores"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)"),
):
    """Translate natural language to SIEM query"""
    
    async def translate():
        request_data = {
            "query": query,
            "params": {
                "target_format": target_format,
                "include_confidence": show_confidence
            }
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/query/translate",
                    data=request_data,
                    description=f"Translating query: {query[:50]}..."
                )
                
                print_output(response, "Query Translation", output_format)
                
                # Show translation summary
                if response.get('success') and not output_format:
                    data = response.get('data', {})
                    print_info(f"Intent: {data.get('intent', 'Unknown')}")
                    print_info(f"Confidence: {data.get('confidence', 0):.2%}")
                    print_info(f"Entities found: {len(data.get('entities', []))}")
                
            except APIError as e:
                print_error(f"Query translation failed: {e}")
    
    run_async(translate())


@app.command("suggestions")
def get_suggestions(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Suggestion category"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of suggestions to show"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format"),
):
    """Get intelligent query suggestions"""
    
    async def fetch_suggestions():
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "GET",
                    "/api/query/suggestions",
                    description="Getting query suggestions..."
                )
                
                # Filter by category if specified
                if category:
                    suggestions_data = response.get('data', {})
                    if category in suggestions_data:
                        filtered_suggestions = suggestions_data[category][:limit]
                        filtered_response = {
                            "success": True,
                            "data": {category: filtered_suggestions},
                            "total": len(filtered_suggestions)
                        }
                        print_output(filtered_response, f"Query Suggestions - {category.title()}", output_format)
                    else:
                        available_categories = list(suggestions_data.keys())
                        print_error(f"Category '{category}' not found. Available: {', '.join(available_categories)}")
                else:
                    # Show all categories, limited per category
                    if limit and response.get('data'):
                        limited_data = {}
                        for cat, suggestions in response['data'].items():
                            limited_data[cat] = suggestions[:limit]
                        response['data'] = limited_data
                    
                    print_output(response, "Query Suggestions", output_format)
                
            except APIError as e:
                print_error(f"Failed to get suggestions: {e}")
    
    run_async(fetch_suggestions())


@app.command("optimize")
def optimize_query(
    query: str = typer.Argument(..., help="Query to optimize"),
    show_tips: bool = typer.Option(True, "--tips/--no-tips", help="Show optimization tips"),
    apply_optimization: bool = typer.Option(False, "--apply", help="Apply suggested optimizations"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format"),
):
    """Optimize query for better performance"""
    
    async def optimize():
        request_data = {
            "query": query,
            "params": {
                "include_tips": show_tips,
                "auto_apply": apply_optimization
            }
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/query/optimize",
                    data=request_data,
                    description=f"Optimizing query: {query[:50]}..."
                )
                
                print_output(response, "Query Optimization", output_format)
                
                # Show optimization summary
                if response.get('success') and not output_format:
                    data = response.get('data', {})
                    optimized_query = data.get('optimized_query')
                    if optimized_query and optimized_query != query:
                        print_info(f"✅ Query optimized: {data.get('estimated_improvement', 'performance improved')}")
                    else:
                        print_info("✅ Query is already well optimized")
                
            except APIError as e:
                print_error(f"Query optimization failed: {e}")
    
    run_async(optimize())


@app.command("validate")
def validate_query(
    query: str = typer.Argument(..., help="Query to validate"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict validation mode"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format"),
):
    """Validate query syntax and safety"""
    
    async def validate():
        # First translate the query to get the SIEM query structure
        translate_data = {"query": query}
        
        async with get_client() as client:
            try:
                # Get the translated query first
                translate_response = await client.post("/api/query/translate", data=translate_data)
                
                if not translate_response.get('success'):
                    print_error("Query validation failed: Could not translate query")
                    return
                
                siem_query = translate_response.get('data', {}).get('siem_query', {})
                
                # Now validate the query structure
                validation_info = {
                    "original_query": query,
                    "translated_successfully": True,
                    "siem_query_structure": siem_query,
                    "validation_mode": "strict" if strict else "standard",
                    "safety_checks": {
                        "has_time_range": bool(siem_query.get('range')),
                        "has_size_limit": bool(siem_query.get('size')),
                        "uses_wildcards": '*' in str(siem_query),
                        "query_complexity": "low" if len(str(siem_query)) < 200 else "high"
                    }
                }
                
                # Basic validation checks
                validation_errors = []
                validation_warnings = []
                
                if not siem_query:
                    validation_errors.append("Empty or invalid SIEM query generated")
                
                if not validation_info["safety_checks"]["has_time_range"]:
                    validation_warnings.append("No time range specified - query may be slow")
                
                if not validation_info["safety_checks"]["has_size_limit"]:
                    validation_warnings.append("No result size limit - query may return too many results")
                
                validation_info["errors"] = validation_errors
                validation_info["warnings"] = validation_warnings
                validation_info["is_valid"] = len(validation_errors) == 0
                validation_info["is_safe"] = len(validation_errors) == 0 and (not strict or len(validation_warnings) == 0)
                
                result = {
                    "success": True,
                    "data": validation_info
                }
                
                print_output(result, "Query Validation", output_format)
                
                # Show validation summary
                if not output_format:
                    if validation_info["is_valid"]:
                        print_success("✅ Query is valid")
                    else:
                        print_error("❌ Query has validation errors")
                    
                    if validation_errors:
                        print_error(f"Errors: {', '.join(validation_errors)}")
                    
                    if validation_warnings:
                        print_info(f"Warnings: {', '.join(validation_warnings)}")
                
            except APIError as e:
                print_error(f"Query validation failed: {e}")
    
    run_async(validate())


@app.command("history")
def query_history(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of recent queries to show"),
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Filter by session ID"),
    successful_only: bool = typer.Option(False, "--successful", help="Show only successful queries"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format"),
):
    """Show recent query history"""
    
    # Note: This would require a history endpoint in the API
    # For now, show a placeholder implementation
    
    print_info("Query history feature is not yet implemented in the API")
    print_info("This would show recent queries, execution times, and results summaries")
    
    # Placeholder data structure
    placeholder_history = {
        "success": True,
        "data": {
            "queries": [
                {
                    "id": "q1",
                    "query": "failed login attempts last hour",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "execution_time_ms": 150,
                    "results_count": 42,
                    "status": "success"
                },
                {
                    "id": "q2", 
                    "query": "show malware alerts",
                    "timestamp": "2024-01-15T10:25:00Z",
                    "execution_time_ms": 89,
                    "results_count": 7,
                    "status": "success"
                }
            ],
            "total": 2,
            "filters": {
                "session_id": session_id,
                "successful_only": successful_only
            }
        }
    }
    
    if not output_format:
        print_info("This is placeholder data - actual implementation would connect to API history endpoint")
    
    print_output(placeholder_history, "Query History (Placeholder)", output_format)


@app.command("explain")
def explain_query(
    query: str = typer.Argument(..., help="Query to explain"),
    include_performance: bool = typer.Option(True, "--performance/--no-performance", help="Include performance analysis"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format"),
):
    """Explain what a query does and how it works"""
    
    async def explain():
        request_data = {"query": query}
        
        async with get_client() as client:
            try:
                # Get the translation first to understand the query
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/query/translate",
                    data=request_data,
                    description=f"Analyzing query: {query[:50]}..."
                )
                
                if response.get('success'):
                    data = response.get('data', {})
                    
                    explanation = {
                        "original_query": query,
                        "intent": data.get('intent', 'unknown'),
                        "confidence": data.get('confidence', 0),
                        "entities": data.get('entities', []),
                        "siem_query": data.get('siem_query', {}),
                        "explanation": {
                            "what_it_does": f"This query searches for {data.get('intent', 'unknown')} events",
                            "data_sources": "Security event logs and SIEM data",
                            "expected_results": f"Events matching the {data.get('intent', 'specified')} criteria",
                            "performance_notes": []
                        }
                    }
                    
                    # Add performance notes
                    if include_performance:
                        siem_query = data.get('siem_query', {})
                        if not siem_query.get('range'):
                            explanation["explanation"]["performance_notes"].append("No time range specified - may be slow")
                        if not siem_query.get('size'):
                            explanation["explanation"]["performance_notes"].append("No size limit - may return many results")
                        if len(str(siem_query)) > 500:
                            explanation["explanation"]["performance_notes"].append("Complex query - may take longer to execute")
                    
                    result = {"success": True, "data": explanation}
                    print_output(result, "Query Explanation", output_format)
                    
                else:
                    print_error("Could not analyze query")
                
            except APIError as e:
                print_error(f"Query explanation failed: {e}")
    
    run_async(explain())

"""
Platform events commands for querying security events
Interfaces with the platform-aware event API endpoints
"""

from typing import Optional
import typer

from ..core.client import get_client, run_async, APIError, make_request_with_spinner
from ..core.output import print_output, print_error, print_success

app = typer.Typer(help="🔍 Query platform security events")


@app.command("auth")
def authentication_events(
    query: str = typer.Option("", "--query", "-q", help="Search query"),
    time_range: str = typer.Option("1h", "--time-range", "-t", help="Time range (1h, 24h, 7d, etc.)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results to return"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """Get authentication events"""
    
    async def get_auth_events():
        request_data = {
            "query": query,
            "time_range": time_range,
            "limit": limit
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/events/authentication",
                    data=request_data,
                    description=f"Fetching authentication events ({time_range})..."
                )
                
                print_output(response, "Authentication Events", output_format)
                
            except APIError as e:
                print_error(f"Failed to get authentication events: {e}")
    
    run_async(get_auth_events())


@app.command("failed-logins")
def failed_logins(
    query: str = typer.Option("", "--query", "-q", help="Search query"),
    time_range: str = typer.Option("1h", "--time-range", "-t", help="Time range (1h, 24h, 7d, etc.)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results to return"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """Get failed login attempts"""
    
    async def get_failed_login_events():
        request_data = {
            "query": query,
            "time_range": time_range,
            "limit": limit
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/events/failed-logins",
                    data=request_data,
                    description=f"Fetching failed login attempts ({time_range})..."
                )
                
                print_output(response, "Failed Login Attempts", output_format)
                
            except APIError as e:
                print_error(f"Failed to get failed login events: {e}")
    
    run_async(get_failed_login_events())


@app.command("successful-logins")
def successful_logins(
    query: str = typer.Option("", "--query", "-q", help="Search query"),
    time_range: str = typer.Option("1h", "--time-range", "-t", help="Time range (1h, 24h, 7d, etc.)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results to return"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """Get successful login events"""
    
    async def get_success_login_events():
        request_data = {
            "query": query,
            "time_range": time_range,
            "limit": limit
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/events/successful-logins",
                    data=request_data,
                    description=f"Fetching successful logins ({time_range})..."
                )
                
                print_output(response, "Successful Logins", output_format)
                
            except APIError as e:
                print_error(f"Failed to get successful login events: {e}")
    
    run_async(get_success_login_events())


@app.command("system-metrics")
def system_metrics(
    query: str = typer.Option("", "--query", "-q", help="Search query"),
    time_range: str = typer.Option("1h", "--time-range", "-t", help="Time range (1h, 24h, 7d, etc.)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results to return"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """Get system metrics and monitoring data"""
    
    async def get_system_metric_events():
        request_data = {
            "query": query,
            "time_range": time_range,
            "limit": limit
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/events/system-metrics",
                    data=request_data,
                    description=f"Fetching system metrics ({time_range})..."
                )
                
                print_output(response, "System Metrics", output_format)
                
            except APIError as e:
                print_error(f"Failed to get system metrics: {e}")
    
    run_async(get_system_metric_events())


@app.command("network")
def network_activity(
    query: str = typer.Option("", "--query", "-q", help="Search query"),
    time_range: str = typer.Option("1h", "--time-range", "-t", help="Time range (1h, 24h, 7d, etc.)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results to return"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """Get network activity and traffic events"""
    
    async def get_network_events():
        request_data = {
            "query": query,
            "time_range": time_range,
            "limit": limit
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/events/network-activity",
                    data=request_data,
                    description=f"Fetching network activity ({time_range})..."
                )
                
                print_output(response, "Network Activity", output_format)
                
            except APIError as e:
                print_error(f"Failed to get network activity: {e}")
    
    run_async(get_network_events())


@app.command("processes")
def process_activity(
    query: str = typer.Option("", "--query", "-q", help="Search query"),
    time_range: str = typer.Option("1h", "--time-range", "-t", help="Time range (1h, 24h, 7d, etc.)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results to return"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """Get process activity and execution events"""
    
    async def get_process_events():
        request_data = {
            "query": query,
            "time_range": time_range,
            "limit": limit
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/events/process-activity",
                    data=request_data,
                    description=f"Fetching process activity ({time_range})..."
                )
                
                print_output(response, "Process Activity", output_format)
                
            except APIError as e:
                print_error(f"Failed to get process activity: {e}")
    
    run_async(get_process_events())


@app.command("capabilities")
def platform_capabilities(
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """Get platform capabilities and available features"""
    
    async def get_capabilities():
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "GET",
                    "/api/events/capabilities",
                    description="Getting platform capabilities..."
                )
                
                print_output(response, "Platform Capabilities", output_format)
                
            except APIError as e:
                print_error(f"Failed to get platform capabilities: {e}")
    
    run_async(get_capabilities())


@app.command("search")
def search_events(
    query: str = typer.Argument(..., help="Search query for events"),
    event_type: Optional[str] = typer.Option(None, "--type", "-t", help="Event type filter"),
    time_range: str = typer.Option("1h", "--time-range", help="Time range (1h, 24h, 7d, etc.)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results to return"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """Search across all event types"""
    
    # Map to the appropriate endpoint based on event type or use general search
    endpoint_map = {
        "auth": "/api/events/authentication",
        "authentication": "/api/events/authentication", 
        "failed-login": "/api/events/failed-logins",
        "successful-login": "/api/events/successful-logins",
        "network": "/api/events/network-activity",
        "process": "/api/events/process-activity",
        "system": "/api/events/system-metrics"
    }
    
    endpoint = endpoint_map.get(event_type.lower() if event_type else "", "/api/events/authentication")
    
    async def search():
        request_data = {
            "query": query,
            "time_range": time_range,
            "limit": limit
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    endpoint,
                    data=request_data,
                    description=f"Searching events: {query[:50]}..."
                )
                
                print_output(response, f"Search Results - {query}", output_format)
                
            except APIError as e:
                print_error(f"Event search failed: {e}")
    
    run_async(search())

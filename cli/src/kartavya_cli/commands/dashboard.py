"""
Dashboard commands for metrics and system monitoring
Interfaces with the Kartavya dashboard API endpoints
"""

from typing import Optional
import typer

from ..core.client import get_client, run_async, APIError, make_request_with_spinner
from ..core.output import print_output, print_error, print_success

app = typer.Typer(help="📈 Dashboard metrics and alerts")


@app.command("metrics")
def get_metrics(
    time_range: str = typer.Option("24h", "--time-range", "-t", help="Time range (1h, 24h, 7d, 30d)"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """Get dashboard security metrics"""
    
    async def fetch_metrics():
        params = {"time_range": time_range}
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "GET",
                    "/api/dashboard/metrics",
                    params=params,
                    description=f"Fetching metrics for {time_range}..."
                )
                
                print_output(response, f"Security Metrics ({time_range})", output_format)
                
            except APIError as e:
                print_error(f"Failed to get metrics: {e}")
    
    run_async(fetch_metrics())


@app.command("alerts")
def get_alerts(
    limit: int = typer.Option(50, "--limit", "-l", help="Number of alerts to return"),
    severity: Optional[str] = typer.Option(None, "--severity", "-s", help="Filter by severity (critical, high, medium, low)"),
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status (active, investigating, resolved)"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """Get security alerts"""
    
    async def fetch_alerts():
        params = {"limit": limit}
        if severity:
            params["severity"] = severity
        if status:
            params["status"] = status
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "GET",
                    "/api/dashboard/alerts",
                    params=params,
                    description="Fetching security alerts..."
                )
                
                print_output(response, "Security Alerts", output_format)
                
            except APIError as e:
                print_error(f"Failed to get alerts: {e}")
    
    run_async(fetch_alerts())


@app.command("update-alert")
def update_alert(
    alert_id: str = typer.Argument(..., help="Alert ID to update"),
    status: Optional[str] = typer.Option(None, "--status", help="New status"),
    assignee: Optional[str] = typer.Option(None, "--assignee", help="Assign to user"),
    notes: Optional[str] = typer.Option(None, "--notes", help="Add notes"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format")
):
    """Update an alert status or details"""
    
    updates = {}
    if status:
        updates["status"] = status
    if assignee:
        updates["assignee"] = assignee
    if notes:
        updates["notes"] = notes
    
    if not updates:
        print_error("No updates specified. Use --status, --assignee, or --notes")
        return
    
    async def update():
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "PATCH",
                    f"/api/dashboard/alerts/{alert_id}",
                    data=updates,
                    description=f"Updating alert {alert_id}..."
                )
                
                print_output(response, "Alert Update", output_format)
                print_success(f"Alert {alert_id} updated successfully")
                
            except APIError as e:
                print_error(f"Failed to update alert: {e}")
    
    run_async(update())


@app.command("status")
def system_status(
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format")
):
    """Get system status and data source information"""
    
    async def get_status():
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "GET",
                    "/api/dashboard/system/status",
                    description="Getting system status..."
                )
                
                print_output(response, "System Status", output_format)
                
            except APIError as e:
                print_error(f"Failed to get system status: {e}")
    
    run_async(get_status())


@app.command("data-sources")
def data_source_status(
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format")
):
    """Get data source configuration and availability"""
    
    async def get_data_sources():
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "GET",
                    "/api/dashboard/data-source/status",
                    description="Getting data source status..."
                )
                
                print_output(response, "Data Source Status", output_format)
                
            except APIError as e:
                print_error(f"Failed to get data source status: {e}")
    
    run_async(get_data_sources())

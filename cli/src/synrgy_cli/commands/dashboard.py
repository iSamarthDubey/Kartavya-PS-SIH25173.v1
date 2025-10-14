"""
Dashboard commands for metrics and alerting functionality.

Provides access to system metrics, performance data, and alert management
for the Kartavya SIEM dashboard.
"""

from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn

from synrgy_cli.core.client import APIClient, APIError
from synrgy_cli.core.config import Config
from synrgy_cli.core.output import OutputFormatter

console = Console()
app = typer.Typer(help="📈 Dashboard metrics and alerting")

def get_client_and_formatter():
    """Get API client and output formatter."""
    config = Config()
    client = APIClient(config)
    formatter = OutputFormatter(config, console)
    return client, formatter

@app.command()
def metrics(
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json)"
    ),
    category: Optional[str] = typer.Option(
        None,
        "--category", "-c",
        help="Filter by metric category (system, security, performance)"
    )
):
    """Show dashboard metrics and key performance indicators."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Fetching dashboard metrics..."):
            metrics_data = client.get_dashboard_metrics()
        
        if not metrics_data:
            formatter.print_warning("No metrics data available")
            return
        
        if format == "json":
            formatter.print_json(metrics_data, "Dashboard Metrics")
        else:
            # Display key metrics in a structured format
            _display_metrics_overview(metrics_data, formatter, category)
            
    except APIError as e:
        formatter.print_error(f"Failed to fetch metrics: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def alerts(
    status: Optional[str] = typer.Option(
        None,
        "--status", "-s",
        help="Filter by alert status (active, acknowledged, resolved)"
    ),
    limit: int = typer.Option(
        50,
        "--limit", "-n",
        help="Maximum number of alerts to show"
    ),
    severity: Optional[str] = typer.Option(
        None,
        "--severity",
        help="Filter by severity (critical, high, medium, low)"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json, csv)"
    )
):
    """List and manage system alerts."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Fetching alerts..."):
            alerts_data = client.get_alerts(status=status)
        
        if not alerts_data:
            formatter.print_warning("No alerts found")
            return
        
        # Apply additional filtering
        filtered_alerts = alerts_data
        if severity:
            filtered_alerts = [a for a in alerts_data if a.get('severity', '').lower() == severity.lower()]
        
        # Limit results
        filtered_alerts = filtered_alerts[:limit]
        
        title = f"System Alerts ({len(filtered_alerts)} found)"
        if status:
            title += f" - Status: {status.title()}"
        if severity:
            title += f" - Severity: {severity.title()}"
        
        formatter.print_data(filtered_alerts, format, title)
        
        # Show alert summary
        if filtered_alerts and format == "table":
            _show_alert_summary(filtered_alerts, formatter)
            
    except APIError as e:
        formatter.print_error(f"Failed to fetch alerts: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def acknowledge(
    alert_id: str = typer.Argument(..., help="Alert ID to acknowledge"),
    message: Optional[str] = typer.Option(
        None,
        "--message", "-m",
        help="Acknowledgment message"
    )
):
    """Acknowledge a specific alert."""
    client, formatter = get_client_and_formatter()
    
    try:
        formatter.print_info(f"Acknowledging alert {alert_id}...")
        
        with console.status("[bold blue]Processing acknowledgment..."):
            result = client.acknowledge_alert(alert_id)
        
        if result.get('success', True):
            formatter.print_success(f"Alert {alert_id} acknowledged successfully")
            
            # Show acknowledgment details
            details = {
                "Alert ID": alert_id,
                "Status": "Acknowledged",
                "Acknowledged At": result.get('acknowledged_at', 'Now'),
                "Acknowledged By": result.get('acknowledged_by', 'Current User')
            }
            
            if message:
                details["Message"] = message
            
            formatter.print_data(details, "table", "✅ Acknowledgment Details")
        else:
            formatter.print_error(f"Failed to acknowledge alert: {result.get('error', 'Unknown error')}")
            
    except APIError as e:
        formatter.print_error(f"Failed to acknowledge alert: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def status():
    """Show overall system status and health."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Checking system status..."):
            # Get health and metrics data
            health_ok = client.get_health()
            metrics_data = client.get_dashboard_metrics()
            active_alerts = client.get_alerts(status="active")
        
        # Overall system status
        if health_ok:
            status_color = "green"
            status_text = "✅ System Healthy"
        else:
            status_color = "red"
            status_text = "❌ System Issues Detected"
        
        console.print(Panel.fit(
            f"[{status_color}]{status_text}[/{status_color}]",
            title="🏥 System Health",
            border_style=status_color
        ))
        
        # Quick metrics overview
        if metrics_data:
            quick_stats = {
                "CPU Usage": f"{metrics_data.get('cpu_usage', 0):.1f}%",
                "Memory Usage": f"{metrics_data.get('memory_usage', 0):.1f}%",
                "Disk Usage": f"{metrics_data.get('disk_usage', 0):.1f}%",
                "Active Sessions": metrics_data.get('active_sessions', 0),
                "Events/Hour": metrics_data.get('events_per_hour', 0)
            }
            
            formatter.print_data(quick_stats, "table", "📊 Quick Stats")
        
        # Active alerts summary
        if active_alerts:
            alert_counts = {}
            for alert in active_alerts:
                severity = alert.get('severity', 'unknown')
                alert_counts[severity] = alert_counts.get(severity, 0) + 1
            
            alert_summary = {
                "Critical": alert_counts.get('critical', 0),
                "High": alert_counts.get('high', 0),
                "Medium": alert_counts.get('medium', 0),
                "Low": alert_counts.get('low', 0),
                "Total": len(active_alerts)
            }
            
            formatter.print_data(alert_summary, "table", "🚨 Active Alerts")
        else:
            formatter.print_success("No active alerts")
            
    except APIError as e:
        formatter.print_error(f"Failed to get system status: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def watch(
    interval: int = typer.Option(
        30,
        "--interval", "-i",
        help="Refresh interval in seconds"
    ),
    metrics: bool = typer.Option(
        True,
        "--metrics/--no-metrics",
        help="Show metrics in watch mode"
    ),
    alerts: bool = typer.Option(
        True,
        "--alerts/--no-alerts", 
        help="Show alerts in watch mode"
    )
):
    """Watch dashboard metrics and alerts in real-time."""
    client, formatter = get_client_and_formatter()
    
    try:
        formatter.print_info(f"Starting dashboard watch mode (refresh every {interval}s)")
        formatter.print_info("Press Ctrl+C to stop")
        
        import time
        from rich.live import Live
        from rich.layout import Layout
        
        layout = Layout()
        
        if metrics and alerts:
            layout.split_column(
                Layout(name="metrics", ratio=1),
                Layout(name="alerts", ratio=1)
            )
        elif metrics:
            layout.add_split(Layout(name="metrics"))
        else:
            layout.add_split(Layout(name="alerts"))
        
        with Live(layout, console=console, refresh_per_second=1):
            while True:
                try:
                    # Update metrics
                    if metrics:
                        metrics_data = client.get_dashboard_metrics()
                        if metrics_data:
                            metrics_panel = _create_metrics_panel(metrics_data)
                            layout["metrics"].update(metrics_panel)
                    
                    # Update alerts
                    if alerts:
                        alerts_data = client.get_alerts(status="active")
                        if alerts_data:
                            alerts_panel = _create_alerts_panel(alerts_data[:10])  # Show top 10
                            if metrics and alerts:
                                layout["alerts"].update(alerts_panel)
                            elif alerts:
                                layout.update(alerts_panel)
                    
                    time.sleep(interval)
                    
                except KeyboardInterrupt:
                    break
                    
        formatter.print_info("Watch mode stopped")
        
    except KeyboardInterrupt:
        formatter.print_info("Watch mode stopped")
    except APIError as e:
        formatter.print_error(f"Watch mode failed: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

def _display_metrics_overview(metrics_data: dict, formatter: OutputFormatter, category: Optional[str] = None):
    """Display metrics in organized categories."""
    
    # System metrics
    if not category or category == "system":
        system_metrics = {
            "CPU Usage": f"{metrics_data.get('cpu_usage', 0):.1f}%",
            "Memory Usage": f"{metrics_data.get('memory_usage', 0):.1f}%",
            "Disk Usage": f"{metrics_data.get('disk_usage', 0):.1f}%",
            "Network I/O": f"{metrics_data.get('network_io', 0)} MB/s",
            "Uptime": metrics_data.get('uptime', 'Unknown')
        }
        formatter.print_data(system_metrics, "table", "🖥️ System Metrics")
    
    # Security metrics
    if not category or category == "security":
        security_metrics = {
            "Events Today": metrics_data.get('events_today', 0),
            "Failed Logins": metrics_data.get('failed_logins_today', 0),
            "Active Sessions": metrics_data.get('active_sessions', 0),
            "Threat Detections": metrics_data.get('threats_detected', 0),
            "Blocked IPs": metrics_data.get('blocked_ips', 0)
        }
        formatter.print_data(security_metrics, "table", "🔒 Security Metrics")
    
    # Performance metrics
    if not category or category == "performance":
        performance_metrics = {
            "Query Response Time": f"{metrics_data.get('avg_query_time', 0):.0f}ms",
            "Events/Second": metrics_data.get('events_per_second', 0),
            "Database Size": f"{metrics_data.get('database_size_gb', 0):.1f} GB",
            "Index Efficiency": f"{metrics_data.get('index_efficiency', 0):.1f}%",
            "Cache Hit Rate": f"{metrics_data.get('cache_hit_rate', 0):.1f}%"
        }
        formatter.print_data(performance_metrics, "table", "⚡ Performance Metrics")

def _show_alert_summary(alerts: list, formatter: OutputFormatter):
    """Show summary statistics for alerts."""
    # Count by severity
    severity_counts = {}
    status_counts = {}
    
    for alert in alerts:
        severity = alert.get('severity', 'unknown')
        status = alert.get('status', 'unknown')
        
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Severity distribution
    severity_data = []
    for severity in ['critical', 'high', 'medium', 'low']:
        count = severity_counts.get(severity, 0)
        if count > 0:
            percentage = (count / len(alerts)) * 100
            severity_data.append({
                "Severity": severity.title(),
                "Count": count,
                "Percentage": f"{percentage:.1f}%"
            })
    
    if severity_data:
        formatter.print_data(severity_data, "table", "🚨 Alert Severity Distribution")
    
    # Status distribution
    status_data = []
    for status, count in status_counts.items():
        percentage = (count / len(alerts)) * 100
        status_data.append({
            "Status": status.title(),
            "Count": count,
            "Percentage": f"{percentage:.1f}%"
        })
    
    formatter.print_data(status_data, "table", "📊 Alert Status Distribution")

def _create_metrics_panel(metrics_data: dict) -> Panel:
    """Create a panel for metrics display in watch mode."""
    content = []
    
    # Key metrics
    content.append(f"CPU: {metrics_data.get('cpu_usage', 0):.1f}%")
    content.append(f"Memory: {metrics_data.get('memory_usage', 0):.1f}%")
    content.append(f"Events/Hour: {metrics_data.get('events_per_hour', 0)}")
    content.append(f"Active Sessions: {metrics_data.get('active_sessions', 0)}")
    
    return Panel(
        "\n".join(content),
        title="📊 System Metrics",
        border_style="blue"
    )

def _create_alerts_panel(alerts_data: list) -> Panel:
    """Create a panel for alerts display in watch mode."""
    if not alerts_data:
        return Panel(
            "No active alerts",
            title="🚨 Active Alerts",
            border_style="green"
        )
    
    content = []
    for alert in alerts_data[:5]:  # Show top 5
        severity = alert.get('severity', 'unknown')
        message = alert.get('message', 'No message')[:50]
        
        # Color based on severity
        if severity == 'critical':
            color = "red"
        elif severity == 'high':
            color = "yellow"
        elif severity == 'medium':
            color = "blue"
        else:
            color = "white"
        
        content.append(f"[{color}]• {severity.upper()}: {message}[/{color}]")
    
    if len(alerts_data) > 5:
        content.append(f"[dim]... and {len(alerts_data) - 5} more alerts[/dim]")
    
    border_color = "red" if any(a.get('severity') == 'critical' for a in alerts_data) else "yellow"
    
    return Panel(
        "\n".join(content),
        title=f"🚨 Active Alerts ({len(alerts_data)})",
        border_style=border_color
    )

if __name__ == "__main__":
    app()

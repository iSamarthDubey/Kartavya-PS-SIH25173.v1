"""
Reports commands for generation and management.

Provides functionality to generate, list, export, and schedule
various types of security and operational reports.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from synrgy_cli.core.client import APIClient, APIError
from synrgy_cli.core.config import Config
from synrgy_cli.core.output import OutputFormatter

console = Console()
app = typer.Typer(help="📊 Report generation and management")

def get_client_and_formatter():
    """Get API client and output formatter."""
    config = Config()
    client = APIClient(config)
    formatter = OutputFormatter(config, console)
    return client, formatter

@app.command()
def generate(
    report_type: str = typer.Argument(..., help="Type of report (security, compliance, activity, threat)"),
    start_date: Optional[str] = typer.Option(
        None,
        "--start-date",
        help="Report start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None,
        "--end-date",
        help="Report end date (YYYY-MM-DD)"
    ),
    format: str = typer.Option(
        "pdf",
        "--format", "-f",
        help="Report format (pdf, html, csv, json)"
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="Custom report title"
    ),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        help="Report description"
    ),
    filters: Optional[str] = typer.Option(
        None,
        "--filters",
        help="JSON string of additional filters"
    ),
    email: Optional[str] = typer.Option(
        None,
        "--email",
        help="Email address to send the report to"
    )
):
    """Generate a new report."""
    client, formatter = get_client_and_formatter()
    
    try:
        # Prepare report parameters
        parameters = {
            "format": format,
            "start_date": start_date,
            "end_date": end_date,
        }
        
        if title:
            parameters["title"] = title
        if description:
            parameters["description"] = description
        if email:
            parameters["email"] = email
        
        # Parse additional filters if provided
        if filters:
            try:
                additional_filters = json.loads(filters)
                parameters.update(additional_filters)
            except json.JSONDecodeError:
                formatter.print_error("Invalid JSON format for filters")
                raise typer.Exit(1)
        
        formatter.print_info(f"Generating {report_type} report...")
        
        with console.status("[bold blue]Generating report..."):
            report = client.generate_report(report_type, parameters)
        
        report_id = report.get('report_id')
        status = report.get('status', 'unknown')
        
        if status == 'completed':
            formatter.print_success(f"Report generated successfully!")
            console.print(Panel.fit(
                f"[bold green]Report ID:[/bold green] {report_id}\n"
                f"[bold blue]Type:[/bold blue] {report_type.title()}\n"
                f"[bold blue]Format:[/bold blue] {format.upper()}\n"
                f"[bold blue]Status:[/bold blue] {status.title()}",
                title="📊 Report Generated",
                border_style="green"
            ))
            
            if report.get('download_url'):
                console.print(f"\n[dim]Download URL: {report['download_url']}[/dim]")
            
        elif status == 'processing':
            formatter.print_info(f"Report generation started (ID: {report_id})")
            formatter.print_info("Use 'kartavya reports status' to check progress")
        else:
            formatter.print_warning(f"Report generation status: {status}")
        
        # Show additional details if available
        if report.get('estimated_completion'):
            console.print(f"[dim]Estimated completion: {report['estimated_completion']}[/dim]")
            
    except APIError as e:
        formatter.print_error(f"Failed to generate report: {e.message}")
        if e.response_data:
            console.print(f"[dim]{e.response_data}[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def list(
    limit: int = typer.Option(
        50,
        "--limit", "-n",
        help="Maximum number of reports to show"
    ),
    status: Optional[str] = typer.Option(
        None,
        "--status",
        help="Filter by status (completed, processing, failed, scheduled)"
    ),
    report_type: Optional[str] = typer.Option(
        None,
        "--type", "-t",
        help="Filter by report type"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json)"
    )
):
    """List existing reports."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Fetching reports..."):
            reports = client.get_reports(limit=limit)
        
        if not reports:
            formatter.print_warning("No reports found")
            return
        
        # Apply filtering
        filtered_reports = reports
        if status:
            filtered_reports = [r for r in reports if r.get('status', '').lower() == status.lower()]
        if report_type:
            filtered_reports = [r for r in reports if r.get('type', '').lower() == report_type.lower()]
        
        title = f"Reports ({len(filtered_reports)} found)"
        if status:
            title += f" - Status: {status}"
        if report_type:
            title += f" - Type: {report_type}"
        
        formatter.print_data(filtered_reports, format, title)
        
        # Show summary if table format
        if filtered_reports and format == "table":
            _show_report_summary(filtered_reports, formatter)
            
    except APIError as e:
        formatter.print_error(f"Failed to fetch reports: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def status(
    report_id: str = typer.Argument(..., help="Report ID to check"),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json)"
    )
):
    """Check the status of a specific report."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status(f"[bold blue]Checking report status..."):
            report = client.get_report(report_id)
        
        if format == "json":
            formatter.print_json(report, f"Report Status - {report_id}")
        else:
            status = report.get('status', 'unknown')
            progress = report.get('progress', 0)
            
            # Status-specific styling
            if status == 'completed':
                status_display = f"[green]✓ {status.title()}[/green]"
            elif status == 'processing':
                status_display = f"[yellow]⏳ {status.title()} ({progress}%)[/yellow]"
            elif status == 'failed':
                status_display = f"[red]✗ {status.title()}[/red]"
            else:
                status_display = f"[blue]{status.title()}[/blue]"
            
            console.print(Panel.fit(
                f"[bold blue]Report ID:[/bold blue] {report_id}\n"
                f"[bold blue]Type:[/bold blue] {report.get('type', 'Unknown').title()}\n"
                f"[bold blue]Status:[/bold blue] {status_display}\n"
                f"[bold blue]Created:[/bold blue] {report.get('created_at', 'Unknown')}\n"
                f"[bold blue]Format:[/bold blue] {report.get('format', 'Unknown').upper()}",
                title="📊 Report Status",
                border_style="blue"
            ))
            
            if status == 'completed' and report.get('download_url'):
                console.print(f"\n[green]Download URL:[/green] {report['download_url']}")
            elif status == 'failed' and report.get('error'):
                console.print(f"\n[red]Error:[/red] {report['error']}")
            
    except APIError as e:
        formatter.print_error(f"Failed to get report status: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def export(
    report_id: str = typer.Argument(..., help="Report ID to export"),
    format: str = typer.Option(
        "csv",
        "--format", "-f",
        help="Export format (csv, json, xlsx, pdf)"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output file path"
    )
):
    """Export a report in different formats."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status(f"[bold blue]Exporting report..."):
            export_data = client.export_report(report_id, format)
        
        # Determine output filename
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"report_{report_id[:8]}_{timestamp}.{format}"
        
        # Handle different response types
        if 'download_url' in export_data:
            # Server provides download URL
            formatter.print_success(f"Export ready for download")
            console.print(f"[green]Download URL:[/green] {export_data['download_url']}")
        elif 'data' in export_data:
            # Server returns data directly
            if format == 'json':
                with open(output, 'w') as f:
                    json.dump(export_data['data'], f, indent=2, default=str)
            else:
                with open(output, 'w') as f:
                    f.write(str(export_data['data']))
            
            formatter.print_success(f"Report exported to {output}")
        else:
            formatter.print_warning("Export completed but no data returned")
            
    except APIError as e:
        formatter.print_error(f"Failed to export report: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def schedule(
    report_type: str = typer.Argument(..., help="Type of report to schedule"),
    frequency: str = typer.Option(
        "daily",
        "--frequency",
        help="Schedule frequency (daily, weekly, monthly)"
    ),
    time: str = typer.Option(
        "09:00",
        "--time",
        help="Time to run (HH:MM format)"
    ),
    email: str = typer.Option(
        ...,
        "--email",
        help="Email address to send reports to"
    ),
    format: str = typer.Option(
        "pdf",
        "--format", "-f",
        help="Report format (pdf, csv, html)"
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="Custom report title template"
    ),
    enabled: bool = typer.Option(
        True,
        "--enabled/--disabled",
        help="Enable or disable the schedule"
    )
):
    """Schedule recurring reports."""
    client, formatter = get_client_and_formatter()
    
    try:
        schedule_config = {
            "report_type": report_type,
            "frequency": frequency,
            "time": time,
            "email": email,
            "format": format,
            "enabled": enabled
        }
        
        if title:
            schedule_config["title"] = title
        
        with console.status("[bold blue]Creating report schedule..."):
            result = client.schedule_report(schedule_config)
        
        schedule_id = result.get('schedule_id')
        formatter.print_success(f"Report schedule created successfully!")
        
        console.print(Panel.fit(
            f"[bold green]Schedule ID:[/bold green] {schedule_id}\n"
            f"[bold blue]Report Type:[/bold blue] {report_type.title()}\n"
            f"[bold blue]Frequency:[/bold blue] {frequency.title()}\n"
            f"[bold blue]Time:[/bold blue] {time}\n"
            f"[bold blue]Email:[/bold blue] {email}\n"
            f"[bold blue]Format:[/bold blue] {format.upper()}\n"
            f"[bold blue]Status:[/bold blue] {'Enabled' if enabled else 'Disabled'}",
            title="📅 Scheduled Report",
            border_style="green"
        ))
        
        if result.get('next_run'):
            console.print(f"\n[dim]Next run: {result['next_run']}[/dim]")
            
    except APIError as e:
        formatter.print_error(f"Failed to schedule report: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def templates():
    """Show available report templates and types."""
    formatter = OutputFormatter()
    
    # Built-in report templates (this would typically come from the API)
    templates = [
        {
            "Type": "security",
            "Description": "Comprehensive security event analysis",
            "Parameters": "start_date, end_date, severity_level",
            "Formats": "PDF, HTML, CSV"
        },
        {
            "Type": "compliance", 
            "Description": "Regulatory compliance reporting",
            "Parameters": "start_date, end_date, framework",
            "Formats": "PDF, HTML"
        },
        {
            "Type": "activity",
            "Description": "User and system activity summary",
            "Parameters": "start_date, end_date, user_filter",
            "Formats": "PDF, CSV, JSON"
        },
        {
            "Type": "threat",
            "Description": "Threat intelligence and indicators",
            "Parameters": "start_date, end_date, threat_type",
            "Formats": "PDF, JSON"
        },
        {
            "Type": "performance",
            "Description": "System performance and availability",
            "Parameters": "start_date, end_date, metrics",
            "Formats": "PDF, HTML, CSV"
        },
        {
            "Type": "audit",
            "Description": "Security audit trail and changes",
            "Parameters": "start_date, end_date, category",
            "Formats": "PDF, CSV"
        }
    ]
    
    formatter.print_data(templates, "table", "📋 Available Report Templates")
    
    # Show example usage
    console.print("\n[bold blue]Example Usage:[/bold blue]")
    console.print("  kartavya reports generate security --start-date 2024-01-01 --end-date 2024-01-31")
    console.print("  kartavya reports generate compliance --format pdf --email user@company.com")
    console.print("  kartavya reports schedule activity --frequency weekly --time 08:00 --email admin@company.com")

def _show_report_summary(reports, formatter: OutputFormatter):
    """Show summary statistics for reports."""
    # Status distribution
    status_counts = {}
    type_counts = {}
    
    for report in reports:
        status = report.get('status', 'unknown')
        report_type = report.get('type', 'unknown')
        
        status_counts[status] = status_counts.get(status, 0) + 1
        type_counts[report_type] = type_counts.get(report_type, 0) + 1
    
    # Status summary
    status_data = []
    for status, count in sorted(status_counts.items()):
        percentage = (count / len(reports)) * 100
        status_data.append({
            "Status": status.title(),
            "Count": count,
            "Percentage": f"{percentage:.1f}%"
        })
    
    formatter.print_data(status_data, "table", "📊 Report Status Summary")
    
    # Type summary
    type_data = []
    for report_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(reports)) * 100
        type_data.append({
            "Type": report_type.title(),
            "Count": count,
            "Percentage": f"{percentage:.1f}%"
        })
    
    formatter.print_data(type_data, "table", "📈 Report Type Distribution")

if __name__ == "__main__":
    app()

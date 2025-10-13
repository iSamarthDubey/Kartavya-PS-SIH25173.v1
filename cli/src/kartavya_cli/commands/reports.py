"""
Reports commands for generating and managing security reports
Interfaces with the Kartavya reports API endpoints
"""

from typing import Optional, Dict, Any
import typer
import json

from ..core.client import get_client, run_async, APIError, make_request_with_spinner
from ..core.output import print_output, print_error, print_success, print_info

app = typer.Typer(help="📊 Generate and manage reports")


@app.command("generate")
def generate_report(
    report_type: str = typer.Argument(..., help="Report type (security_summary, incident_report, etc.)"),
    params: Optional[str] = typer.Option(None, "--params", "-p", help="JSON parameters for report generation"),
    size: int = typer.Option(1000, "--size", "-s", help="Maximum number of events to analyze"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)"),
    save_file: Optional[str] = typer.Option(None, "--save", help="Save report to file"),
):
    """Generate a security report"""
    
    async def create_report():
        # Parse parameters if provided
        report_params = {"size": size}
        if params:
            try:
                additional_params = json.loads(params)
                report_params.update(additional_params)
            except json.JSONDecodeError:
                print_error("Invalid JSON in parameters")
                return
        
        request_data = {
            "report_type": report_type,
            "params": report_params
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/reports/generate",
                    data=request_data,
                    description=f"Generating {report_type} report..."
                )
                
                if save_file:
                    # Save report to file
                    try:
                        with open(save_file, 'w', encoding='utf-8') as f:
                            if output_format == "json" or save_file.endswith('.json'):
                                json.dump(response, f, indent=2)
                            else:
                                # Save as formatted text
                                f.write(print_output(response, f"{report_type.title()} Report", output_format))
                        
                        print_success(f"Report saved to {save_file}")
                    except Exception as e:
                        print_error(f"Failed to save report: {e}")
                
                print_output(response, f"{report_type.title()} Report", output_format)
                
            except APIError as e:
                print_error(f"Failed to generate report: {e}")
    
    run_async(create_report())


@app.command("list")
def list_reports(
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """List available report types"""
    
    async def get_report_list():
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "GET",
                    "/api/reports/templates",
                    description="Getting available report types..."
                )
                
                print_output(response, "Available Report Types", output_format)
                
            except APIError as e:
                print_error(f"Failed to get report types: {e}")
    
    run_async(get_report_list())


@app.command("export")
def export_report(
    report_format: str = typer.Argument(..., help="Export format (pdf, csv, json, html)"),
    report_id: Optional[str] = typer.Option(None, "--id", help="Report ID to export"),
    report_type: Optional[str] = typer.Option(None, "--type", help="Generate and export report of this type"),
    params: Optional[str] = typer.Option(None, "--params", help="JSON parameters for report generation"),
    output_file: Optional[str] = typer.Option(None, "--file", "-f", help="Output file path"),
):
    """Export report in specified format"""
    
    if not report_id and not report_type:
        print_error("Either --id or --type must be specified")
        return
    
    async def export():
        if report_type:
            # Generate new report first
            report_params = {}
            if params:
                try:
                    report_params = json.loads(params)
                except json.JSONDecodeError:
                    print_error("Invalid JSON in parameters")
                    return
            
            # Generate the report
            generate_data = {
                "report_type": report_type,
                "params": report_params
            }
            
            async with get_client() as client:
                try:
                    # Generate report first
                    report_response = await make_request_with_spinner(
                        client,
                        "POST",
                        "/api/reports/generate",
                        data=generate_data,
                        description=f"Generating {report_type} report for export..."
                    )
                    
                    # Export the generated report
                    export_response = await make_request_with_spinner(
                        client,
                        "GET",
                        f"/api/reports/export/{report_format}",
                        description=f"Exporting report as {report_format.upper()}..."
                    )
                    
                    if output_file:
                        try:
                            with open(output_file, 'w', encoding='utf-8') as f:
                                if report_format.lower() == 'json':
                                    json.dump(export_response, f, indent=2)
                                else:
                                    f.write(str(export_response.get('data', export_response)))
                            
                            print_success(f"Report exported to {output_file}")
                        except Exception as e:
                            print_error(f"Failed to save exported report: {e}")
                    else:
                        print_output(export_response, f"Exported Report ({report_format.upper()})")
                    
                except APIError as e:
                    print_error(f"Failed to export report: {e}")
        
        else:
            # Export existing report by ID
            async with get_client() as client:
                try:
                    response = await make_request_with_spinner(
                        client,
                        "GET",
                        f"/api/reports/export/{report_format}?id={report_id}",
                        description=f"Exporting report {report_id} as {report_format.upper()}..."
                    )
                    
                    if output_file:
                        try:
                            with open(output_file, 'w', encoding='utf-8') as f:
                                if report_format.lower() == 'json':
                                    json.dump(response, f, indent=2)
                                else:
                                    f.write(str(response.get('data', response)))
                            
                            print_success(f"Report exported to {output_file}")
                        except Exception as e:
                            print_error(f"Failed to save exported report: {e}")
                    else:
                        print_output(response, f"Exported Report ({report_format.upper()})")
                    
                except APIError as e:
                    print_error(f"Failed to export report: {e}")
    
    run_async(export())


@app.command("schedule")
def schedule_report(
    report_type: str = typer.Argument(..., help="Report type to schedule"),
    schedule: str = typer.Option("daily", "--schedule", "-s", help="Schedule frequency (hourly, daily, weekly, monthly)"),
    params: Optional[str] = typer.Option(None, "--params", help="JSON parameters for report"),
    email: Optional[str] = typer.Option(None, "--email", help="Email address for delivery"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format"),
):
    """Schedule recurring report generation"""
    
    async def schedule_recurring_report():
        # Parse parameters if provided
        report_params = {}
        if params:
            try:
                report_params = json.loads(params)
            except json.JSONDecodeError:
                print_error("Invalid JSON in parameters")
                return
        
        request_data = {
            "report_type": report_type,
            "schedule": schedule,
            "params": report_params,
            "delivery": {
                "email": email
            } if email else {}
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/reports/schedule",
                    data=request_data,
                    description=f"Scheduling {schedule} {report_type} report..."
                )
                
                print_output(response, "Scheduled Report", output_format)
                print_success(f"Successfully scheduled {schedule} {report_type} report")
                
            except APIError as e:
                print_error(f"Failed to schedule report: {e}")
    
    run_async(schedule_recurring_report())


@app.command("security-summary")
def security_summary_report(
    time_range: str = typer.Option("24h", "--time-range", "-t", help="Time range for analysis"),
    include_charts: bool = typer.Option(True, "--charts/--no-charts", help="Include visualizations"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format"),
    save_file: Optional[str] = typer.Option(None, "--save", help="Save report to file"),
):
    """Generate comprehensive security summary report"""
    
    params = {
        "time_range": time_range,
        "include_visualizations": include_charts,
        "analysis_depth": "comprehensive"
    }
    
    async def generate_security_summary():
        request_data = {
            "report_type": "security_summary",
            "params": params
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/reports/generate",
                    data=request_data,
                    description=f"Generating security summary for {time_range}..."
                )
                
                if save_file:
                    try:
                        with open(save_file, 'w', encoding='utf-8') as f:
                            if save_file.endswith('.json'):
                                json.dump(response, f, indent=2)
                            else:
                                f.write(str(response.get('data', response)))
                        
                        print_success(f"Security summary saved to {save_file}")
                    except Exception as e:
                        print_error(f"Failed to save report: {e}")
                
                print_output(response, "Security Summary Report", output_format)
                
            except APIError as e:
                print_error(f"Failed to generate security summary: {e}")
    
    run_async(generate_security_summary())


@app.command("incident-report")
def incident_report(
    severity: str = typer.Option("critical", "--severity", "-s", help="Minimum severity level"),
    time_range: str = typer.Option("7d", "--time-range", "-t", help="Time range for incidents"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum incidents to include"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format"),
    save_file: Optional[str] = typer.Option(None, "--save", help="Save report to file"),
):
    """Generate incident analysis report"""
    
    params = {
        "severity": severity,
        "time_range": time_range,
        "size": limit,
        "include_timeline": True,
        "include_affected_systems": True
    }
    
    async def generate_incident_report():
        request_data = {
            "report_type": "incident_report",
            "params": params
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/reports/generate",
                    data=request_data,
                    description=f"Generating incident report for {severity}+ incidents..."
                )
                
                if save_file:
                    try:
                        with open(save_file, 'w', encoding='utf-8') as f:
                            if save_file.endswith('.json'):
                                json.dump(response, f, indent=2)
                            else:
                                f.write(str(response.get('data', response)))
                        
                        print_success(f"Incident report saved to {save_file}")
                    except Exception as e:
                        print_error(f"Failed to save report: {e}")
                
                print_output(response, "Incident Analysis Report", output_format)
                
            except APIError as e:
                print_error(f"Failed to generate incident report: {e}")
    
    run_async(generate_incident_report())

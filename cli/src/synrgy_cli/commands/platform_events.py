"""
Platform events commands for security event analysis and filtering.

Provides commands to query, filter, and analyze various types of
security events from the Kartavya SIEM platform.
"""

from datetime import datetime, timedelta
from typing import Optional, List
import typer
from rich.console import Console

from synrgy_cli.core.client import APIClient, APIError
from synrgy_cli.core.config import Config
from synrgy_cli.core.output import OutputFormatter

console = Console()
app = typer.Typer(help="🔍 Platform event analysis and filtering")

def get_client_and_formatter():
    """Get API client and output formatter."""
    config = Config()
    client = APIClient(config)
    formatter = OutputFormatter(config, console)
    return client, formatter

@app.command()
def list(
    event_type: Optional[str] = typer.Option(
        None,
        "--type", "-t",
        help="Filter by event type (authentication, network, system, etc.)"
    ),
    start_time: Optional[str] = typer.Option(
        None,
        "--start",
        help="Start time (ISO format: YYYY-MM-DDTHH:MM:SS)"
    ),
    end_time: Optional[str] = typer.Option(
        None,
        "--end", 
        help="End time (ISO format: YYYY-MM-DDTHH:MM:SS)"
    ),
    limit: int = typer.Option(
        100,
        "--limit", "-n",
        help="Maximum number of events to retrieve"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json, csv)"
    ),
    save: Optional[str] = typer.Option(
        None,
        "--save", "-o",
        help="Save results to file"
    )
):
    """List platform events with optional filtering."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Fetching platform events..."):
            events = client.get_platform_events(
                event_type=event_type,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
        
        if not events:
            formatter.print_warning("No events found matching the criteria")
            return
        
        title = f"Platform Events ({len(events)} found)"
        if event_type:
            title += f" - Type: {event_type}"
        
        if save:
            formatter.save_to_file(events, save, format)
            formatter.print_success(f"Events saved to {save}")
        else:
            formatter.print_data(events, format, title)
            
    except APIError as e:
        formatter.print_error(f"Failed to fetch events: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def authentication(
    limit: int = typer.Option(
        100,
        "--limit", "-n",
        help="Maximum number of events to retrieve"
    ),
    success_only: bool = typer.Option(
        False,
        "--success-only",
        help="Show only successful authentication events"
    ),
    failed_only: bool = typer.Option(
        False,
        "--failed-only", 
        help="Show only failed authentication events"
    ),
    user: Optional[str] = typer.Option(
        None,
        "--user", "-u",
        help="Filter by username"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json, csv)"
    )
):
    """Show authentication events."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Fetching authentication events..."):
            events = client.get_authentication_events(limit=limit)
        
        if not events:
            formatter.print_warning("No authentication events found")
            return
        
        # Apply additional filtering
        filtered_events = events
        if success_only:
            filtered_events = [e for e in events if e.get('success', False)]
        elif failed_only:
            filtered_events = [e for e in events if not e.get('success', True)]
        
        if user:
            filtered_events = [e for e in filtered_events if user.lower() in e.get('username', '').lower()]
        
        title = f"Authentication Events ({len(filtered_events)} found)"
        if success_only:
            title += " - Successful Only"
        elif failed_only:
            title += " - Failed Only"
        if user:
            title += f" - User: {user}"
        
        formatter.print_data(filtered_events, format, title)
        
        # Show summary statistics
        if filtered_events and format == "table":
            total = len(filtered_events)
            successful = len([e for e in filtered_events if e.get('success', False)])
            failed = total - successful
            
            summary = {
                "Total Events": total,
                "Successful": successful,
                "Failed": failed,
                "Success Rate": f"{(successful/total)*100:.1f}%" if total > 0 else "0%"
            }
            
            formatter.print_data(summary, "table", "📊 Authentication Summary")
            
    except APIError as e:
        formatter.print_error(f"Failed to fetch authentication events: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def failed_logins(
    limit: int = typer.Option(
        100,
        "--limit", "-n",
        help="Maximum number of events to retrieve"
    ),
    hours: int = typer.Option(
        24,
        "--hours",
        help="Show failed logins from the last N hours"
    ),
    ip: Optional[str] = typer.Option(
        None,
        "--ip",
        help="Filter by source IP address"
    ),
    user: Optional[str] = typer.Option(
        None,
        "--user", "-u",
        help="Filter by username"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json, csv)"
    )
):
    """Show failed login attempts with analysis."""
    client, formatter = get_client_and_formatter()
    
    try:
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        with console.status("[bold blue]Fetching failed login events..."):
            events = client.get_failed_login_events(limit=limit)
        
        if not events:
            formatter.print_warning("No failed login events found")
            return
        
        # Filter by time range, IP, and user
        filtered_events = []
        for event in events:
            # Add time filtering logic here based on your event structure
            if ip and ip not in event.get('source_ip', ''):
                continue
            if user and user.lower() not in event.get('username', '').lower():
                continue
            filtered_events.append(event)
        
        title = f"Failed Login Attempts ({len(filtered_events)} found)"
        if hours < 24:
            title += f" - Last {hours} hours"
        if ip:
            title += f" - IP: {ip}"
        if user:
            title += f" - User: {user}"
        
        formatter.print_data(filtered_events, format, title)
        
        # Show threat analysis
        if filtered_events and format == "table":
            _show_failed_login_analysis(filtered_events, formatter)
            
    except APIError as e:
        formatter.print_error(f"Failed to fetch failed login events: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def network(
    limit: int = typer.Option(
        100,
        "--limit", "-n",
        help="Maximum number of events to retrieve"
    ),
    protocol: Optional[str] = typer.Option(
        None,
        "--protocol", "-p",
        help="Filter by protocol (tcp, udp, icmp, etc.)"
    ),
    port: Optional[int] = typer.Option(
        None,
        "--port",
        help="Filter by destination port"
    ),
    src_ip: Optional[str] = typer.Option(
        None,
        "--src-ip",
        help="Filter by source IP address"
    ),
    dst_ip: Optional[str] = typer.Option(
        None,
        "--dst-ip",
        help="Filter by destination IP address"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json, csv)"
    )
):
    """Show network events and traffic analysis."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Fetching network events..."):
            events = client.get_network_events(limit=limit)
        
        if not events:
            formatter.print_warning("No network events found")
            return
        
        # Apply filtering
        filtered_events = events
        if protocol:
            filtered_events = [e for e in filtered_events if e.get('protocol', '').lower() == protocol.lower()]
        if port:
            filtered_events = [e for e in filtered_events if e.get('dest_port') == port]
        if src_ip:
            filtered_events = [e for e in filtered_events if src_ip in e.get('source_ip', '')]
        if dst_ip:
            filtered_events = [e for e in filtered_events if dst_ip in e.get('dest_ip', '')]
        
        title = f"Network Events ({len(filtered_events)} found)"
        filters = []
        if protocol:
            filters.append(f"Protocol: {protocol}")
        if port:
            filters.append(f"Port: {port}")
        if src_ip:
            filters.append(f"Src IP: {src_ip}")
        if dst_ip:
            filters.append(f"Dst IP: {dst_ip}")
        if filters:
            title += f" - {', '.join(filters)}"
        
        formatter.print_data(filtered_events, format, title)
        
        # Show network analysis
        if filtered_events and format == "table":
            _show_network_analysis(filtered_events, formatter)
            
    except APIError as e:
        formatter.print_error(f"Failed to fetch network events: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query for events"),
    limit: int = typer.Option(
        100,
        "--limit", "-n",
        help="Maximum number of events to retrieve"
    ),
    event_type: Optional[str] = typer.Option(
        None,
        "--type", "-t",
        help="Filter by event type"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json, csv)"
    )
):
    """Search events using text query."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status(f"[bold blue]Searching for '{query}'..."):
            events = client.get_platform_events(
                event_type=event_type,
                limit=limit
            )
        
        if not events:
            formatter.print_warning("No events found")
            return
        
        # Filter events by search query
        search_results = []
        query_lower = query.lower()
        
        for event in events:
            # Search in various fields
            searchable_text = " ".join([
                str(event.get('message', '')),
                str(event.get('source_ip', '')),
                str(event.get('username', '')),
                str(event.get('event_type', '')),
                str(event.get('details', ''))
            ]).lower()
            
            if query_lower in searchable_text:
                search_results.append(event)
        
        title = f"Search Results for '{query}' ({len(search_results)} found)"
        if event_type:
            title += f" - Type: {event_type}"
        
        if search_results:
            formatter.print_data(search_results, format, title)
        else:
            formatter.print_warning(f"No events found matching '{query}'")
            
    except APIError as e:
        formatter.print_error(f"Search failed: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def stats(
    hours: int = typer.Option(
        24,
        "--hours",
        help="Statistics for the last N hours"
    ),
    by_type: bool = typer.Option(
        True,
        "--by-type/--no-by-type",
        help="Group statistics by event type"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json)"
    )
):
    """Show event statistics and trends."""
    client, formatter = get_client_and_formatter()
    
    try:
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        with console.status("[bold blue]Calculating event statistics..."):
            events = client.get_platform_events(
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                limit=1000  # Get more events for better stats
            )
        
        if not events:
            formatter.print_warning("No events found for statistics")
            return
        
        # Calculate statistics
        stats_data = []
        
        if by_type:
            # Group by event type
            type_counts = {}
            for event in events:
                event_type = event.get('event_type', 'Unknown')
                type_counts[event_type] = type_counts.get(event_type, 0) + 1
            
            for event_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(events)) * 100
                stats_data.append({
                    "Event Type": event_type,
                    "Count": count,
                    "Percentage": f"{percentage:.1f}%"
                })
        else:
            # Overall statistics
            total_events = len(events)
            unique_ips = len(set(e.get('source_ip', '') for e in events if e.get('source_ip')))
            unique_users = len(set(e.get('username', '') for e in events if e.get('username')))
            
            stats_data = [{
                "Metric": "Total Events",
                "Value": total_events
            }, {
                "Metric": "Unique Source IPs",
                "Value": unique_ips
            }, {
                "Metric": "Unique Users",
                "Value": unique_users
            }, {
                "Metric": "Events per Hour",
                "Value": f"{total_events / hours:.1f}"
            }]
        
        title = f"Event Statistics - Last {hours} hours"
        formatter.print_data(stats_data, format, title)
        
    except APIError as e:
        formatter.print_error(f"Failed to get statistics: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

def _show_failed_login_analysis(events: List[dict], formatter: OutputFormatter):
    """Show analysis of failed login attempts."""
    # Analyze by IP
    ip_counts = {}
    user_counts = {}
    
    for event in events:
        ip = event.get('source_ip', 'Unknown')
        user = event.get('username', 'Unknown')
        
        ip_counts[ip] = ip_counts.get(ip, 0) + 1
        user_counts[user] = user_counts.get(user, 0) + 1
    
    # Top attacking IPs
    top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ip_analysis = []
    for ip, count in top_ips:
        threat_level = "🔴 HIGH" if count > 10 else "🟡 MEDIUM" if count > 5 else "🟢 LOW"
        ip_analysis.append({
            "Source IP": ip,
            "Failed Attempts": count,
            "Threat Level": threat_level
        })
    
    formatter.print_data(ip_analysis, "table", "🚨 Top Attacking IPs")
    
    # Top targeted users
    top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    user_analysis = []
    for user, count in top_users:
        user_analysis.append({
            "Username": user,
            "Failed Attempts": count
        })
    
    formatter.print_data(user_analysis, "table", "🎯 Most Targeted Users")

def _show_network_analysis(events: List[dict], formatter: OutputFormatter):
    """Show analysis of network events."""
    # Analyze by protocol and port
    protocol_counts = {}
    port_counts = {}
    
    for event in events:
        protocol = event.get('protocol', 'Unknown')
        port = event.get('dest_port')
        
        protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
        if port:
            port_counts[port] = port_counts.get(port, 0) + 1
    
    # Protocol distribution
    protocol_data = []
    for protocol, count in sorted(protocol_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(events)) * 100
        protocol_data.append({
            "Protocol": protocol.upper(),
            "Count": count,
            "Percentage": f"{percentage:.1f}%"
        })
    
    formatter.print_data(protocol_data, "table", "🌐 Protocol Distribution")
    
    # Top destination ports
    top_ports = sorted(port_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    port_data = []
    for port, count in top_ports:
        # Common port identification
        common_ports = {
            22: "SSH", 80: "HTTP", 443: "HTTPS", 21: "FTP",
            25: "SMTP", 53: "DNS", 110: "POP3", 143: "IMAP",
            993: "IMAPS", 995: "POP3S"
        }
        service = common_ports.get(port, "Unknown")
        
        port_data.append({
            "Port": port,
            "Service": service,
            "Count": count
        })
    
    formatter.print_data(port_data, "table", "🔌 Top Destination Ports")

if __name__ == "__main__":
    app()

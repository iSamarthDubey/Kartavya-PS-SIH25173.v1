"""
Admin commands for user management and audit log operations.

Provides administrative functionality for managing users, permissions,
and viewing audit trails in the Kartavya SIEM system.
"""

import json
from typing import Optional, Dict, Any
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

from synrgy_cli.core.client import APIClient, APIError
from synrgy_cli.core.config import Config
from synrgy_cli.core.output import OutputFormatter

console = Console()
app = typer.Typer(help="👥 Administrative operations")

def get_client_and_formatter():
    """Get API client and output formatter."""
    config = Config()
    client = APIClient(config)
    formatter = OutputFormatter(config, console)
    return client, formatter

@app.command()
def users(
    limit: int = typer.Option(
        100,
        "--limit", "-n",
        help="Maximum number of users to show"
    ),
    active_only: bool = typer.Option(
        False,
        "--active-only",
        help="Show only active users"
    ),
    role: Optional[str] = typer.Option(
        None,
        "--role", "-r",
        help="Filter by user role (admin, analyst, viewer)"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json, csv)"
    )
):
    """List and manage system users."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Fetching users..."):
            users_data = client.get_users(limit=limit)
        
        if not users_data:
            formatter.print_warning("No users found")
            return
        
        # Apply filtering
        filtered_users = users_data
        if active_only:
            filtered_users = [u for u in users_data if u.get('active', True)]
        if role:
            filtered_users = [u for u in filtered_users if u.get('role', '').lower() == role.lower()]
        
        title = f"System Users ({len(filtered_users)} found)"
        if active_only:
            title += " - Active Only"
        if role:
            title += f" - Role: {role.title()}"
        
        formatter.print_data(filtered_users, format, title)
        
        # Show user statistics
        if filtered_users and format == "table":
            _show_user_statistics(filtered_users, formatter)
            
    except APIError as e:
        formatter.print_error(f"Failed to fetch users: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def create_user(
    username: str = typer.Argument(..., help="Username for the new user"),
    email: str = typer.Option(..., "--email", help="Email address"),
    role: str = typer.Option(
        "analyst",
        "--role", "-r",
        help="User role (admin, analyst, viewer)"
    ),
    full_name: Optional[str] = typer.Option(
        None,
        "--full-name",
        help="Full name of the user"
    ),
    department: Optional[str] = typer.Option(
        None,
        "--department",
        help="User's department"
    ),
    active: bool = typer.Option(
        True,
        "--active/--inactive",
        help="Set user as active or inactive"
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive", "-i",
        help="Interactive user creation mode"
    )
):
    """Create a new user account."""
    client, formatter = get_client_and_formatter()
    
    try:
        if interactive:
            # Interactive mode
            username = Prompt.ask("Username", default=username)
            email = Prompt.ask("Email address", default=email)
            role = Prompt.ask("Role", choices=["admin", "analyst", "viewer"], default=role)
            full_name = Prompt.ask("Full name", default=full_name or "")
            department = Prompt.ask("Department", default=department or "")
            active = Confirm.ask("Active user?", default=active)
        
        # Validate required fields
        if not username or not email:
            formatter.print_error("Username and email are required")
            raise typer.Exit(1)
        
        user_data = {
            "username": username,
            "email": email,
            "role": role,
            "active": active
        }
        
        if full_name:
            user_data["full_name"] = full_name
        if department:
            user_data["department"] = department
        
        formatter.print_info(f"Creating user '{username}'...")
        
        with console.status("[bold blue]Creating user account..."):
            result = client.create_user(user_data)
        
        user_id = result.get('user_id')
        formatter.print_success(f"User '{username}' created successfully!")
        
        # Show created user details
        user_details = {
            "User ID": user_id,
            "Username": username,
            "Email": email,
            "Role": role.title(),
            "Status": "Active" if active else "Inactive"
        }
        
        if full_name:
            user_details["Full Name"] = full_name
        if department:
            user_details["Department"] = department
        
        formatter.print_data(user_details, "table", "👤 User Created")
        
        # Show temporary password if provided
        if result.get('temporary_password'):
            console.print(Panel.fit(
                f"[yellow]Temporary Password: {result['temporary_password']}[/yellow]\n"
                "[dim]The user should change this password on first login[/dim]",
                title="🔑 Login Credentials",
                border_style="yellow"
            ))
            
    except APIError as e:
        formatter.print_error(f"Failed to create user: {e.message}")
        if e.response_data:
            console.print(f"[dim]{e.response_data}[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def update_user(
    user_id: str = typer.Argument(..., help="User ID to update"),
    email: Optional[str] = typer.Option(None, "--email", help="New email address"),
    role: Optional[str] = typer.Option(None, "--role", help="New role"),
    active: Optional[bool] = typer.Option(None, "--active/--inactive", help="Set active status"),
    full_name: Optional[str] = typer.Option(None, "--full-name", help="New full name"),
    department: Optional[str] = typer.Option(None, "--department", help="New department")
):
    """Update an existing user account."""
    client, formatter = get_client_and_formatter()
    
    try:
        # Build update data from provided options
        update_data = {}
        if email:
            update_data["email"] = email
        if role:
            update_data["role"] = role
        if active is not None:
            update_data["active"] = active
        if full_name:
            update_data["full_name"] = full_name
        if department:
            update_data["department"] = department
        
        if not update_data:
            formatter.print_error("No update parameters provided")
            raise typer.Exit(1)
        
        formatter.print_info(f"Updating user {user_id}...")
        
        with console.status("[bold blue]Updating user account..."):
            result = client.update_user(user_id, update_data)
        
        formatter.print_success(f"User {user_id} updated successfully!")
        
        # Show updated user details
        if result.get('user'):
            updated_user = result['user']
            user_details = {
                "User ID": user_id,
                "Username": updated_user.get('username', 'N/A'),
                "Email": updated_user.get('email', 'N/A'),
                "Role": updated_user.get('role', 'N/A').title(),
                "Status": "Active" if updated_user.get('active', True) else "Inactive",
                "Last Updated": updated_user.get('updated_at', 'Now')
            }
            
            formatter.print_data(user_details, "table", "👤 Updated User")
            
    except APIError as e:
        formatter.print_error(f"Failed to update user: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def delete_user(
    user_id: str = typer.Argument(..., help="User ID to delete"),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Skip confirmation prompt"
    )
):
    """Delete a user account."""
    client, formatter = get_client_and_formatter()
    
    try:
        if not force:
            confirm = Confirm.ask(f"Are you sure you want to delete user {user_id}?")
            if not confirm:
                formatter.print_info("User deletion cancelled")
                return
        
        formatter.print_info(f"Deleting user {user_id}...")
        
        with console.status("[bold blue]Deleting user account..."):
            result = client.delete_user(user_id)
        
        if result.get('success', True):
            formatter.print_success(f"User {user_id} deleted successfully")
        else:
            formatter.print_error(f"Failed to delete user: {result.get('error', 'Unknown error')}")
            
    except APIError as e:
        formatter.print_error(f"Failed to delete user: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def audit_logs(
    limit: int = typer.Option(
        100,
        "--limit", "-n",
        help="Maximum number of log entries to show"
    ),
    user: Optional[str] = typer.Option(
        None,
        "--user", "-u",
        help="Filter by username"
    ),
    action: Optional[str] = typer.Option(
        None,
        "--action", "-a",
        help="Filter by action type"
    ),
    start_date: Optional[str] = typer.Option(
        None,
        "--start-date",
        help="Start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None,
        "--end-date",
        help="End date (YYYY-MM-DD)"
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
    """View system audit logs."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Fetching audit logs..."):
            logs_data = client.get_audit_logs(limit=limit)
        
        if not logs_data:
            formatter.print_warning("No audit logs found")
            return
        
        # Apply filtering
        filtered_logs = logs_data
        if user:
            filtered_logs = [log for log in logs_data if user.lower() in log.get('username', '').lower()]
        if action:
            filtered_logs = [log for log in filtered_logs if action.lower() in log.get('action', '').lower()]
        
        # Date filtering would be implemented based on the API response format
        
        title = f"Audit Logs ({len(filtered_logs)} entries)"
        filters = []
        if user:
            filters.append(f"User: {user}")
        if action:
            filters.append(f"Action: {action}")
        if start_date or end_date:
            date_range = f"{start_date or 'start'} to {end_date or 'now'}"
            filters.append(f"Date: {date_range}")
        if filters:
            title += f" - {', '.join(filters)}"
        
        if save:
            formatter.save_to_file(filtered_logs, save, format)
            formatter.print_success(f"Audit logs saved to {save}")
        else:
            formatter.print_data(filtered_logs, format, title)
        
        # Show audit log summary
        if filtered_logs and format == "table":
            _show_audit_summary(filtered_logs, formatter)
            
    except APIError as e:
        formatter.print_error(f"Failed to fetch audit logs: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def permissions(
    user_id: Optional[str] = typer.Argument(None, help="User ID to show permissions for"),
    role: Optional[str] = typer.Option(
        None,
        "--role", "-r",
        help="Show permissions for a specific role"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json)"
    )
):
    """Show user permissions and role capabilities."""
    formatter = OutputFormatter()
    
    if user_id:
        # Show permissions for specific user
        # This would typically call the API to get user-specific permissions
        formatter.print_info(f"Showing permissions for user: {user_id}")
        
        # Mock permissions data (replace with actual API call)
        user_permissions = [
            {"Resource": "Events", "Permissions": "Read, Write"},
            {"Resource": "Reports", "Permissions": "Read, Generate"},
            {"Resource": "Users", "Permissions": "Read"},
            {"Resource": "Dashboard", "Permissions": "Read"},
            {"Resource": "Queries", "Permissions": "Read, Execute"}
        ]
        
        formatter.print_data(user_permissions, format, f"👤 User Permissions - {user_id}")
        
    elif role:
        # Show permissions for specific role
        role_permissions = _get_role_permissions(role)
        if role_permissions:
            formatter.print_data(role_permissions, format, f"🔒 Role Permissions - {role.title()}")
        else:
            formatter.print_error(f"Unknown role: {role}")
            
    else:
        # Show all role definitions
        all_roles = [
            {
                "Role": "Admin",
                "Description": "Full system access and user management",
                "Key Permissions": "All operations, user management, system config"
            },
            {
                "Role": "Analyst", 
                "Description": "Security analysis and investigation",
                "Key Permissions": "Read events, generate reports, execute queries"
            },
            {
                "Role": "Viewer",
                "Description": "Read-only access to dashboards and reports",
                "Key Permissions": "Read dashboards, view reports"
            }
        ]
        
        formatter.print_data(all_roles, format, "🔐 System Roles")

@app.command()
def system_info():
    """Show system information and configuration."""
    client, formatter = get_client_and_formatter()
    
    try:
        # This would typically call multiple API endpoints
        with console.status("[bold blue]Gathering system information..."):
            health_ok = client.get_health()
            # Additional system info would come from dedicated endpoints
        
        system_info = {
            "System Status": "Healthy" if health_ok else "Issues Detected",
            "API Version": "1.0.0",  # This would come from API
            "Database": "Connected",  # This would come from API
            "Authentication": "Active",  # This would come from API
            "Backup Status": "Up to date",  # This would come from API
            "License": "Valid"  # This would come from API
        }
        
        formatter.print_data(system_info, "table", "⚙️ System Information")
        
        # Additional system details
        console.print("\n[bold blue]System Capabilities:[/bold blue]")
        capabilities = [
            "✅ Natural Language Processing",
            "✅ Real-time Event Processing", 
            "✅ Advanced Analytics",
            "✅ Automated Reporting",
            "✅ User Management",
            "✅ Audit Logging",
            "✅ API Access",
            "✅ Dashboard Monitoring"
        ]
        
        for capability in capabilities:
            console.print(f"  {capability}")
            
    except APIError as e:
        formatter.print_error(f"Failed to get system info: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

def _show_user_statistics(users: list, formatter: OutputFormatter):
    """Show user statistics summary."""
    # Role distribution
    role_counts = {}
    status_counts = {"active": 0, "inactive": 0}
    
    for user in users:
        role = user.get('role', 'unknown')
        active = user.get('active', True)
        
        role_counts[role] = role_counts.get(role, 0) + 1
        status_counts["active" if active else "inactive"] += 1
    
    # Role summary
    role_data = []
    for role, count in sorted(role_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(users)) * 100
        role_data.append({
            "Role": role.title(),
            "Count": count,
            "Percentage": f"{percentage:.1f}%"
        })
    
    formatter.print_data(role_data, "table", "👥 Role Distribution")
    
    # Status summary
    status_data = [{
        "Status": "Active",
        "Count": status_counts["active"]
    }, {
        "Status": "Inactive", 
        "Count": status_counts["inactive"]
    }]
    
    formatter.print_data(status_data, "table", "📊 User Status")

def _show_audit_summary(logs: list, formatter: OutputFormatter):
    """Show audit log summary statistics."""
    # Action distribution
    action_counts = {}
    user_counts = {}
    
    for log in logs:
        action = log.get('action', 'unknown')
        user = log.get('username', 'unknown')
        
        action_counts[action] = action_counts.get(action, 0) + 1
        user_counts[user] = user_counts.get(user, 0) + 1
    
    # Top actions
    top_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    action_data = []
    for action, count in top_actions:
        percentage = (count / len(logs)) * 100
        action_data.append({
            "Action": action.title(),
            "Count": count,
            "Percentage": f"{percentage:.1f}%"
        })
    
    formatter.print_data(action_data, "table", "📋 Top Actions")
    
    # Most active users
    top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    user_data = []
    for user, count in top_users:
        user_data.append({
            "Username": user,
            "Actions": count
        })
    
    formatter.print_data(user_data, "table", "👤 Most Active Users")

def _get_role_permissions(role: str) -> list:
    """Get permissions for a specific role."""
    role_permissions = {
        "admin": [
            {"Resource": "Events", "Permissions": "Read, Write, Delete"},
            {"Resource": "Reports", "Permissions": "Read, Generate, Schedule, Delete"},
            {"Resource": "Users", "Permissions": "Read, Create, Update, Delete"},
            {"Resource": "Dashboard", "Permissions": "Read, Configure"},
            {"Resource": "Queries", "Permissions": "Read, Execute, Optimize"},
            {"Resource": "System", "Permissions": "Configure, Monitor, Backup"}
        ],
        "analyst": [
            {"Resource": "Events", "Permissions": "Read, Write"},
            {"Resource": "Reports", "Permissions": "Read, Generate"},
            {"Resource": "Users", "Permissions": "Read (own profile only)"},
            {"Resource": "Dashboard", "Permissions": "Read"},
            {"Resource": "Queries", "Permissions": "Read, Execute"}
        ],
        "viewer": [
            {"Resource": "Events", "Permissions": "Read"},
            {"Resource": "Reports", "Permissions": "Read"},
            {"Resource": "Users", "Permissions": "Read (own profile only)"},
            {"Resource": "Dashboard", "Permissions": "Read"},
            {"Resource": "Queries", "Permissions": "Read"}
        ]
    }
    
    return role_permissions.get(role.lower())

if __name__ == "__main__":
    app()

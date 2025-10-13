"""
Admin commands for user management and system administration
Interfaces with the Kartavya admin API endpoints
"""

from typing import Optional
import typer

from ..core.client import get_client, run_async, APIError, make_request_with_spinner
from ..core.output import print_output, print_error, print_success

app = typer.Typer(help="⚙️ Administrative commands")


@app.command("users")
def list_users(
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)")
):
    """List all users"""
    
    async def get_users():
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "GET",
                    "/api/admin/users",
                    description="Fetching users..."
                )
                
                print_output(response, "System Users", output_format)
                
            except APIError as e:
                print_error(f"Failed to get users: {e}")
    
    run_async(get_users())


@app.command("create-user")
def create_user(
    username: str = typer.Argument(..., help="Username for new user"),
    email: str = typer.Option("", "--email", "-e", help="Email address"),
    role: str = typer.Option("viewer", "--role", "-r", help="User role (admin, analyst, viewer)"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format")
):
    """Create a new user"""
    
    async def create():
        user_data = {
            "username": username,
            "email": email,
            "role": role
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/admin/users",
                    data=user_data,
                    description=f"Creating user {username}..."
                )
                
                print_output(response, "User Created", output_format)
                print_success(f"User {username} created successfully")
                
            except APIError as e:
                print_error(f"Failed to create user: {e}")
    
    run_async(create())


@app.command("update-user")
def update_user(
    username: str = typer.Argument(..., help="Username to update"),
    email: Optional[str] = typer.Option(None, "--email", "-e", help="New email address"),
    role: Optional[str] = typer.Option(None, "--role", "-r", help="New role"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format")
):
    """Update user details"""
    
    updates = {}
    if email:
        updates["email"] = email
    if role:
        updates["role"] = role
    
    if not updates:
        print_error("No updates specified. Use --email or --role")
        return
    
    async def update():
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "PUT",
                    f"/api/admin/users/{username}",
                    data=updates,
                    description=f"Updating user {username}..."
                )
                
                print_output(response, "User Updated", output_format)
                print_success(f"User {username} updated successfully")
                
            except APIError as e:
                print_error(f"Failed to update user: {e}")
    
    run_async(update())


@app.command("delete-user")
def delete_user(
    username: str = typer.Argument(..., help="Username to delete"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format")
):
    """Delete a user"""
    
    if not confirm:
        if not typer.confirm(f"Delete user {username}? This action cannot be undone."):
            print("Operation cancelled.")
            return
    
    async def delete():
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "DELETE",
                    f"/api/admin/users/{username}",
                    description=f"Deleting user {username}..."
                )
                
                print_output(response, "User Deleted", output_format)
                print_success(f"User {username} deleted successfully")
                
            except APIError as e:
                print_error(f"Failed to delete user: {e}")
    
    run_async(delete())


@app.command("audit-log")
def audit_log(
    limit: int = typer.Option(50, "--limit", "-l", help="Number of audit entries to show"),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Filter by username"),
    action: Optional[str] = typer.Option(None, "--action", "-a", help="Filter by action"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format")
):
    """View system audit log"""
    
    async def get_audit():
        params = {"limit": limit}
        if user:
            params["user"] = user
        if action:
            params["action"] = action
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "GET",
                    "/api/admin/audit",
                    params=params,
                    description="Fetching audit log..."
                )
                
                print_output(response, "Audit Log", output_format)
                
            except APIError as e:
                print_error(f"Failed to get audit log: {e}")
    
    run_async(get_audit())

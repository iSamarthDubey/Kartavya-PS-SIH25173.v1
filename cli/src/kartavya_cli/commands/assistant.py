"""
Assistant commands for chat and conversation management
Interfaces with the Kartavya SIEM NLP Assistant API
"""

from typing import Optional, Dict, Any
import uuid
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from ..core.client import get_client, run_async, APIError, make_request_with_spinner
from ..core.output import print_output, print_error, print_success, print_chat_response
from ..core.config import get_config

app = typer.Typer(help="💬 Chat with the AI assistant")
console = Console()


@app.command("ask")
def chat_ask(
    query: str = typer.Argument(..., help="Natural language security query"),
    conversation_id: Optional[str] = typer.Option(None, "--conversation-id", "-c", help="Conversation ID for context"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results to return"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (table, json, csv)"),
    filters: Optional[str] = typer.Option(None, "--filters", help="JSON filters to apply"),
):
    """Ask the AI assistant a security question"""
    
    async def execute():
        # Parse filters if provided
        filter_dict = {}
        if filters:
            try:
                import json
                filter_dict = json.loads(filters)
            except json.JSONDecodeError:
                print_error("Invalid JSON in filters")
                return
        
        # Prepare request data
        request_data = {
            "query": query,
            "conversation_id": conversation_id,
            "limit": limit,
            "filters": filter_dict or None
        }
        
        async with get_client() as client:
            try:
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/assistant/chat",
                    data=request_data,
                    description=f"Processing query: {query[:50]}..."
                )
                
                # Use special chat formatting if no custom format specified
                if not output_format:
                    print_chat_response(response)
                else:
                    print_output(response, format_type=output_format)
                
            except APIError as e:
                print_error(f"Chat request failed: {e}")
    
    run_async(execute())


@app.command("interactive")
def interactive_chat(
    conversation_id: Optional[str] = typer.Option(None, "--conversation-id", "-c", help="Conversation ID to resume"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results per query"),
):
    """Start interactive chat session"""
    
    config = get_config()
    conv_id = conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
    
    if config.color:
        console.print(Panel.fit(
            f"[bold green]Kartavya Interactive Chat[/bold green]\\n"
            f"Conversation ID: [cyan]{conv_id}[/cyan]\\n"
            f"Type 'exit', 'quit', or press Ctrl+C to end session\\n"
            f"Type 'help' for available commands",
            title="💬 Chat Session Started"
        ))
    else:
        print(f"\\n=== Kartavya Interactive Chat ===")
        print(f"Conversation ID: {conv_id}")
        print("Type 'exit', 'quit', or press Ctrl+C to end session")
        print("Type 'help' for available commands\\n")
    
    while True:
        try:
            # Get user input
            if config.color:
                query = Prompt.ask("[bold blue]You[/bold blue]")
            else:
                query = input("You: ")
            
            # Handle special commands
            if query.lower() in ['exit', 'quit']:
                break
            elif query.lower() == 'help':
                show_help()
                continue
            elif query.lower() == 'clear':
                console.clear()
                continue
            elif query.strip() == '':
                continue
            
            # Process the query
            async def process_query():
                request_data = {
                    "query": query,
                    "conversation_id": conv_id,
                    "limit": limit
                }
                
                async with get_client() as client:
                    try:
                        response = await make_request_with_spinner(
                            client,
                            "POST",
                            "/api/assistant/chat",
                            data=request_data,
                            description="Thinking..."
                        )
                        
                        print_chat_response(response)
                        print()  # Add spacing
                        
                    except APIError as e:
                        print_error(f"Query failed: {e}")
            
            run_async(process_query())
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    if config.color:
        console.print("\\n[bold yellow]Chat session ended. Goodbye![/bold yellow]")
    else:
        print("\\nChat session ended. Goodbye!")


def show_help():
    """Show interactive chat help"""
    config = get_config()
    
    if config.color:
        console.print(Panel(
            "[bold]Available Commands:[/bold]\\n"
            "[cyan]exit, quit[/cyan] - End chat session\\n"
            "[cyan]help[/cyan] - Show this help\\n"
            "[cyan]clear[/cyan] - Clear screen\\n\\n"
            "[bold]Example Queries:[/bold]\\n"
            "• Show failed login attempts from last hour\\n"
            "• Find malware alerts with high severity\\n"
            "• What are the top security threats today?\\n"
            "• Show user activity for admin accounts\\n"
            "• Analyze network traffic anomalies",
            title="💡 Chat Help"
        ))
    else:
        print("\\n=== Available Commands ===")
        print("exit, quit - End chat session")
        print("help - Show this help")
        print("clear - Clear screen")
        print("\\n=== Example Queries ===")
        print("• Show failed login attempts from last hour")
        print("• Find malware alerts with high severity")
        print("• What are the top security threats today?")
        print("• Show user activity for admin accounts")
        print("• Analyze network traffic anomalies\\n")


@app.command("history")
def conversation_history(
    conversation_id: str = typer.Argument(..., help="Conversation ID"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of history entries to show"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format")
):
    """Get conversation history"""
    
    async def get_history():
        request_data = {
            "conversation_id": conversation_id,
            "limit": limit
        }
        
        async with get_client() as client:
            try:
                # Note: This endpoint might not exist in current API, 
                # but showing the structure for when it's implemented
                response = await make_request_with_spinner(
                    client,
                    "POST",
                    "/api/assistant/history",
                    data=request_data,
                    description="Fetching conversation history..."
                )
                
                print_output(response, f"Conversation History ({conversation_id})", output_format)
                
            except APIError as e:
                if e.status_code == 404:
                    print_error("Conversation history not found or feature not available")
                else:
                    print_error(f"Failed to get conversation history: {e}")
    
    run_async(get_history())


@app.command("clear")
def clear_conversation(
    conversation_id: str = typer.Argument(..., help="Conversation ID to clear"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Clear conversation context"""
    
    if not confirm:
        if not typer.confirm(f"Clear conversation {conversation_id}?"):
            print("Operation cancelled.")
            return
    
    async def clear_conv():
        async with get_client() as client:
            try:
                # This would clear the conversation context on the backend
                response = await make_request_with_spinner(
                    client,
                    "DELETE",
                    f"/api/assistant/conversations/{conversation_id}",
                    description="Clearing conversation..."
                )
                
                print_success(f"Conversation {conversation_id} cleared")
                
            except APIError as e:
                if e.status_code == 404:
                    print_error("Conversation not found or feature not available")
                else:
                    print_error(f"Failed to clear conversation: {e}")
    
    run_async(clear_conv())


@app.command("suggest")
def get_suggestions(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Suggestion category"),
    output_format: Optional[str] = typer.Option(None, "--output", "-o", help="Output format")
):
    """Get query suggestions"""
    
    async def get_query_suggestions():
        async with get_client() as client:
            try:
                # Get suggestions from query endpoint
                response = await make_request_with_spinner(
                    client,
                    "GET",
                    "/api/query/suggestions",
                    description="Getting suggestions..."
                )
                
                # Filter by category if specified
                if category:
                    suggestions = response.get('data', {})
                    if category in suggestions:
                        filtered_response = {
                            "success": True,
                            "data": {category: suggestions[category]}
                        }
                        print_output(filtered_response, f"Suggestions - {category.title()}", output_format)
                    else:
                        print_error(f"Category '{category}' not found. Available categories: {list(suggestions.keys())}")
                else:
                    print_output(response, "Query Suggestions", output_format)
                
            except APIError as e:
                print_error(f"Failed to get suggestions: {e}")
    
    run_async(get_query_suggestions())

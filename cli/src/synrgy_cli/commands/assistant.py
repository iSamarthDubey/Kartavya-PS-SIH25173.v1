"""
Assistant commands for AI chat and conversation management.

Provides interactive chat sessions and one-shot question answering
with the Kartavya SIEM NLP assistant.
"""

import json
import uuid
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live
import questionary

from synrgy_cli.core.client import APIClient, APIError
from synrgy_cli.core.config import Config
from synrgy_cli.core.output import OutputFormatter

console = Console()
app = typer.Typer(help="💬 AI Assistant chat and conversation management")

def get_client_and_formatter():
    """Get API client and output formatter."""
    config = Config()
    client = APIClient(config)
    formatter = OutputFormatter(config, console)
    return client, formatter

@app.command()
def interactive(
    conversation_id: Optional[str] = typer.Option(
        None, 
        "--conversation", "-c",
        help="Resume existing conversation by ID"
    ),
    system_prompt: Optional[str] = typer.Option(
        None,
        "--system",
        help="System prompt to initialize the conversation"
    )
):
    """Start an interactive chat session with the AI assistant."""
    client, formatter = get_client_and_formatter()
    
    # Generate conversation ID if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    formatter.print_info(f"Starting interactive session (ID: {conversation_id[:8]}...)")
    
    if system_prompt:
        formatter.print_info(f"System prompt: {system_prompt}")
    
    console.print(Panel.fit(
        "[bold blue]Kartavya AI Assistant[/bold blue]\n\n"
        "💬 Ask questions about security events, threats, or SIEM operations\n"
        "🔍 Use natural language to query your security data\n"
        "📊 Get insights and recommendations for threat hunting\n\n"
        "[dim]Type 'exit', 'quit', or press Ctrl+C to end the session[/dim]\n"
        "[dim]Type 'help' for available commands[/dim]",
        title="Welcome to Kartavya Chat",
        border_style="blue"
    ))
    
    try:
        while True:
            try:
                # Get user input
                message = questionary.text(
                    "You:",
                    style=questionary.Style([
                        ('question', 'fg:#5f87d7 bold'),
                        ('text', 'fg:#ffffff'),
                    ])
                ).ask()
                
                if not message:
                    continue
                
                message = message.strip()
                
                # Handle special commands
                if message.lower() in ['exit', 'quit', 'bye']:
                    formatter.print_info("Goodbye! 👋")
                    break
                elif message.lower() in ['help', '?']:
                    _show_help()
                    continue
                elif message.lower() == 'clear':
                    console.clear()
                    continue
                elif message.lower().startswith('save'):
                    _save_conversation(client, conversation_id, message)
                    continue
                elif message.lower() == 'history':
                    _show_history(client, conversation_id)
                    continue
                
                # Send message to assistant
                with console.status("[bold blue]Assistant is thinking..."):
                    try:
                        response = client.chat_with_assistant(
                            message=message,
                            conversation_id=conversation_id
                        )
                        
                        assistant_response = response.get('response', 'No response received')
                        
                        # Display response
                        console.print("\n[bold green]Assistant:[/bold green]")
                        
                        # Try to render as markdown if it looks like structured content
                        if any(marker in assistant_response for marker in ['##', '**', '```', '- ']):
                            console.print(Markdown(assistant_response))
                        else:
                            console.print(assistant_response)
                        
                        # Show additional context if available
                        if response.get('context'):
                            console.print(f"\n[dim]Context: {response['context']}[/dim]")
                        
                        if response.get('confidence'):
                            console.print(f"[dim]Confidence: {response['confidence']:.2%}[/dim]")
                            
                        console.print()  # Add spacing
                        
                    except APIError as e:
                        formatter.print_error(f"Failed to get response: {e.message}")
                        if e.response_data and 'detail' in e.response_data:
                            console.print(f"[dim]{e.response_data['detail']}[/dim]")
                    except Exception as e:
                        formatter.print_error(f"Unexpected error: {str(e)}")
                
            except KeyboardInterrupt:
                formatter.print_info("\nSession interrupted. Goodbye! 👋")
                break
            except EOFError:
                formatter.print_info("\nSession ended. Goodbye! 👋")
                break
                
    except KeyboardInterrupt:
        formatter.print_info("\nGoodbye! 👋")
    finally:
        client.close()

@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask the assistant"),
    conversation_id: Optional[str] = typer.Option(
        None, 
        "--conversation", "-c",
        help="Conversation ID to maintain context"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json, markdown)"
    ),
    stream: bool = typer.Option(
        False,
        "--stream", "-s",
        help="Stream the response in real-time"
    )
):
    """Ask a single question to the AI assistant."""
    client, formatter = get_client_and_formatter()
    
    try:
        if stream:
            _stream_response(client, question, conversation_id)
        else:
            with console.status("[bold blue]Getting response..."):
                response = client.chat_with_assistant(
                    message=question,
                    conversation_id=conversation_id
                )
            
            assistant_response = response.get('response', 'No response received')
            
            if format == "json":
                formatter.print_json(response, "Assistant Response")
            elif format == "markdown":
                console.print(Markdown(assistant_response))
            else:
                console.print(Panel.fit(
                    assistant_response,
                    title="💬 Assistant Response",
                    border_style="green"
                ))
                
                # Show metadata if available
                metadata = {}
                if response.get('context'):
                    metadata['Context'] = response['context']
                if response.get('confidence'):
                    metadata['Confidence'] = f"{response['confidence']:.2%}"
                if response.get('conversation_id'):
                    metadata['Conversation ID'] = response['conversation_id']
                
                if metadata:
                    formatter.print_data(metadata, "table", "Metadata")
                    
    except APIError as e:
        formatter.print_error(f"Failed to get response: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def history(
    conversation_id: str = typer.Argument(..., help="Conversation ID to retrieve"),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json)"
    ),
    limit: int = typer.Option(
        50,
        "--limit", "-n",
        help="Maximum number of messages to show"
    )
):
    """Show conversation history."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Fetching conversation history..."):
            messages = client.get_conversation_history(conversation_id)
        
        if not messages:
            formatter.print_warning("No messages found for this conversation")
            return
        
        # Limit messages if requested
        if limit > 0:
            messages = messages[-limit:]
        
        if format == "json":
            formatter.print_json(messages, f"Conversation History ({conversation_id[:8]}...)")
        else:
            # Create a formatted table
            history_data = []
            for i, msg in enumerate(messages, 1):
                history_data.append({
                    "#": i,
                    "Role": msg.get('role', 'unknown').title(),
                    "Message": msg.get('content', '')[:100] + ("..." if len(msg.get('content', '')) > 100 else ""),
                    "Timestamp": msg.get('timestamp', 'N/A')
                })
            
            formatter.print_data(
                history_data, 
                "table", 
                f"💬 Conversation History ({conversation_id[:8]}...)"
            )
            
    except APIError as e:
        formatter.print_error(f"Failed to get conversation history: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

def _stream_response(client: APIClient, question: str, conversation_id: Optional[str]):
    """Stream response from the assistant."""
    try:
        response_stream = client.stream_chat_response(question, conversation_id)
        
        console.print("[bold green]Assistant:[/bold green]")
        
        # Use Rich Live for streaming output
        accumulated_response = ""
        with Live(console=console, refresh_per_second=10) as live:
            try:
                for line in response_stream.iter_lines():
                    if line:
                        try:
                            # Parse streaming response (assuming SSE format)
                            if line.startswith(b"data: "):
                                data = json.loads(line[6:])
                                chunk = data.get('content', '')
                                accumulated_response += chunk
                                
                                # Update live display
                                live.update(Text(accumulated_response))
                                
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                console.print(f"\n[red]Streaming error: {str(e)}[/red]")
        
        console.print()  # Add final newline
        
    except Exception as e:
        console.print(f"[red]Failed to stream response: {str(e)}[/red]")
        # Fallback to regular response
        response = client.chat_with_assistant(question, conversation_id)
        console.print(response.get('response', 'No response received'))

def _show_help():
    """Show available commands in interactive mode."""
    help_text = """
[bold blue]Available Commands:[/bold blue]

• [cyan]help, ?[/cyan] - Show this help message
• [cyan]clear[/cyan] - Clear the screen
• [cyan]history[/cyan] - Show current conversation history
• [cyan]save <filename>[/cyan] - Save conversation to file
• [cyan]exit, quit, bye[/cyan] - Exit the chat session

[bold blue]Tips:[/bold blue]

• Ask about security events, threats, or SIEM operations
• Use natural language queries like "Show me failed login attempts from last hour"
• Request analysis: "Analyze this IP address: 192.168.1.100"
• Get recommendations: "What should I investigate for potential threats?"
"""
    console.print(Panel(help_text, title="Help", border_style="yellow"))

def _save_conversation(client: APIClient, conversation_id: str, command: str):
    """Save conversation to file."""
    try:
        parts = command.split()
        filename = parts[1] if len(parts) > 1 else f"conversation_{conversation_id[:8]}.json"
        
        messages = client.get_conversation_history(conversation_id)
        
        with open(filename, 'w') as f:
            json.dump({
                'conversation_id': conversation_id,
                'messages': messages,
                'saved_at': str(typer.get_current_time())
            }, f, indent=2, default=str)
        
        console.print(f"[green]✓[/green] Conversation saved to {filename}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to save conversation: {str(e)}")

def _show_history(client: APIClient, conversation_id: str):
    """Show conversation history in interactive mode."""
    try:
        messages = client.get_conversation_history(conversation_id)
        
        if not messages:
            console.print("[dim]No previous messages in this conversation[/dim]")
            return
        
        console.print("\n[bold blue]Conversation History:[/bold blue]")
        for i, msg in enumerate(messages[-10:], 1):  # Show last 10 messages
            role = msg.get('role', 'unknown').title()
            content = msg.get('content', '')[:100]
            if len(msg.get('content', '')) > 100:
                content += "..."
            
            style = "green" if role == "Assistant" else "blue"
            console.print(f"[{style}]{i}. {role}:[/{style}] {content}")
        
        if len(messages) > 10:
            console.print(f"[dim]... and {len(messages) - 10} more messages[/dim]")
        
        console.print()
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get history: {str(e)}")

if __name__ == "__main__":
    app()

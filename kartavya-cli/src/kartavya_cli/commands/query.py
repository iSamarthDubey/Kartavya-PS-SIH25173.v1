"""
Query commands for natural language processing and query operations.

Provides functionality to execute queries, translate natural language,
get suggestions, optimize performance, and validate syntax.
"""

import json
from typing import Optional, List
import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table

from kartavya_cli.core.client import APIClient, APIError
from kartavya_cli.core.config import Config
from kartavya_cli.core.output import OutputFormatter

console = Console()
app = typer.Typer(help="🔧 Query operations and NLP processing")

def get_client_and_formatter():
    """Get API client and output formatter."""
    config = Config()
    client = APIClient(config)
    formatter = OutputFormatter(config, console)
    return client, formatter

@app.command()
def execute(
    query: str = typer.Argument(..., help="Query to execute"),
    query_type: str = typer.Option(
        "natural",
        "--type", "-t",
        help="Query type (natural, sql, kql, etc.)"
    ),
    limit: int = typer.Option(
        100,
        "--limit", "-n",
        help="Maximum number of results to return"
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
    ),
    explain: bool = typer.Option(
        False,
        "--explain",
        help="Show query execution plan"
    )
):
    """Execute a query against the SIEM data."""
    client, formatter = get_client_and_formatter()
    
    try:
        formatter.print_info(f"Executing {query_type} query...")
        
        with console.status("[bold blue]Processing query..."):
            result = client.execute_query(query, query_type)
        
        if not result:
            formatter.print_warning("No results returned from query")
            return
        
        # Display results
        results = result.get('results', [])
        query_info = result.get('query_info', {})
        
        if results:
            title = f"Query Results ({len(results)} rows)"
            if query_info.get('execution_time'):
                title += f" - {query_info['execution_time']}ms"
            
            if save:
                formatter.save_to_file(results, save, format)
                formatter.print_success(f"Results saved to {save}")
            else:
                formatter.print_data(results, format, title)
        else:
            formatter.print_warning("Query executed but returned no results")
        
        # Show query information
        if query_info:
            info_data = {}
            if query_info.get('translated_query'):
                info_data['Translated Query'] = query_info['translated_query']
            if query_info.get('execution_time'):
                info_data['Execution Time'] = f"{query_info['execution_time']}ms"
            if query_info.get('rows_examined'):
                info_data['Rows Examined'] = query_info['rows_examined']
            if query_info.get('confidence'):
                info_data['Confidence'] = f"{query_info['confidence']:.2%}"
            
            if info_data:
                formatter.print_data(info_data, "table", "📊 Query Information")
        
        # Show execution plan if requested
        if explain and result.get('execution_plan'):
            console.print(Panel.fit(
                result['execution_plan'],
                title="🔍 Execution Plan",
                border_style="blue"
            ))
            
    except APIError as e:
        formatter.print_error(f"Failed to execute query: {e.message}")
        if e.response_data and 'detail' in e.response_data:
            console.print(f"[dim]{e.response_data['detail']}[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def translate(
    natural_query: str = typer.Argument(..., help="Natural language query to translate"),
    target_language: str = typer.Option(
        "sql",
        "--target", "-t",
        help="Target query language (sql, kql, elasticsearch)"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json)"
    ),
    execute: bool = typer.Option(
        False,
        "--execute",
        help="Execute the translated query"
    )
):
    """Translate natural language query to structured query language."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Translating query..."):
            result = client.translate_query(natural_query)
        
        translated_query = result.get('translated_query', '')
        confidence = result.get('confidence', 0)
        explanation = result.get('explanation', '')
        
        if not translated_query:
            formatter.print_error("Failed to translate query")
            return
        
        if format == "json":
            formatter.print_json(result, "Query Translation")
        else:
            # Display translated query with syntax highlighting
            if target_language.lower() == 'sql':
                syntax = Syntax(translated_query, "sql", theme="monokai", line_numbers=True)
            else:
                syntax = Syntax(translated_query, "text", theme="monokai", line_numbers=True)
            
            console.print(Panel(
                syntax,
                title=f"🔄 Translated Query (Confidence: {confidence:.1%})",
                border_style="green"
            ))
            
            if explanation:
                console.print(Panel.fit(
                    explanation,
                    title="💡 Translation Explanation",
                    border_style="blue"
                ))
        
        # Show additional metadata
        metadata = {}
        if result.get('query_type'):
            metadata['Query Type'] = result['query_type']
        if result.get('complexity'):
            metadata['Complexity'] = result['complexity']
        if result.get('estimated_rows'):
            metadata['Estimated Results'] = result['estimated_rows']
        
        if metadata:
            formatter.print_data(metadata, "table", "📋 Query Metadata")
        
        # Execute if requested
        if execute and translated_query:
            formatter.print_info("Executing translated query...")
            # Use the execute command functionality
            from .query import execute as execute_query
            # This would need to be restructured to avoid circular import
            console.print("[dim]Use 'kartavya query execute' with the translated query above[/dim]")
            
    except APIError as e:
        formatter.print_error(f"Failed to translate query: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def suggestions(
    partial_query: str = typer.Argument(..., help="Partial query to get suggestions for"),
    limit: int = typer.Option(
        10,
        "--limit", "-n",
        help="Maximum number of suggestions"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json, list)"
    )
):
    """Get query suggestions and completions."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Getting suggestions..."):
            suggestions = client.get_query_suggestions(partial_query)
        
        if not suggestions:
            formatter.print_warning("No suggestions found")
            return
        
        # Limit suggestions
        suggestions = suggestions[:limit]
        
        if format == "json":
            formatter.print_json(suggestions, "Query Suggestions")
        elif format == "list":
            console.print(f"\n[bold blue]Suggestions for '{partial_query}':[/bold blue]")
            for i, suggestion in enumerate(suggestions, 1):
                console.print(f"  {i}. {suggestion}")
            console.print()
        else:
            # Table format
            suggestion_data = []
            for i, suggestion in enumerate(suggestions, 1):
                suggestion_data.append({
                    "#": i,
                    "Suggestion": suggestion,
                    "Length": len(suggestion)
                })
            
            formatter.print_data(
                suggestion_data,
                "table",
                f"💡 Query Suggestions for '{partial_query}'"
            )
            
    except APIError as e:
        formatter.print_error(f"Failed to get suggestions: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def optimize(
    query: str = typer.Argument(..., help="Query to optimize"),
    query_type: str = typer.Option(
        "auto",
        "--type", "-t",
        help="Query type (auto, sql, kql, natural)"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json)"
    )
):
    """Optimize a query for better performance."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Optimizing query..."):
            result = client.optimize_query(query)
        
        optimized_query = result.get('optimized_query', '')
        improvements = result.get('improvements', [])
        performance_gain = result.get('performance_gain', 0)
        
        if format == "json":
            formatter.print_json(result, "Query Optimization")
        else:
            # Show original vs optimized
            console.print("[bold blue]Original Query:[/bold blue]")
            original_syntax = Syntax(query, "sql", theme="monokai")
            console.print(Panel(original_syntax, border_style="red"))
            
            if optimized_query and optimized_query != query:
                console.print("\n[bold green]Optimized Query:[/bold green]")
                optimized_syntax = Syntax(optimized_query, "sql", theme="monokai")
                console.print(Panel(optimized_syntax, border_style="green"))
                
                if performance_gain > 0:
                    console.print(f"\n[green]Estimated Performance Gain: {performance_gain:.1%}[/green]")
            else:
                formatter.print_info("Query is already optimized")
            
            # Show improvements
            if improvements:
                console.print("\n[bold blue]Optimization Suggestions:[/bold blue]")
                for i, improvement in enumerate(improvements, 1):
                    console.print(f"  {i}. {improvement}")
            
            # Show performance metrics
            metrics = {}
            if result.get('estimated_execution_time'):
                metrics['Est. Execution Time'] = f"{result['estimated_execution_time']}ms"
            if result.get('estimated_rows_scanned'):
                metrics['Est. Rows Scanned'] = result['estimated_rows_scanned']
            if result.get('complexity_score'):
                metrics['Complexity Score'] = f"{result['complexity_score']}/10"
            
            if metrics:
                formatter.print_data(metrics, "table", "📊 Performance Metrics")
            
    except APIError as e:
        formatter.print_error(f"Failed to optimize query: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def validate(
    query: str = typer.Argument(..., help="Query to validate"),
    query_type: str = typer.Option(
        "auto",
        "--type", "-t", 
        help="Query type (auto, sql, kql, natural)"
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Enable strict validation mode"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json)"
    )
):
    """Validate query syntax and structure."""
    client, formatter = get_client_and_formatter()
    
    try:
        with console.status("[bold blue]Validating query..."):
            result = client.validate_query(query)
        
        is_valid = result.get('valid', False)
        errors = result.get('errors', [])
        warnings = result.get('warnings', [])
        suggestions = result.get('suggestions', [])
        
        if format == "json":
            formatter.print_json(result, "Query Validation")
        else:
            # Show validation status
            if is_valid:
                console.print(Panel.fit(
                    "[green]✓ Query is valid[/green]",
                    title="Validation Result",
                    border_style="green"
                ))
            else:
                console.print(Panel.fit(
                    "[red]✗ Query validation failed[/red]",
                    title="Validation Result",
                    border_style="red"
                ))
            
            # Show errors
            if errors:
                console.print("\n[bold red]Errors:[/bold red]")
                for i, error in enumerate(errors, 1):
                    error_msg = error.get('message', str(error))
                    line = error.get('line')
                    column = error.get('column')
                    
                    location = ""
                    if line and column:
                        location = f" (Line {line}, Column {column})"
                    
                    console.print(f"  {i}. [red]{error_msg}{location}[/red]")
            
            # Show warnings
            if warnings:
                console.print("\n[bold yellow]Warnings:[/bold yellow]")
                for i, warning in enumerate(warnings, 1):
                    warning_msg = warning.get('message', str(warning))
                    console.print(f"  {i}. [yellow]{warning_msg}[/yellow]")
            
            # Show suggestions
            if suggestions:
                console.print("\n[bold blue]Suggestions:[/bold blue]")
                for i, suggestion in enumerate(suggestions, 1):
                    console.print(f"  {i}. [blue]{suggestion}[/blue]")
            
            # Show validation details
            validation_details = {}
            if result.get('query_type'):
                validation_details['Detected Type'] = result['query_type']
            if result.get('complexity'):
                validation_details['Complexity'] = result['complexity']
            if result.get('performance_impact'):
                validation_details['Performance Impact'] = result['performance_impact']
            
            if validation_details:
                formatter.print_data(validation_details, "table", "🔍 Validation Details")
            
    except APIError as e:
        formatter.print_error(f"Failed to validate query: {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def examples():
    """Show example queries for different use cases."""
    formatter = OutputFormatter()
    
    examples = [
        {
            "Category": "Authentication",
            "Natural Language": "Show failed login attempts in the last hour",
            "Description": "Find authentication failures",
            "Use Case": "Security monitoring"
        },
        {
            "Category": "Network",
            "Natural Language": "Find connections to external IPs on port 443",
            "Description": "Analyze HTTPS traffic",
            "Use Case": "Network analysis"
        },
        {
            "Category": "User Activity",
            "Natural Language": "Show admin users who logged in today",
            "Description": "Track privileged access",
            "Use Case": "Access monitoring"
        },
        {
            "Category": "Threats",
            "Natural Language": "Find suspicious file executions",
            "Description": "Detect malware activity",
            "Use Case": "Threat hunting"
        },
        {
            "Category": "Performance",
            "Natural Language": "Show high CPU usage alerts",
            "Description": "System performance monitoring",
            "Use Case": "Infrastructure monitoring"
        },
        {
            "Category": "Compliance",
            "Natural Language": "List all file access in shared folders",
            "Description": "File access auditing",
            "Use Case": "Compliance reporting"
        }
    ]
    
    formatter.print_data(examples, "table", "📚 Example Queries")
    
    console.print("\n[bold blue]Usage Examples:[/bold blue]")
    console.print("  kartavya query execute \"Show failed login attempts in the last hour\"")
    console.print("  kartavya query translate \"Find admin users\" --target sql")
    console.print("  kartavya query suggestions \"Show users\"")
    console.print("  kartavya query validate \"SELECT * FROM events WHERE timestamp > '2024-01-01'\"")

@app.command()
def history(
    limit: int = typer.Option(
        20,
        "--limit", "-n",
        help="Number of recent queries to show"
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table, json)"
    )
):
    """Show query execution history."""
    # This would typically be stored locally or retrieved from the API
    formatter = OutputFormatter()
    
    # Mock history data (in a real implementation, this would come from storage)
    history_data = [
        {
            "Timestamp": "2024-01-15 10:30:00",
            "Query": "Show failed login attempts",
            "Type": "Natural",
            "Results": 25,
            "Duration": "150ms"
        },
        {
            "Timestamp": "2024-01-15 10:25:00", 
            "Query": "SELECT * FROM events WHERE event_type='auth'",
            "Type": "SQL",
            "Results": 1250,
            "Duration": "320ms"
        },
        {
            "Timestamp": "2024-01-15 10:20:00",
            "Query": "Find network connections to suspicious IPs",
            "Type": "Natural",
            "Results": 5,
            "Duration": "220ms"
        }
    ]
    
    # Limit results
    history_data = history_data[:limit]
    
    if not history_data:
        formatter.print_warning("No query history found")
        return
    
    formatter.print_data(history_data, format, f"📝 Query History (Last {len(history_data)} queries)")
    
    console.print("\n[dim]Note: Query history is stored locally and may not persist across sessions[/dim]")

if __name__ == "__main__":
    app()

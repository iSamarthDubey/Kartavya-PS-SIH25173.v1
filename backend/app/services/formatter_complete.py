"""
Kartavya Response Formatter - Complete Implementation
Formats SIEM results for different output types
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime


# --- From backend/response_formatter/formatter.py ---
"""
Response Formatter for SIEM Query Results
Converts raw Elasticsearch results into formatted tables and visualizations.
"""

import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from dataclasses import dataclass
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


@dataclass
class FormattedResponse:
    """Represents a formatted response."""
    query: str
    intent: str
    summary: str
    table_data: Optional[pd.DataFrame] = None
    chart_data: Optional[str] = None  # Base64 encoded chart
    raw_count: int = 0
    aggregations: Optional[Dict[str, Any]] = None
    recommendations: List[str] = None


class ResponseFormatter:
    """Formats Elasticsearch query results for display."""
    
    def __init__(self):
        """Initialize the response formatter."""
        # Set matplotlib to use a non-interactive backend
        plt.switch_backend('Agg')
        sns.set_style("whitegrid")
        
        # Column mappings for different data types
        self.column_mappings = {
            'timestamp': ['@timestamp', 'timestamp', 'time'],
            'source_ip': ['source.ip', 'src_ip', 'source_address'],
            'dest_ip': ['destination.ip', 'dest_ip', 'dst_ip', 'destination_address'],
            'username': ['user.name', 'username', 'user', 'account'],
            'hostname': ['host.name', 'hostname', 'computer_name'],
            'event_id': ['winlog.event_id', 'event.code', 'event_id'],
            'message': ['message', 'description', 'event_description'],
            'severity': ['event.severity', 'severity', 'level'],
            'process': ['process.name', 'process_name', 'executable'],
            'port': ['source.port', 'destination.port', 'port'],
            'protocol': ['network.protocol', 'protocol']
        }
    
    def format_response(self, query: str, intent: str, results: List[Dict[str, Any]], 
                       aggregations: Optional[Dict[str, Any]] = None) -> FormattedResponse:
        """
        Format query results into a structured response.
        
        Args:
            query: Original natural language query
            intent: Classified intent
            results: Raw Elasticsearch results
            aggregations: Aggregation results if any
            
        Returns:
            FormattedResponse object
        """
        logger.info(f"Formatting {len(results)} results for intent: {intent}")
        
        # Generate summary
        summary = self._generate_summary(query, intent, results, aggregations)
        
        # Convert to DataFrame for easier manipulation
        df = self._results_to_dataframe(results, intent)
        
        # Generate chart if applicable
        chart_data = None
        if len(results) > 0 and self._should_generate_chart(intent):
            chart_data = self._generate_chart(df, intent, aggregations)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(intent, results, aggregations)
        
        return FormattedResponse(
            query=query,
            intent=intent,
            summary=summary,
            table_data=df,
            chart_data=chart_data,
            raw_count=len(results),
            aggregations=aggregations,
            recommendations=recommendations
        )
    
    def _generate_summary(self, query: str, intent: str, results: List[Dict[str, Any]], 
                         aggregations: Optional[Dict[str, Any]]) -> str:
        """Generate a human-readable summary of the results."""
        count = len(results)
        
        if count == 0:
            return f"No results found for query: '{query}'"
        
        # Intent-specific summaries
        if intent == "show_failed_logins":
            unique_users = len(set(self._extract_field(results, 'username')))
            unique_ips = len(set(self._extract_field(results, 'source_ip')))
            summary = (f"Found {count} failed login attempts. "
                      f"Affected {unique_users} unique users from {unique_ips} unique IP addresses.")
            
        elif intent == "show_successful_logins":
            unique_users = len(set(self._extract_field(results, 'username')))
            summary = (f"Found {count} successful login events for {unique_users} unique users.")
            
        elif intent == "security_alerts":
            summary = f"Found {count} security alerts. Review high-priority alerts immediately."
            
        elif intent == "network_traffic":
            unique_ips = len(set(self._extract_field(results, 'source_ip') + 
                                self._extract_field(results, 'dest_ip')))
            summary = f"Found {count} network events involving {unique_ips} unique IP addresses."
            
        elif intent == "system_errors":
            summary = f"Found {count} system errors. Investigate critical errors first."
            
        else:
            summary = f"Found {count} matching log entries for your query."
        
        # Add time range if available
        if results:
            timestamps = self._extract_field(results, 'timestamp')
            if timestamps:
                try:
                    times = [datetime.fromisoformat(ts.replace('Z', '+00:00')) 
                            for ts in timestamps if ts]
                    if times:
                        earliest = min(times)
                        latest = max(times)
                        summary += f" Time range: {earliest.strftime('%Y-%m-%d %H:%M')} to {latest.strftime('%Y-%m-%d %H:%M')}."
                except:
                    pass
        
        return summary
    
    def _results_to_dataframe(self, results: List[Dict[str, Any]], intent: str) -> pd.DataFrame:
        """Convert results to a formatted DataFrame."""
        if not results:
            return pd.DataFrame()
        
        # Determine which columns to include based on intent
        columns = self._get_relevant_columns(intent)
        
        # Extract data for each column
        data = {}
        for col_name, field_names in columns.items():
            values = []
            for result in results:
                value = self._extract_value_from_result(result, field_names)
                values.append(value)
            data[col_name.replace('_', ' ').title()] = values
        
        df = pd.DataFrame(data)
        
        # Format timestamp columns
        for col in df.columns:
            if 'timestamp' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
        
        # Limit rows for display
        if len(df) > 100:
            df = df.head(100)
        
        return df
    
    def _get_relevant_columns(self, intent: str) -> Dict[str, List[str]]:
        """Get relevant columns based on intent."""
        base_columns = {
            'timestamp': self.column_mappings['timestamp'],
            'message': self.column_mappings['message']
        }
        
        if intent in ["show_failed_logins", "show_successful_logins"]:
            return {
                **base_columns,
                'username': self.column_mappings['username'],
                'source_ip': self.column_mappings['source_ip'],
                'hostname': self.column_mappings['hostname'],
                'event_id': self.column_mappings['event_id']
            }
            
        elif intent == "security_alerts":
            return {
                **base_columns,
                'severity': self.column_mappings['severity'],
                'hostname': self.column_mappings['hostname'],
                'source_ip': self.column_mappings['source_ip']
            }
            
        elif intent == "network_traffic":
            return {
                **base_columns,
                'source_ip': self.column_mappings['source_ip'],
                'dest_ip': self.column_mappings['dest_ip'],
                'port': self.column_mappings['port'],
                'protocol': self.column_mappings['protocol']
            }
            
        elif intent == "system_errors":
            return {
                **base_columns,
                'hostname': self.column_mappings['hostname'],
                'severity': self.column_mappings['severity'],
                'process': self.column_mappings['process']
            }
            
        else:
            # Default columns for general search
            return {
                **base_columns,
                'hostname': self.column_mappings['hostname'],
                'source_ip': self.column_mappings['source_ip']
            }
    
    def _extract_value_from_result(self, result: Dict[str, Any], field_names: List[str]) -> str:
        """Extract value from result using field name priority."""
        for field_name in field_names:
            value = self._get_nested_field(result, field_name)
            if value is not None:
                return str(value)
        return ""
    
    def _get_nested_field(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get nested field value using dot notation."""
        try:
            keys = field_path.split('.')
            value = data
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            return value
        except:
            return None
    
    def _extract_field(self, results: List[Dict[str, Any]], field_type: str) -> List[str]:
        """Extract all values for a specific field type."""
        values = []
        field_names = self.column_mappings.get(field_type, [])
        
        for result in results:
            value = self._extract_value_from_result(result, field_names)
            if value and value != "":
                values.append(value)
        
        return values
    
    def _should_generate_chart(self, intent: str) -> bool:
        """Determine if a chart should be generated for this intent."""
        chart_intents = [
            "show_failed_logins",
            "show_successful_logins", 
            "security_alerts",
            "network_traffic",
            "system_errors"
        ]
        return intent in chart_intents
    
    def _generate_chart(self, df: pd.DataFrame, intent: str, 
                       aggregations: Optional[Dict[str, Any]]) -> Optional[str]:
        """Generate a chart based on the data and intent."""
        if df.empty:
            return None
        
        try:
            plt.figure(figsize=(12, 8))
            
            if intent in ["show_failed_logins", "show_successful_logins"]:
                self._create_login_chart(df, intent)
            elif intent == "security_alerts":
                self._create_security_chart(df, aggregations)
            elif intent == "network_traffic":
                self._create_network_chart(df, aggregations)
            elif intent == "system_errors":
                self._create_error_chart(df)
            else:
                self._create_timeline_chart(df)
            
            # Save to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_b64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_b64
            
        except Exception as e:
            logger.error(f"Failed to generate chart: {e}")
            return None
    
    def _create_login_chart(self, df: pd.DataFrame, intent: str):
        """Create login-specific charts."""
        plt.subplot(2, 2, 1)
        
        # Timeline
        if 'Timestamp' in df.columns:
            try:
                df['Hour'] = pd.to_datetime(df['Timestamp']).dt.hour
                hourly_counts = df['Hour'].value_counts().sort_index()
                plt.plot(hourly_counts.index, hourly_counts.values)
                plt.title(f"{'Failed' if 'failed' in intent else 'Successful'} Logins by Hour")
                plt.xlabel("Hour of Day")
                plt.ylabel("Count")
            except:
                pass
        
        # Top IPs
        plt.subplot(2, 2, 2)
        if 'Source Ip' in df.columns:
            top_ips = df['Source Ip'].value_counts().head(10)
            if not top_ips.empty:
                plt.barh(range(len(top_ips)), top_ips.values)
                plt.yticks(range(len(top_ips)), top_ips.index)
                plt.title("Top Source IPs")
                plt.xlabel("Count")
        
        # Top Users
        plt.subplot(2, 2, 3)
        if 'Username' in df.columns:
            top_users = df['Username'].value_counts().head(10)
            if not top_users.empty:
                plt.barh(range(len(top_users)), top_users.values)
                plt.yticks(range(len(top_users)), top_users.index)
                plt.title("Top Users")
                plt.xlabel("Count")
        
        plt.tight_layout()
    
    def _create_security_chart(self, df: pd.DataFrame, aggregations: Optional[Dict[str, Any]]):
        """Create security alert charts."""
        if aggregations and 'severity_breakdown' in aggregations:
            severity_data = aggregations['severity_breakdown']['buckets']
            severities = [bucket['key'] for bucket in severity_data]
            counts = [bucket['doc_count'] for bucket in severity_data]
            
            plt.pie(counts, labels=severities, autopct='%1.1f%%')
            plt.title("Security Alerts by Severity")
        else:
            # Fallback to simple timeline
            self._create_timeline_chart(df)
    
    def _create_network_chart(self, df: pd.DataFrame, aggregations: Optional[Dict[str, Any]]):
        """Create network traffic charts."""
        plt.subplot(2, 2, 1)
        
        # Protocol distribution
        if aggregations and 'protocols' in aggregations:
            protocol_data = aggregations['protocols']['buckets']
            protocols = [bucket['key'] for bucket in protocol_data]
            counts = [bucket['doc_count'] for bucket in protocol_data]
            
            plt.pie(counts, labels=protocols, autopct='%1.1f%%')
            plt.title("Traffic by Protocol")
        
        # Top source IPs
        plt.subplot(2, 2, 2)
        if 'Source Ip' in df.columns:
            top_ips = df['Source Ip'].value_counts().head(10)
            if not top_ips.empty:
                plt.barh(range(len(top_ips)), top_ips.values)
                plt.yticks(range(len(top_ips)), top_ips.index)
                plt.title("Top Source IPs")
        
        plt.tight_layout()
    
    def _create_error_chart(self, df: pd.DataFrame):
        """Create system error charts."""
        # Error timeline
        self._create_timeline_chart(df)
    
    def _create_timeline_chart(self, df: pd.DataFrame):
        """Create a basic timeline chart."""
        if 'Timestamp' in df.columns:
            try:
                df['Hour'] = pd.to_datetime(df['Timestamp']).dt.floor('H')
                hourly_counts = df.groupby('Hour').size()
                
                plt.plot(hourly_counts.index, hourly_counts.values, marker='o')
                plt.title("Events Over Time")
                plt.xlabel("Time")
                plt.ylabel("Count")
                plt.xticks(rotation=45)
            except Exception as e:
                logger.error(f"Timeline chart error: {e}")
                plt.text(0.5, 0.5, "Unable to generate timeline", 
                        ha='center', va='center', transform=plt.gca().transAxes)
    
    def _generate_recommendations(self, intent: str, results: List[Dict[str, Any]], 
                                 aggregations: Optional[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations based on results."""
        recommendations = []
        
        if not results:
            return ["No events found. Consider broadening your search criteria."]
        
        count = len(results)
        
        if intent == "show_failed_logins":
            if count > 10:
                recommendations.append("⚠️ High number of failed login attempts detected. Consider reviewing security policies.")
            
            # Check for brute force patterns
            usernames = self._extract_field(results, 'username')
            source_ips = self._extract_field(results, 'source_ip')
            
            if usernames:
                user_counts = {}
                for user in usernames:
                    user_counts[user] = user_counts.get(user, 0) + 1
                max_user_failures = max(user_counts.values())
                if max_user_failures > 5:
                    recommendations.append(f"🔒 User account with {max_user_failures} failed attempts may be under attack.")
            
            if source_ips:
                ip_counts = {}
                for ip in source_ips:
                    ip_counts[ip] = ip_counts.get(ip, 0) + 1
                max_ip_failures = max(ip_counts.values())
                if max_ip_failures > 10:
                    recommendations.append(f"🚫 Consider blocking IP with {max_ip_failures} failed attempts.")
        
        elif intent == "security_alerts":
            recommendations.append("🔍 Review all high and critical severity alerts immediately.")
            recommendations.append("📊 Check for patterns in alert timing and sources.")
            
        elif intent == "system_errors":
            recommendations.append("🔧 Investigate critical and error-level events first.")
            recommendations.append("📈 Monitor error trends to identify recurring issues.")
            
        elif intent == "network_traffic":
            recommendations.append("🌐 Review unusual traffic patterns and unknown destinations.")
            recommendations.append("🔒 Verify that high-volume connections are legitimate.")
        
        # General recommendations
        if count > 1000:
            recommendations.append("📋 Large result set detected. Consider filtering by time or specific criteria.")
        
        recommendations.append("💾 Export results for detailed analysis if needed.")
        
        return recommendations
    
    def to_json(self, response: FormattedResponse) -> str:
        """Convert formatted response to JSON string."""
        data = {
            "query": response.query,
            "intent": response.intent,
            "summary": response.summary,
            "raw_count": response.raw_count,
            "recommendations": response.recommendations,
            "aggregations": response.aggregations
        }
        
        if response.table_data is not None and not response.table_data.empty:
            data["table_data"] = response.table_data.to_dict(orient='records')
        
        if response.chart_data:
            data["chart_data"] = response.chart_data
        
        return json.dumps(data, indent=2, default=str)
    
    def to_html(self, response: FormattedResponse) -> str:
        """Convert formatted response to HTML string."""
        html_parts = [
            f"<h2>Query Results</h2>",
            f"<p><strong>Query:</strong> {response.query}</p>",
            f"<p><strong>Intent:</strong> {response.intent}</p>",
            f"<div class='summary'><h3>Summary</h3><p>{response.summary}</p></div>"
        ]
        
        # Add recommendations
        if response.recommendations:
            html_parts.append("<div class='recommendations'><h3>Recommendations</h3><ul>")
            for rec in response.recommendations:
                html_parts.append(f"<li>{rec}</li>")
            html_parts.append("</ul></div>")
        
        # Add table
        if response.table_data is not None and not response.table_data.empty:
            html_parts.append("<div class='table-container'><h3>Results</h3>")
            html_parts.append(response.table_data.to_html(classes='results-table', index=False))
            html_parts.append("</div>")
        
        # Add chart
        if response.chart_data:
            html_parts.append(f"<div class='chart-container'><h3>Visualization</h3>")
            html_parts.append(f"<img src='data:image/png;base64,{response.chart_data}' alt='Chart'>")
            html_parts.append("</div>")
        
        return "\n".join(html_parts)


# Example usage and testing
if __name__ == "__main__":
    formatter = ResponseFormatter()
    
    # Sample test data
    sample_results = [
        {
            "@timestamp": "2024-01-15T10:30:00Z",
            "user.name": "admin",
            "source.ip": "192.168.1.100", 
            "winlog.event_id": "4625",
            "message": "Authentication failed for user admin"
        },
        {
            "@timestamp": "2024-01-15T10:35:00Z",
            "user.name": "admin",
            "source.ip": "192.168.1.100",
            "winlog.event_id": "4625", 
            "message": "Authentication failed for user admin"
        }
    ]
    
    response = formatter.format_response(
        query="Show failed login attempts from admin user",
        intent="show_failed_logins",
        results=sample_results
    )
    
    print("Formatted Response:")
    print("=" * 50)
    print(response.summary)
    print("\nTable Data:")
    if response.table_data is not None:
        print(response.table_data.to_string())
    print("\nRecommendations:")
    for rec in response.recommendations:
        print(f"- {rec}")
# --- From backend/response_formatter/text_formatter.py ---
"""
Text formatting utilities for SIEM responses.
"""

from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class TextFormatter:
    """Format SIEM query results into human-readable text."""
    
    def __init__(self):
        """Initialize the text formatter."""
        pass
    
    def format_search_results(self, results: List[Dict[str, Any]], 
                            query: str = "") -> str:
        """Format search results into readable text."""
        if not results:
            return "No results found for your query."
        
        formatted_text = f"Found {len(results)} results"
        if query:
            formatted_text += f" for query: '{query}'"
        formatted_text += "\n\n"
        
        for i, result in enumerate(results[:10], 1):  # Limit to top 10
            formatted_text += f"Result {i}:\n"
            
            # Format timestamp
            if '@timestamp' in result:
                formatted_text += f"  Time: {result['@timestamp']}\n"
            
            # Format source
            if 'source' in result:
                formatted_text += f"  Source: {result['source']}\n"
            
            # Format message
            if 'message' in result:
                message = result['message']
                if len(message) > 200:
                    message = message[:200] + "..."
                formatted_text += f"  Message: {message}\n"
            
            # Format other fields
            for key, value in result.items():
                if key not in ['@timestamp', 'source', 'message', '_id', '_index']:
                    if isinstance(value, (str, int, float)):
                        formatted_text += f"  {key.title()}: {value}\n"
            
            formatted_text += "\n"
        
        if len(results) > 10:
            formatted_text += f"... and {len(results) - 10} more results\n"
        
        return formatted_text
    
    def format_summary(self, data: Dict[str, Any]) -> str:
        """Format summary statistics."""
        summary = "Summary:\n"
        
        for key, value in data.items():
            if isinstance(value, (int, float)):
                summary += f"  {key.title()}: {value:,}\n"
            elif isinstance(value, str):
                summary += f"  {key.title()}: {value}\n"
            elif isinstance(value, list):
                summary += f"  {key.title()}: {len(value)} items\n"
        
        return summary
    
    def format_error(self, error: str, context: str = "") -> str:
        """Format error messages."""
        error_text = "Error occurred"
        if context:
            error_text += f" while {context}"
        error_text += f": {error}"
        return error_text
# --- From backend/response_formatter/chart_formatter.py ---

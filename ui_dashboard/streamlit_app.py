"""
Streamlit web application for SIEM Assistant.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from siem_connector.elastic_connector import ElasticConnector
except ImportError as e:
    st.error(f"Failed to import ElasticConnector: {e}")
    ElasticConnector = None

try:
    from siem_connector.wazuh_connector import WazuhConnector
except ImportError as e:
    st.error(f"Failed to import WazuhConnector: {e}")
    WazuhConnector = None

try:
    from nlp_parser.parser import NLPParser
    ENHANCED_PARSER_AVAILABLE = True
except ImportError as e:
    st.error(f"Failed to import NLP parser: {e}")
    NLPParser = None
    ENHANCED_PARSER_AVAILABLE = False

try:
    from rag_pipeline.pipeline import RAGPipeline
except ImportError as e:
    st.error(f"Failed to import RAGPipeline: {e}")
    RAGPipeline = None

try:
    from context_manager.context import ContextManager
except ImportError as e:
    st.error(f"Failed to import ContextManager: {e}")
    ContextManager = None

# Import demo data generator
try:
    from ui_dashboard.demo_data import DemoDataGenerator
except ImportError:
    try:
        from demo_data import DemoDataGenerator
    except ImportError:
        DemoDataGenerator = None


def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'context_manager' not in st.session_state:
        if ContextManager:
            st.session_state.context_manager = ContextManager()
        else:
            st.session_state.context_manager = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'connectors' not in st.session_state:
        st.session_state.connectors = {
            'elasticsearch': None,
            'wazuh': None
        }


def setup_sidebar():
    """Setup the sidebar with configuration options."""
    st.sidebar.title("SIEM Configuration")
    
    # SIEM Platform Selection
    platform = st.sidebar.selectbox(
        "Select SIEM Platform",
        ["Elasticsearch", "Wazuh", "Both"]
    )
    
    # Connection Status
    st.sidebar.subheader("Connection Status")
    
    try:
        if platform in ["Elasticsearch", "Both"]:
            if ElasticConnector and st.session_state.connectors['elasticsearch'] is None:
                st.session_state.connectors['elasticsearch'] = ElasticConnector()
            if st.session_state.connectors['elasticsearch']:
                st.sidebar.success("✅ Elasticsearch Connected")
            else:
                st.sidebar.warning("⚠️ Elasticsearch: Not available")
    except Exception as e:
        st.sidebar.error(f"❌ Elasticsearch: {str(e)}")
    
    try:
        if platform in ["Wazuh", "Both"]:
            if WazuhConnector and st.session_state.connectors['wazuh'] is None:
                st.session_state.connectors['wazuh'] = WazuhConnector()
            if st.session_state.connectors['wazuh']:
                st.sidebar.success("✅ Wazuh Connected")
            else:
                st.sidebar.warning("⚠️ Wazuh: Not available")
    except Exception as e:
        st.sidebar.error(f"❌ Wazuh: {str(e)}")
    
    # Parser Selection
    st.sidebar.subheader("Parser Configuration")
    parser_type = st.sidebar.selectbox(
        "NLP Parser Type",
        ["Enhanced ML Parser", "Basic Parser"]
    )
    
    # Test parser capabilities
    if NLPParser:
        try:
            test_parser = NLPParser(use_ml=(parser_type == "Enhanced ML Parser"))
            parser_info = test_parser.get_parser_info()
            
            if parser_type == "Enhanced ML Parser" and parser_info['ml_trained']:
                st.sidebar.success("🤖 ML-enhanced parser ready")
                st.sidebar.caption(f"spaCy: {'✅' if parser_info['spacy_available'] else '❌'}")
            elif parser_type == "Enhanced ML Parser":
                st.sidebar.warning("🔄 ML parser available but not trained")
                parser_type = "Basic Parser"  # Fallback
            else:
                st.sidebar.info("📝 Using pattern-based parser")
        except Exception as e:
            st.sidebar.error(f"❌ Parser error: {str(e)}")
            parser_type = "Basic Parser"
    else:
        st.sidebar.error("❌ Parser not available")
    # Query Settings
    st.sidebar.subheader("Query Settings")
    max_results = st.sidebar.slider("Max Results", 10, 1000, 100)
    time_range = st.sidebar.selectbox(
        "Default Time Range",
        ["Last Hour", "Last 24 Hours", "Last Week", "Last Month"]
    )
    
    return platform, max_results, time_range, parser_type


def display_chat_interface(parser_type="Enhanced ML Parser"):
    """Display the main chat interface."""
    st.title("🛡️ Kartavya SIEM Assistant")
    st.markdown("Ask questions about your security logs in natural language")
    
    # Show demo mode indicator
    has_real_connection = (
        st.session_state.connectors.get('elasticsearch') or 
        st.session_state.connectors.get('wazuh')
    )
    
    if not has_real_connection:
        st.info("🎭 **Demo Mode**: No SIEM connections available. Showing demonstration data.")
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            if message['type'] == 'user':
                st.chat_message("user").write(message['content'])
            else:
                st.chat_message("assistant").write(message['content'])
    
    # Query input
    query = st.chat_input("Ask about your security logs...")
    
    if query:
        # Add user message to history
        st.session_state.chat_history.append({
            'type': 'user',
            'content': query,
            'timestamp': datetime.now()
        })
        
        # Process query
        with st.spinner("Analyzing your query..."):
            response = process_query(query, parser_type)
        
        # Add assistant response to history
        st.session_state.chat_history.append({
            'type': 'assistant',
            'content': response,
            'timestamp': datetime.now()
        })
        
        st.rerun()


def process_query(query: str, parser_type: str = "Enhanced ML Parser") -> str:
    """Process user query and return response."""
    try:
        # Check if required components are available
        if not NLPParser:
            return "❌ NLP Parser not available. Please install required dependencies."
        
        if not RAGPipeline:
            return "❌ RAG Pipeline not available. Please install required dependencies."
        
        # Initialize parser with ML capabilities
        use_ml = parser_type == "Enhanced ML Parser"
        nlp_parser = NLPParser(use_ml=use_ml)
        parsed_query = nlp_parser.parse_query(query)
        
        # Display parser results
        parser_info = nlp_parser.get_parser_info()
        confidence = parsed_query.get('confidence', 0.0)
        
        if use_ml and parser_info['ml_trained']:
            st.info(f"🤖 **Enhanced ML Parser Results:**\n"
                   f"- Confidence: {confidence:.2f}\n"
                   f"- Intent: {parsed_query['intent']}\n"
                   f"- Parser: {parsed_query['parser_type']}")
        else:
            st.info(f"⚡ **Basic Parser Results:**\n"
                   f"- Intent: {parsed_query['intent']}\n"
                   f"- Entities: {len(parsed_query.get('entities', {}))}")
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline()
        
        # Generate SIEM query using RAG
        siem_query = rag_pipeline.generate_query(parsed_query)
        
        # Execute query based on available connectors
        results = []
        
        if st.session_state.connectors['elasticsearch']:
            try:
                es_results = st.session_state.connectors['elasticsearch'].execute_query(siem_query)
                results.extend(es_results.get('hits', {}).get('hits', []))
            except Exception as e:
                st.error(f"Elasticsearch query failed: {e}")
        
        if st.session_state.connectors['wazuh']:
            try:
                wazuh_results = st.session_state.connectors['wazuh'].get_alerts()
                results.extend(wazuh_results)
            except Exception as e:
                st.error(f"Wazuh query failed: {e}")
        
        # Format and return results
        if results:
            return format_results(results, parsed_query['intent'])
        else:
            # Use demo data generator for demonstration
            if DemoDataGenerator:
                demo_gen = DemoDataGenerator()
                demo_events = demo_gen.generate_events(
                    count=random.randint(3, 8), 
                    intent=parsed_query.get('intent', 'search_logs')
                )
                return format_demo_results(demo_events, parsed_query)
            else:
                return "No results found for your query. Try adjusting your search criteria."
    
    except Exception as e:
        return f"An error occurred while processing your query: {str(e)}"


def format_demo_results(demo_events: list, parsed_query: dict) -> str:
    """Format demo results for display."""
    intent = parsed_query.get('intent', 'search_logs')
    entities = parsed_query.get('entities', {})
    
    response = f"🔍 **Query Analysis:**\n"
    response += f"- Intent: {intent}\n"
    response += f"- Entities found: {', '.join(entities.keys()) if entities else 'None'}\n\n"
    
    response += f"📊 **Demo Results:** (Found {len(demo_events)} events)\n\n"
    
    if intent == 'count_events':
        total_count = sum(event.get('count', 1) for event in demo_events)
        response += f"**Total Event Count:** {total_count}\n\n"
    
    # Display sample events
    for i, event in enumerate(demo_events[:3], 1):
        response += f"**Event {i}:**\n"
        response += f"- Timestamp: {event.get('@timestamp', 'N/A')}\n"
        response += f"- Message: {event.get('message', 'N/A')}\n"
        response += f"- Severity: {event.get('severity', 'N/A')}\n"
        response += f"- Source IP: {event.get('source_ip', 'N/A')}\n"
        response += f"- User: {event.get('user', 'N/A')}\n\n"
    
    if len(demo_events) > 3:
        response += f"... and {len(demo_events) - 3} more events\n\n"
    
    response += "💡 **Note:** This is demo data. Connect to a real SIEM platform for actual results."
    
    return response


def format_results(results: list, intent: str) -> str:
    """Format query results for display."""
    if not results:
        return "No results found."
    
    response = f"Found {len(results)} results:\n\n"
    
    if intent == 'count_events':
        response = f"Total events found: {len(results)}"
    
    elif intent == 'get_stats':
        # Generate basic statistics
        df = pd.DataFrame(results)
        if not df.empty:
            response += f"**Statistics:**\n"
            response += f"- Total records: {len(df)}\n"
            if 'severity' in df.columns:
                severity_counts = df['severity'].value_counts()
                response += f"- By severity: {dict(severity_counts)}\n"
    
    else:
        # Display first few results
        for i, result in enumerate(results[:5]):
            response += f"**Result {i+1}:**\n"
            if isinstance(result, dict):
                for key, value in list(result.items())[:5]:  # Limit fields
                    response += f"- {key}: {value}\n"
            response += "\n"
        
        if len(results) > 5:
            response += f"... and {len(results) - 5} more results"
    
    return response


def display_analytics_dashboard():
    """Display analytics dashboard."""
    st.title("📊 Security Analytics Dashboard")
    
    # Get demo data if available
    if DemoDataGenerator:
        demo_gen = DemoDataGenerator()
        stats = demo_gen.get_demo_stats()
        chart_data = demo_gen.get_demo_chart_data()
    else:
        # Fallback static data
        stats = {
            "total_events": 1234,
            "high_severity_alerts": 56,
            "active_threats": 8,
            "blocked_ips": 892
        }
        chart_data = None
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", f"{stats['total_events']:,}", "12%")
    
    with col2:
        st.metric("High Severity", stats['high_severity_alerts'], "-3%")
    
    with col3:
        st.metric("Active Threats", stats['active_threats'], "2%")
    
    with col4:
        st.metric("Blocked IPs", stats['blocked_ips'], "15%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Alert trend chart
        if chart_data:
            trend_data = chart_data['trend_data']
            fig = px.line(
                x=trend_data['dates'], 
                y=trend_data['values'], 
                title="Daily Alert Trend (Demo Data)"
            )
        else:
            # Fallback chart
            dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
            alerts = [50 + i % 10 + (i % 3) * 20 for i in range(len(dates))]
            fig = px.line(x=dates, y=alerts, title="Daily Alert Trend")
        
        fig.update_layout(xaxis_title="Date", yaxis_title="Number of Alerts")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Severity distribution
        if chart_data:
            severity_data = chart_data['severity_distribution']
            fig = px.pie(
                values=list(severity_data.values()),
                names=list(severity_data.keys()),
                title="Alert Severity Distribution (Demo)"
            )
        else:
            # Fallback pie chart
            severities = ['Low', 'Medium', 'High', 'Critical']
            counts = [150, 89, 45, 12]
            fig = px.pie(values=counts, names=severities, title="Alert Severity Distribution")
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Top threats table
    st.subheader("Top Threats")
    if chart_data and 'top_threats' in chart_data:
        threat_df = pd.DataFrame(chart_data['top_threats'])
        threat_df['Severity'] = ['Critical', 'High', 'Medium', 'High']  # Add severity column
        st.dataframe(threat_df)
    else:
        # Fallback threat data
        threat_data = {
            'Threat Type': ['Malware', 'Phishing', 'Brute Force', 'DDoS', 'SQL Injection'],
            'Count': [45, 32, 28, 15, 8],
            'Severity': ['Critical', 'High', 'Medium', 'High', 'Critical']
        }
        st.dataframe(pd.DataFrame(threat_data))


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Kartavya SIEM Assistant",
        page_icon="🛡️",
        layout="wide"
    )
    
    initialize_session_state()
    
    # Setup sidebar
    platform, max_results, time_range, parser_type = setup_sidebar()
    
    # Main content area
    tab1, tab2 = st.tabs(["💬 Chat Assistant", "📊 Analytics Dashboard"])
    
    with tab1:
        display_chat_interface(parser_type)
    
    with tab2:
        display_analytics_dashboard()


if __name__ == "__main__":
    main()
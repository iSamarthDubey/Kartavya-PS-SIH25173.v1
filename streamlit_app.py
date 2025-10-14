"""
Kartavya SIEM - Streamlit Web Application
A beautiful, interactive web interface for the Kartavya SIEM NLP Assistant
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import time

# Page configuration
st.set_page_config(
    page_title="Kartavya SIEM",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        color: #155724;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'backend_url' not in st.session_state:
    st.session_state.backend_url = "http://localhost:8000"
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

def make_api_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Make API request to backend"""
    try:
        url = f"{st.session_state.backend_url}/{endpoint.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state.api_key}" if st.session_state.api_key else ""
        }
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            response = requests.request(method, url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection Error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}"}

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ Kartavya SIEM</h1>
        <p>AI-Powered Security Information & Event Management</p>
        <p>Natural Language Processing • Threat Hunting • Real-time Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Backend URL
        backend_url = st.text_input(
            "Backend URL", 
            value=st.session_state.backend_url,
            help="URL of your Kartavya backend API"
        )
        if backend_url != st.session_state.backend_url:
            st.session_state.backend_url = backend_url
        
        # API Key
        api_key = st.text_input(
            "API Key", 
            value=st.session_state.api_key,
            type="password",
            help="Your API key for authentication"
        )
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
        
        # Test Connection
        if st.button("🔌 Test Connection"):
            with st.spinner("Testing connection..."):
                result = make_api_request("health")
                if result["success"]:
                    st.success("✅ Connection successful!")
                else:
                    st.error(f"❌ Connection failed: {result['error']}")
        
        st.divider()
        
        # Navigation
        st.header("📋 Navigation")
        page = st.selectbox(
            "Select Page",
            [
                "🏠 Dashboard",
                "💬 AI Assistant",
                "🔍 Event Analysis", 
                "📊 Reports",
                "🔧 Query Builder",
                "👥 Admin Panel"
            ]
        )
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "💬 AI Assistant":
        show_ai_assistant()
    elif page == "🔍 Event Analysis":
        show_event_analysis()
    elif page == "📊 Reports":
        show_reports()
    elif page == "🔧 Query Builder":
        show_query_builder()
    elif page == "👥 Admin Panel":
        show_admin_panel()

def show_dashboard():
    """Dashboard page with metrics and overview"""
    st.header("📊 Security Dashboard")
    
    # Fetch dashboard data
    with st.spinner("Loading dashboard data..."):
        result = make_api_request("dashboard/metrics")
    
    if result["success"]:
        data = result["data"]
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🚨 Active Alerts", 
                data.get("active_alerts", 0),
                delta=data.get("alert_delta", 0)
            )
        
        with col2:
            st.metric(
                "📈 Events Today", 
                data.get("events_today", 0),
                delta=data.get("events_delta", 0)
            )
        
        with col3:
            st.metric(
                "🔐 Failed Logins", 
                data.get("failed_logins", 0),
                delta=data.get("login_delta", 0)
            )
        
        with col4:
            st.metric(
                "⚡ System Health", 
                f"{data.get('system_health', 95)}%",
                delta=f"{data.get('health_delta', 2)}%"
            )
        
        st.divider()
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 Threat Level Distribution")
            if "threat_levels" in data:
                fig = px.pie(
                    values=list(data["threat_levels"].values()),
                    names=list(data["threat_levels"].keys()),
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No threat data available")
        
        with col2:
            st.subheader("📊 Events Timeline")
            if "timeline_data" in data:
                df = pd.DataFrame(data["timeline_data"])
                fig = px.line(df, x="time", y="count", title="Events Over Time")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No timeline data available")
        
        # Recent Alerts
        st.subheader("🚨 Recent Alerts")
        alerts_result = make_api_request("dashboard/alerts?limit=10")
        
        if alerts_result["success"] and alerts_result["data"]:
            alerts_df = pd.DataFrame(alerts_result["data"])
            st.dataframe(alerts_df, use_container_width=True)
        else:
            st.info("No recent alerts")
    
    else:
        st.error(f"Failed to load dashboard: {result['error']}")
        
        # Show mock data for demo
        st.warning("Showing demo data:")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🚨 Active Alerts", 12, delta=3)
        with col2:
            st.metric("📈 Events Today", 1547, delta=234)
        with col3:
            st.metric("🔐 Failed Logins", 45, delta=-12)
        with col4:
            st.metric("⚡ System Health", "98%", delta="2%")

def show_ai_assistant():
    """AI Assistant chat interface"""
    st.header("🤖 AI Security Assistant")
    st.write("Ask questions about security events, threats, or get recommendations!")
    
    # Chat interface
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_message = st.text_input(
                "Ask me anything about security...",
                placeholder="e.g., Show me failed login attempts from the last hour",
                label_visibility="collapsed"
            )
        
        with col2:
            submitted = st.form_submit_button("Send 🚀")
    
    if submitted and user_message:
        # Add user message to chat
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get AI response
        with st.spinner("🤔 AI is thinking..."):
            result = make_api_request("assistant/chat", "POST", {
                "message": user_message,
                "conversation_id": "streamlit_session"
            })
        
        if result["success"]:
            ai_response = result["data"].get("response", "I'm sorry, I couldn't process that request.")
        else:
            ai_response = f"Error: {result['error']}. But I can still help with general security questions!"
        
        # Add AI response to chat
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": ai_response
        })
        
        # Refresh to show new messages
        st.rerun()
    
    # Quick action buttons
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Show Recent Events"):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "Show me recent security events"
            })
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "Here are the recent security events from your SIEM system..."
            })
            st.rerun()
    
    with col2:
        if st.button("⚠️ Check Threats"):
            st.session_state.chat_history.append({
                "role": "user", 
                "content": "Are there any active threats?"
            })
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "I'm analyzing your current threat landscape..."
            })
            st.rerun()
    
    with col3:
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

def show_event_analysis():
    """Event analysis page"""
    st.header("🔍 Security Event Analysis")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        event_type = st.selectbox(
            "Event Type",
            ["All", "Authentication", "Network", "System", "Security"]
        )
    
    with col2:
        time_range = st.selectbox(
            "Time Range", 
            ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
        )
    
    with col3:
        limit = st.number_input("Max Results", min_value=10, max_value=1000, value=100)
    
    # Fetch events
    if st.button("🔍 Analyze Events"):
        with st.spinner("Fetching and analyzing events..."):
            # Convert filters to API parameters
            event_type_param = None if event_type == "All" else event_type.lower()
            
            result = make_api_request("platform_events", "GET")
            
            if result["success"]:
                events_data = result["data"]
                
                if events_data:
                    df = pd.DataFrame(events_data)
                    
                    # Display summary
                    st.success(f"✅ Found {len(df)} events")
                    
                    # Event distribution chart
                    if 'event_type' in df.columns:
                        fig = px.histogram(df, x='event_type', title="Event Type Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Events table
                    st.subheader("📋 Event Details")
                    st.dataframe(df, use_container_width=True)
                    
                    # Download option
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime='text/csv'
                    )
                else:
                    st.info("No events found for the selected criteria")
            else:
                st.error(f"Failed to fetch events: {result['error']}")
                
                # Show mock data for demo
                st.warning("Showing demo data:")
                mock_data = pd.DataFrame({
                    'timestamp': [datetime.now() - timedelta(minutes=x*10) for x in range(10)],
                    'event_type': ['authentication', 'network', 'system'] * 3 + ['authentication'],
                    'severity': ['high', 'medium', 'low'] * 3 + ['critical'],
                    'source': ['192.168.1.100', '10.0.0.1', 'server01'] * 3 + ['192.168.1.100'],
                    'description': ['Failed login attempt'] * 10
                })
                st.dataframe(mock_data, use_container_width=True)

def show_reports():
    """Reports page"""
    st.header("📊 Security Reports")
    
    # Report generation
    st.subheader("📝 Generate New Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["Security Summary", "Compliance Report", "Threat Analysis", "User Activity", "Network Traffic"]
        )
        
        date_range = st.date_input(
            "Date Range",
            value=[datetime.now().date() - timedelta(days=7), datetime.now().date()],
            format="YYYY-MM-DD"
        )
    
    with col2:
        report_format = st.selectbox("Format", ["PDF", "CSV", "JSON", "HTML"])
        
        email = st.text_input("Email (optional)", placeholder="user@company.com")
    
    if st.button("🔄 Generate Report"):
        with st.spinner("Generating report..."):
            report_data = {
                "report_type": report_type.lower().replace(" ", "_"),
                "start_date": str(date_range[0]) if len(date_range) > 0 else None,
                "end_date": str(date_range[1]) if len(date_range) > 1 else None,
                "format": report_format.lower(),
                "email": email if email else None
            }
            
            result = make_api_request("reports/generate", "POST", report_data)
            
            if result["success"]:
                st.success("✅ Report generated successfully!")
                report_id = result["data"].get("report_id", "demo_report_123")
                st.info(f"Report ID: {report_id}")
                
                if result["data"].get("download_url"):
                    st.markdown(f"[📥 Download Report]({result['data']['download_url']})")
            else:
                st.error(f"Failed to generate report: {result['error']}")
    
    st.divider()
    
    # Recent reports
    st.subheader("📋 Recent Reports")
    
    reports_result = make_api_request("reports")
    
    if reports_result["success"] and reports_result["data"]:
        reports_df = pd.DataFrame(reports_result["data"])
        st.dataframe(reports_df, use_container_width=True)
    else:
        st.info("No reports found")
        
        # Mock data for demo
        mock_reports = pd.DataFrame({
            'report_id': ['RPT001', 'RPT002', 'RPT003'],
            'type': ['Security Summary', 'Compliance Report', 'Threat Analysis'],
            'created_at': ['2024-01-10', '2024-01-09', '2024-01-08'],
            'status': ['Completed', 'Completed', 'Processing'],
            'format': ['PDF', 'CSV', 'HTML']
        })
        st.dataframe(mock_reports, use_container_width=True)

def show_query_builder():
    """Query builder page"""
    st.header("🔧 Natural Language Query Builder")
    
    st.write("Transform natural language questions into structured queries!")
    
    # Query input
    natural_query = st.text_area(
        "Natural Language Query",
        placeholder="e.g., Show me all failed login attempts from IP addresses starting with 192.168 in the last 24 hours",
        height=100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Translate to SQL"):
            if natural_query:
                with st.spinner("Translating query..."):
                    result = make_api_request("query/translate", "POST", {
                        "query": natural_query
                    })
                    
                    if result["success"]:
                        translated = result["data"].get("translated_query", "")
                        confidence = result["data"].get("confidence", 0)
                        
                        st.subheader("📝 Translated SQL")
                        st.code(translated, language="sql")
                        st.info(f"Confidence: {confidence:.1%}")
                    else:
                        st.error(f"Translation failed: {result['error']}")
            else:
                st.warning("Please enter a natural language query first!")
    
    with col2:
        if st.button("▶️ Execute Query"):
            if natural_query:
                with st.spinner("Executing query..."):
                    result = make_api_request("query/execute", "POST", {
                        "query": natural_query,
                        "limit": 100
                    })
                    
                    if result["success"]:
                        query_results = result["data"].get("results", [])
                        
                        if query_results:
                            st.subheader("📊 Query Results")
                            df = pd.DataFrame(query_results)
                            st.dataframe(df, use_container_width=True)
                            
                            # Download option
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results",
                                data=csv,
                                file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime='text/csv'
                            )
                        else:
                            st.info("Query executed but returned no results")
                    else:
                        st.error(f"Query execution failed: {result['error']}")
            else:
                st.warning("Please enter a query first!")
    
    # Query examples
    st.divider()
    st.subheader("💡 Example Queries")
    
    examples = [
        "Show me all failed login attempts from the last hour",
        "Find network connections to external IP addresses on port 443",
        "List all admin users who logged in today",
        "Show suspicious file executions with high risk score",
        "Find all events from IP address 192.168.1.100"
    ]
    
    for example in examples:
        if st.button(f"💭 {example}", key=f"example_{hash(example)}"):
            st.session_state.example_query = example
            st.rerun()
    
    if hasattr(st.session_state, 'example_query'):
        st.text_area(
            "Selected Example",
            value=st.session_state.example_query,
            key="example_display",
            height=50
        )

def show_admin_panel():
    """Admin panel page"""
    st.header("👥 Administration Panel")
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["👤 Users", "📋 Audit Logs", "⚙️ System"])
    
    with tab1:
        st.subheader("User Management")
        
        # Add new user
        with st.expander("➕ Add New User"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                new_role = st.selectbox("Role", ["viewer", "analyst", "admin"])
            
            with col2:
                new_fullname = st.text_input("Full Name")
                new_department = st.text_input("Department")
                new_active = st.checkbox("Active", value=True)
            
            if st.button("Create User"):
                user_data = {
                    "username": new_username,
                    "email": new_email,
                    "role": new_role,
                    "full_name": new_fullname,
                    "department": new_department,
                    "active": new_active
                }
                
                result = make_api_request("admin/users", "POST", user_data)
                
                if result["success"]:
                    st.success(f"✅ User '{new_username}' created successfully!")
                else:
                    st.error(f"Failed to create user: {result['error']}")
        
        # List existing users
        st.subheader("Existing Users")
        users_result = make_api_request("admin/users")
        
        if users_result["success"] and users_result["data"]:
            users_df = pd.DataFrame(users_result["data"])
            st.dataframe(users_df, use_container_width=True)
        else:
            st.info("No users found or unable to fetch user data")
    
    with tab2:
        st.subheader("Audit Logs")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            audit_user = st.text_input("Filter by User")
        
        with col2:
            audit_action = st.text_input("Filter by Action")
        
        with col3:
            audit_limit = st.number_input("Max Records", min_value=10, max_value=500, value=50)
        
        if st.button("🔍 Fetch Audit Logs"):
            params = {
                "limit": audit_limit,
                "user": audit_user if audit_user else None,
                "action": audit_action if audit_action else None
            }
            
            result = make_api_request("admin/audit-logs", "GET")
            
            if result["success"] and result["data"]:
                audit_df = pd.DataFrame(result["data"])
                st.dataframe(audit_df, use_container_width=True)
            else:
                st.info("No audit logs found")
    
    with tab3:
        st.subheader("System Information")
        
        if st.button("🔍 Get System Info"):
            result = make_api_request("admin/system-info")
            
            if result["success"]:
                info = result["data"]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("System Status", info.get("status", "Unknown"))
                    st.metric("API Version", info.get("version", "1.0.0"))
                    st.metric("Database", info.get("database", "Connected"))
                
                with col2:
                    st.metric("Uptime", info.get("uptime", "Unknown"))
                    st.metric("Total Users", info.get("total_users", 0))
                    st.metric("Active Sessions", info.get("active_sessions", 0))
            else:
                st.error(f"Failed to get system info: {result['error']}")

if __name__ == "__main__":
    main()

"""
🚀 SIEM NLP Assistant - Streamlit Frontend
Modern web interface for natural language SIEM queries.
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import base64
from io import BytesIO

# Configure page
st.set_page_config(
    page_title="SIEM NLP Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
BACKEND_URL = "http://localhost:8000"
API_TIMEOUT = 10

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
    .query-box {
        background: #f1f3f4;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_backend_health():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def query_backend(query, max_results=50):
    """Send query to backend API."""
    try:
        payload = {
            "query": query,
            "parser_type": "enhanced",
            "max_results": max_results
        }
        
        with st.spinner("🔍 Processing your query..."):
            response = requests.post(
                f"{BACKEND_URL}/query", 
                json=payload, 
                timeout=API_TIMEOUT
            )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API Error: {response.status_code} - {response.text}"
    
    except requests.exceptions.Timeout:
        return False, "Request timeout - backend may be slow"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to backend - is it running?"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def display_header():
    """Display the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ SIEM NLP Assistant</h1>
        <p>Transform natural language into powerful security insights</p>
        <small>SIH 2025 - Team Kartavya</small>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display the sidebar with system info and examples."""
    with st.sidebar:
        st.header("🚀 System Status")
        
        # Check backend health
        is_healthy, health_data = check_backend_health()
        
        if is_healthy:
            st.success("✅ Backend API: Online")
            if health_data:
                st.json(health_data.get('components', {}))
        else:
            st.error("❌ Backend API: Offline")
            st.info("💡 Start backend with: `cd backend && python test_and_run.py`")
        
        st.divider()
        
        # Query examples
        st.header("💡 Example Queries")
        
        examples = [
            "Show failed login attempts from last hour",
            "Find security alerts with high severity",
            "Get network traffic on port 443",
            "Show malware detections from yesterday", 
            "List successful logins for admin users",
            "Find system errors from specific server",
            "Display user activity for suspicious accounts",
            "Show firewall blocked connections"
        ]
        
        for example in examples:
            if st.button(f"💬 {example}", key=f"example_{hash(example)}", use_container_width=True):
                st.session_state.query_input = example
                st.rerun()
        
        st.divider()
        
        # Advanced options
        st.header("⚙️ Settings")
        max_results = st.slider("Max Results", 10, 200, 50)
        st.session_state.max_results = max_results
        
        # API Info
        with st.expander("🔧 API Information"):
            st.code(f"Backend URL: {BACKEND_URL}")
            st.code("Health: /health")
            st.code("Query: /query")
            st.code("Docs: /docs")

def display_query_interface():
    """Display the main query interface."""
    st.header("🔍 Natural Language Query")
    
    # Initialize session state
    if 'query_input' not in st.session_state:
        st.session_state.query_input = ""
    if 'max_results' not in st.session_state:
        st.session_state.max_results = 50
    
    # Query input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        query = st.text_input(
            "Enter your security question:",
            value=st.session_state.query_input,
            placeholder="e.g., Show failed login attempts from last hour",
            help="Ask questions in plain English about your security logs"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # Process query
    if search_clicked and query:
        success, result = query_backend(query, st.session_state.max_results)
        
        if success:
            display_results(query, result)
        else:
            st.error(f"❌ Query failed: {result}")
    
    elif search_clicked and not query:
        st.warning("⚠️ Please enter a query first!")

def display_results(query, result):
    """Display query results."""
    st.header("📊 Query Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Intent", result.get('intent', 'Unknown'))
    
    with col2:
        confidence = result.get('confidence', 0)
        st.metric("Confidence", f"{confidence:.1%}")
    
    with col3:
        result_count = len(result.get('results', []))
        st.metric("Results Found", result_count)
    
    with col4:
        exec_time = result.get('execution_time', 0)
        st.metric("Execution Time", f"{exec_time:.2f}s")
    
    # Query summary
    if result.get('formatted_response'):
        st.markdown(f"""
        <div class="success-box">
            <h4>📝 Summary</h4>
            <p>{result['formatted_response']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Extracted entities
    if result.get('entities'):
        st.subheader("🏷️ Extracted Entities")
        entities_df = []
        for entity_type, values in result['entities'].items():
            for value in values:
                entities_df.append({'Type': entity_type.replace('_', ' ').title(), 'Value': value})
        
        if entities_df:
            df = pd.DataFrame(entities_df)
            st.dataframe(df, use_container_width=True)
    
    # Results table
    if result.get('results'):
        st.subheader("📋 Detailed Results")
        
        # Convert results to DataFrame
        try:
            df = pd.DataFrame(result['results'])
            
            # Format timestamp columns
            for col in df.columns:
                if 'timestamp' in col.lower() or col == '@timestamp':
                    try:
                        df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
            
            # Display table
            st.dataframe(df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"siem_query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Simple visualization
            if len(df) > 1:
                st.subheader("📈 Visualization")
                
                # Time-based chart if timestamp exists
                timestamp_cols = [col for col in df.columns if 'timestamp' in col.lower() or col == '@timestamp']
                if timestamp_cols:
                    try:
                        ts_col = timestamp_cols[0]
                        chart_df = df.copy()
                        chart_df[ts_col] = pd.to_datetime(chart_df[ts_col])
                        chart_df['count'] = 1
                        
                        # Group by hour
                        hourly = chart_df.set_index(ts_col).resample('H')['count'].sum().reset_index()
                        
                        fig = px.line(hourly, x=ts_col, y='count', 
                                    title="Events Over Time",
                                    labels={ts_col: "Time", 'count': "Event Count"})
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.info(f"Could not generate time chart: {e}")
                
                # Top values charts for categorical columns
                categorical_cols = []
                for col in df.columns:
                    if df[col].dtype == 'object' and len(df[col].unique()) <= 20:
                        categorical_cols.append(col)
                
                if categorical_cols:
                    chart_col = st.selectbox("Select field to visualize:", categorical_cols)
                    if chart_col:
                        value_counts = df[chart_col].value_counts().head(10)
                        
                        fig = px.bar(x=value_counts.values, y=value_counts.index,
                                   orientation='h',
                                   title=f"Top {chart_col} Values",
                                   labels={'x': 'Count', 'y': chart_col})
                        st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error displaying results: {e}")
            st.json(result['results'])
    
    # Generated query (for technical users)
    with st.expander("🔧 Technical Details"):
        st.subheader("Generated Elasticsearch Query")
        try:
            # Try to parse and pretty-print the SIEM query
            if result.get('siem_query'):
                if result['siem_query'].startswith('{'):
                    parsed_query = json.loads(result['siem_query'])
                    st.json(parsed_query)
                else:
                    st.code(result['siem_query'], language='json')
        except:
            st.code(result.get('siem_query', 'No query generated'), language='text')
        
        st.subheader("Full API Response")
        st.json(result)

def display_footer():
    """Display footer information."""
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🛡️ SIEM NLP Assistant**")
        st.markdown("Powered by advanced NLP")
    
    with col2:
        st.markdown("**🏆 SIH 2025**")
        st.markdown("Team Kartavya")
    
    with col3:
        st.markdown("**🔗 Links**")
        st.markdown(f"[API Docs]({BACKEND_URL}/docs)")
        st.markdown(f"[Health Check]({BACKEND_URL}/health)")

def main():
    """Main application function."""
    display_header()
    display_sidebar()
    display_query_interface()
    display_footer()

if __name__ == "__main__":
    main()
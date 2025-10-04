"""Script to create new professional UI"""

ui_code = '''"""
🚀 SIEM NLP Assistant - Professional Modern UI
Enterprise-grade security intelligence interface with stunning visuals.
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from collections import Counter
import re

# Configure page with professional settings
st.set_page_config(
    page_title="🛡️ SIEM Intelligence Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
BACKEND_URL = "http://localhost:8001"
API_TIMEOUT = 30

# PROFESSIONAL MODERN CSS - Dark theme with vibrant accents
st.markdown("""
<style>
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Professional header with glassmorphism effect */
    .main-header {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        animation: slideDown 0.6s ease;
    }
    
    .main-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.85);
        font-size: 1.1rem;
        margin: 0.5rem 0;
    }
    
    .main-header small {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.95rem;
    }
    
    /* Chat messages with modern design */
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        animation: fadeInUp 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .chat-message::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    }
    
    .user-message {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
        margin-left: 3rem;
    }
    
    .assistant-message {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-right: 3rem;
    }
    
    /* Professional metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Beautiful badges */
    .info-badge {
        display: inline-block;
        padding: 0.5rem 1.2rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.3rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .info-badge:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .intent-badge {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.3) 0%, rgba(33, 150, 243, 0.1) 100%);
        color: #64b5f6;
        border-color: rgba(33, 150, 243, 0.4);
    }
    
    .confidence-badge {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.3) 0%, rgba(76, 175, 80, 0.1) 100%);
        color: #81c784;
        border-color: rgba(76, 175, 80, 0.4);
    }
    
    .time-badge {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.3) 0%, rgba(255, 152, 0, 0.1) 100%);
        color: #ffb74d;
        border-color: rgba(255, 152, 0, 0.4);
    }
    
    .count-badge {
        background: linear-gradient(135deg, rgba(156, 39, 176, 0.3) 0%, rgba(156, 39, 176, 0.1) 100%);
        color: #ba68c8;
        border-color: rgba(156, 39, 176, 0.4);
    }
    
    /* Status indicators with pulse animation */
    .status-online {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #4caf50;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(76, 175, 80, 1);
        animation: pulse 2s infinite;
    }
    
    .status-offline {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #f44336;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(244, 67, 54, 1);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
        100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhance Streamlit components */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: white;
        padding: 0.75rem 1rem;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
    }
    
    /* Professional table styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Results section */
    .results-container {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 12, 41, 0.95) 0%, rgba(48, 43, 99, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Text colors */
    .stMarkdown, p, span, div {
        color: rgba(255, 255, 255, 0.9);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: rgba(255, 255, 255, 0.95);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: rgba(76, 175, 80, 0.15);
        border-left: 4px solid #4caf50;
    }
    
    .stError {
        background: rgba(244, 67, 54, 0.15);
        border-left: 4px solid #f44336;
    }
    
    .stWarning {
        background: rgba(255, 152, 0, 0.15);
        border-left: 4px solid #ff9800;
    }
    
    .stInfo {
        background: rgba(33, 150, 243, 0.15);
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = f"conv_{int(time.time())}"
if "backend_healthy" not in st.session_state:
    st.session_state.backend_healthy = False
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "stats" not in st.session_state:
    st.session_state.stats = {
        "total_queries": 0,
        "successful_queries": 0,
        "total_results": 0
    }

def check_backend_health():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            st.session_state.backend_healthy = True
            return True, response.json()
        return False, None
    except:
        st.session_state.backend_healthy = False
        return False, None

def query_assistant(user_query):
    try:
        payload = {
            "query": user_query,
            "conversation_id": st.session_state.conversation_id
        }
        
        response = requests.post(
            f"{BACKEND_URL}/assistant/ask",
            json=payload,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            st.session_state.stats["successful_queries"] += 1
            return True, response.json()
        else:
            return False, f"API Error: {response.status_code}"
    
    except requests.exceptions.Timeout:
        return False, "⏱️ Request timeout"
    except requests.exceptions.ConnectionError:
        return False, f"🔌 Cannot connect to backend"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def display_header():
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ SIEM Intelligence Assistant</h1>
        <p>🔍 Conversational Security Intelligence & Threat Investigation</p>
        <p>Ask questions in natural language • Real-time threat analysis • Multi-SIEM integration</p>
        <small>Powered by Advanced NLP | Elasticsearch | Machine Learning</small>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    with st.sidebar:
        st.markdown("### 🎛️ Control Center")
        
        st.markdown("#### 🔌 Backend Status")
        healthy, health_data = check_backend_health()
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if healthy:
                st.markdown('<div class="status-online"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-offline"></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{'✅ Online' if healthy else '❌ Offline'}**")
        
        if healthy and health_data:
            with st.expander("📊 Health Details"):
                st.json(health_data)
        
        st.divider()
        
        st.markdown("#### 📈 Session Statistics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Queries</div>
                <div class="metric-value">{st.session_state.stats['total_queries']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            success_rate = (st.session_state.stats['successful_queries'] / max(st.session_state.stats['total_queries'], 1)) * 100
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Success</div>
                <div class="metric-value">{success_rate:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Results</div>
            <div class="metric-value">{st.session_state.stats['total_results']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("#### 💬 Conversation")
        st.caption(f"ID: {st.session_state.conversation_id[:16]}...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Chat", use_container_width=True):
                st.session_state.conversation_id = f"conv_{int(time.time())}"
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        st.divider()
        
        st.markdown("#### 💡 Quick Queries")
        
        examples = [
            ("🔐", "Show failed login attempts"),
            ("⚠️", "Find high severity alerts"),
            ("🦠", "Show malware detections"),
            ("🌐", "Show network connections"),
            ("👤", "List top 10 users"),
            ("🔍", "Find suspicious activity"),
            ("📊", "Show authentication failures"),
            ("⚡", "What processes ran today?")
        ]
        
        for icon, example in examples:
            if st.button(f"{icon} {example}", key=f"ex_{example}", use_container_width=True):
                st.session_state.pending_query = example
                st.rerun()
        
        st.divider()
        
        st.markdown("#### 📜 Recent Queries")
        if st.session_state.query_history:
            recent = list(reversed(st.session_state.query_history[-5:]))
            for i, query in enumerate(recent):
                if st.button(f"↩️ {query[:25]}...", key=f"hist_{i}", use_container_width=True):
                    st.session_state.pending_query = query
                    st.rerun()
        else:
            st.info("No query history yet")

def format_response_data(response_data):
    intent = response_data.get('intent', 'N/A')
    confidence = response_data.get('confidence', 0)
    result_count = response_data.get('result_count', 0)
    query_time = response_data.get('query_time_ms', 0)
    
    st.session_state.stats['total_results'] += result_count
    
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <span class="info-badge intent-badge">🎯 Intent: {intent}</span>
        <span class="info-badge confidence-badge">📊 Confidence: {confidence:.2%}</span>
        <span class="info-badge count-badge">📈 Results: {result_count}</span>
        <span class="info-badge time-badge">⚡ {query_time:.0f}ms</span>
    </div>
    """, unsafe_allow_html=True)
    
    if 'summary' in response_data and response_data['summary']:
        st.markdown(f"""
        <div class="results-container">
            <h4>📋 Summary</h4>
            <p style="font-size: 1.1rem; line-height: 1.6;">{response_data['summary']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    if 'answer' in response_data and response_data['answer']:
        st.markdown(f"""
        <div class="results-container">
            <h4>💡 Analysis</h4>
            <p style="font-size: 1.05rem; line-height: 1.6;">{response_data['answer']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    if 'results' in response_data and response_data['results']:
        results = response_data['results']
        
        st.markdown(f"""
        <div class="results-container">
            <h4>📊 Detailed Results ({len(results)} items)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if results:
            df = pd.DataFrame(results)
            
            if len(df.columns) > 10:
                important_cols = ['timestamp', 'event_type', 'severity', 'user', 'ip_address', 'message']
                display_cols = [col for col in important_cols if col in df.columns]
                if not display_cols:
                    display_cols = list(df.columns[:10])
                df_display = df[display_cols]
            else:
                df_display = df
            
            st.dataframe(
                df_display.head(50),
                use_container_width=True,
                height=400
            )
            
            if result_count > 0:
                st.markdown("#### 📈 Visual Analysis")
                
                try:
                    if 'timestamp' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                        time_counts = df.groupby(df['timestamp'].dt.date).size().reset_index()
                        time_counts.columns = ['date', 'count']
                        
                        fig = px.line(
                            time_counts,
                            x='date',
                            y='count',
                            title='Events Over Time',
                            template='plotly_dark'
                        )
                        fig.update_traces(line_color='#667eea', line_width=3)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    if 'severity' in df.columns:
                        severity_counts = df['severity'].value_counts().reset_index()
                        severity_counts.columns = ['severity', 'count']
                        
                        fig = px.bar(
                            severity_counts,
                            x='severity',
                            y='count',
                            title='Events by Severity',
                            template='plotly_dark',
                            color='severity',
                            color_discrete_map={
                                'critical': '#f44336',
                                'high': '#ff9800',
                                'medium': '#ffeb3b',
                                'low': '#4caf50',
                                'info': '#2196f3'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    if 'user' in df.columns:
                        user_counts = df['user'].value_counts().head(10).reset_index()
                        user_counts.columns = ['user', 'count']
                        
                        fig = px.bar(
                            user_counts,
                            x='count',
                            y='user',
                            orientation='h',
                            title='Top 10 Users by Activity',
                            template='plotly_dark'
                        )
                        fig.update_traces(marker_color='#764ba2')
                        st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.info("📊 Visual analysis not available")
    
    if result_count == 0:
        st.warning("""
        ### 🔍 No Results Found
        
        Your query was understood correctly, but no matching data was found.
        
        **Possible reasons:**
        - Time range might not contain relevant events
        - Data might be in a different index
        - Try broader search terms
        
        **Suggestions:**
        - Try: "Show all recent events"
        - Check data source connection
        - Verify time range settings
        """)

def display_chat_message(message, index):
    role = message['role']
    content = message.get('content', '')
    
    if role == 'user':
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>🧑 You</strong><br>
            <span style="font-size: 1.05rem;">{content}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistant</strong>
        """, unsafe_allow_html=True)
        
        if 'response_data' in message:
            format_response_data(message['response_data'])
        else:
            st.markdown(f'<span style="font-size: 1.05rem;">{content}</span>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def main():
    display_header()
    display_sidebar()
    
    st.markdown("### 💬 Conversation")
    
    for i, message in enumerate(st.session_state.chat_history):
        display_chat_message(message, i)
    
    if "pending_query" in st.session_state:
        user_query = st.session_state.pending_query
        del st.session_state.pending_query
        
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_query,
            "timestamp": datetime.now().isoformat()
        })
        
        st.session_state.stats["total_queries"] += 1
        if user_query not in st.session_state.query_history:
            st.session_state.query_history.append(user_query)
        
        with st.spinner("🔍 Analyzing your query..."):
            success, response = query_assistant(user_query)
        
        if success:
            st.session_state.chat_history.append({
                "role": "assistant",
                "response_data": response,
                "timestamp": datetime.now().isoformat()
            })
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"❌ {response}",
                "timestamp": datetime.now().isoformat()
            })
        
        st.rerun()
    
    st.markdown("---")
    user_input = st.chat_input("💬 Ask anything about your security data...", key="chat_input")
    
    if user_input:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        st.session_state.stats["total_queries"] += 1
        if user_input not in st.session_state.query_history:
            st.session_state.query_history.append(user_input)
        
        with st.spinner("🔍 Analyzing your query..."):
            success, response = query_assistant(user_input)
        
        if success:
            st.session_state.chat_history.append({
                "role": "assistant",
                "response_data": response,
                "timestamp": datetime.now().isoformat()
            })
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"❌ {response}",
                "timestamp": datetime.now().isoformat()
            })
        
        st.rerun()
    
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="results-container" style="text-align: center; padding: 3rem;">
            <h2>👋 Welcome to SIEM Intelligence Assistant!</h2>
            <p style="font-size: 1.2rem; margin: 2rem 0;">
                I'm your AI-powered security analyst assistant. Ask me anything about your security data!
            </p>
            <div style="margin: 2rem 0;">
                <span class="info-badge intent-badge">Natural Language Queries</span>
                <span class="info-badge confidence-badge">Real-time Analysis</span>
                <span class="info-badge count-badge">Multi-SIEM Support</span>
                <span class="info-badge time-badge">Instant Results</span>
            </div>
            <p style="margin-top: 2rem; color: rgba(255, 255, 255, 0.7);">
                💡 Try asking: "Show failed login attempts" or click a quick query from the sidebar!
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
'''

# Write to file
with open('ui_dashboard/streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(ui_code)

print("✅ New professional UI created successfully!")
print("📁 File: ui_dashboard/streamlit_app.py")
print("🎨 Features:")
print("  - Dark gradient background with purple/blue theme")
print("  - Glassmorphism effects")
print("  - Animated badges and cards")
print("  - Professional metric displays")
print("  - Beautiful data visualizations")
print("  - Responsive layout")
print("\n🚀 Ready to reload!")

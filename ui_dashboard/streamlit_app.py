"""
🚀 SIEM NLP Assistant - Enhanced Chat Interface
Modern conversational interface with powerful features.
"""

import streamlit as st
import requests
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import hashlib
from collections import Counter
import re
import io
import zipfile

# Backend configuration
_env_backend_url = os.environ.get("ASSISTANT_BACKEND_URL")
_env_host = os.environ.get("ASSISTANT_HOST", "localhost")
_env_port = os.environ.get("ASSISTANT_PORT") or os.environ.get("ASSISTANT_API_PORT") or "8001"

if _env_backend_url:
    BACKEND_URL = _env_backend_url.rstrip("/")
else:
    BACKEND_URL = f"http://{_env_host}:{_env_port}"

# Configure page
st.set_page_config(
    page_title="Conversational SIEM Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Base URL - specific endpoints will add /assistant/ask
API_TIMEOUT = 30
TOKEN_REFRESH_MARGIN = timedelta(seconds=30)
DEFAULT_DEMO_USERNAME = (
    os.environ.get("ASSISTANT_DEMO_USER")
    or os.environ.get("ASSISTANT_DEMO_USERNAME")
    or "admin"
)
DEFAULT_DEMO_PASSWORD = os.environ.get("ASSISTANT_DEMO_PASSWORD") or "Admin!2025"

# Custom CSS for modern chat interface
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        animation: fadeIn 0.3s;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 2rem;
        text-align: right;
    }
    .assistant-message {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        margin-right: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
    }
    .info-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
    }
    .intent-badge {
        background: #e3f2fd;
        color: #1976d2;
    }
    .confidence-badge {
        background: #e8f5e9;
        color: #388e3c;
    }
    .time-badge {
        background: #fff3e0;
        color: #f57c00;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stChatInput {
        border-radius: 25px;
    }
    .command-palette {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #667eea;
        margin: 1rem 0;
    }
    .keyboard-shortcut {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        background: #f0f0f0;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.85rem;
        margin: 0.2rem;
    }
    .feature-highlight {
        background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Command palette commands
COMMANDS = {
    "/help": "Show help and keyboard shortcuts",
    "/clear": "Clear conversation history",
    "/export": "Export conversation",
    "/stats": "Show session statistics",
    "/critical": "Show critical alerts",
    "/failed": "Show failed logins",
    "/network": "Show network activity",
    "/summary": "Get security summary"
}

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = f"conv_{int(time.time())}"
if "backend_healthy" not in st.session_state:
    st.session_state.backend_healthy = False
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "export_history" not in st.session_state:
    st.session_state.export_history = []
if "filters" not in st.session_state:
    st.session_state.filters = {
        "time_range": "Last 24 hours",
        "severity": "All",
        "data_source": "All"
    }

if "auth_username" not in st.session_state:
    st.session_state.auth_username = DEFAULT_DEMO_USERNAME
if "show_dsl_default" not in st.session_state:
    st.session_state.show_dsl_default = False
if "auth_password" not in st.session_state:
    st.session_state.auth_password = DEFAULT_DEMO_PASSWORD
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "auth_token_expires_at" not in st.session_state:
    st.session_state.auth_token_expires_at = None
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "auth_role" not in st.session_state:
    st.session_state.auth_role = None
if "auth_error" not in st.session_state:
    st.session_state.auth_error = None
if "auth_initialized" not in st.session_state:
    st.session_state.auth_initialized = False

def check_backend_health():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/assistant/ping", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            st.session_state.backend_healthy = True
            return True, health_data
        return False, None
    except:
        st.session_state.backend_healthy = False
        return False, None

# Authentication helpers
def _parse_iso_datetime(value):
    if not value:
        return None
    try:
        if isinstance(value, str) and value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except Exception:
        return None


def reset_auth_state(error_message=None):
    st.session_state.auth_token = None
    st.session_state.auth_token_expires_at = None
    st.session_state.auth_user = None
    st.session_state.auth_role = None
    st.session_state.auth_error = error_message
    st.session_state.auth_initialized = True


def perform_login(username=None, password=None):
    username = username or st.session_state.get("auth_username")
    password = password or st.session_state.get("auth_password")

    if not username or not password:
        reset_auth_state("Username or password missing. Configure credentials in the sidebar.")
        return False, st.session_state.auth_error

    try:
        response = requests.post(
            f"{BACKEND_URL}/assistant/auth/login",
            json={"username": username, "password": password},
            timeout=API_TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state.auth_token = data.get("access_token")
            st.session_state.auth_token_expires_at = data.get("expires_at")
            st.session_state.auth_user = username
            st.session_state.auth_role = data.get("role")
            st.session_state.auth_error = None
            st.session_state.auth_initialized = True
            return True, None

        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        reset_auth_state(f"{response.status_code}: {detail}")
        return False, st.session_state.auth_error

    except Exception as exc:
        reset_auth_state(str(exc))
        return False, str(exc)


def ensure_auth_token(force_refresh=False):
    token = st.session_state.get("auth_token")
    expires_at = st.session_state.get("auth_token_expires_at")

    if not force_refresh and token:
        expiry_dt = _parse_iso_datetime(expires_at)
        if expiry_dt:
            if expiry_dt - TOKEN_REFRESH_MARGIN > datetime.utcnow():
                return token
        else:
            return token

    success, _ = perform_login()
    if success:
        return st.session_state.get("auth_token")
    return None

def _transform_filters_for_api(filters: dict) -> dict:
    """Map UI filters to API-ready filters (time_window_gte, severity, index_class)."""
    if not isinstance(filters, dict):
        return {}
    out = {}
    # Time mapping
    time_preset = filters.get("time_range")
    time_map = {
        "Last 15 minutes": "now-15m",
        "Last hour": "now-1h",
        "Last 6 hours": "now-6h",
        "Last 24 hours": "now-1d",
        "Last 7 days": "now-7d",
        "Last 30 days": "now-30d",
    }
    if time_preset in time_map:
        out["time_window_gte"] = time_map[time_preset]
    # Severity
    sev = filters.get("severity")
    if sev and str(sev).lower() != "all":
        out["severity"] = sev
    # Dataset/index_class (optional)
    dataset = filters.get("dataset") or filters.get("index_class")
    if dataset:
        ds_map = {
            "Windows": "windows",
            "Linux": "linux",
            "Network": "network",
            "Auto": ""
        }
        mapped = ds_map.get(dataset, dataset)
        if mapped:
            out["index_class"] = mapped
    # Pass through any explicit override from Investigate tab
    if filters.get("time_window_gte"):
        out["time_window_gte"] = filters["time_window_gte"]
    return out


def query_assistant(user_query, filters=None, limit=None, offset=None, force_intent=None):
    """Send query to the assistant API with optional filters and pagination."""
    try:
        payload = {
            "query": user_query,
            "conversation_id": st.session_state.conversation_id,
        }

        if filters:
            payload["filters"] = _transform_filters_for_api(filters)
        if limit is not None:
            payload["limit"] = int(limit)
        if offset is not None:
            payload["offset"] = int(offset)
        if force_intent:
            payload["force_intent"] = force_intent

        if user_query not in st.session_state.query_history:
            st.session_state.query_history.append(user_query)

        token = ensure_auth_token()
        if not token:
            error_detail = st.session_state.auth_error or "Authentication required. Update credentials in the sidebar."
            return False, f"🔒 {error_detail}"

        def _post(headers_override):
            return requests.post(
                f"{BACKEND_URL}/assistant/ask",
                json=payload,
                headers=headers_override,
                timeout=API_TIMEOUT,
            )

        headers = {"Authorization": f"Bearer {token}"}
        response = _post(headers)

        if response.status_code == 401:
            refreshed_token = ensure_auth_token(force_refresh=True)
            if not refreshed_token:
                error_detail = st.session_state.auth_error or "Authentication failed. Please verify your credentials."
                return False, f"🔒 {error_detail}"
            headers = {"Authorization": f"Bearer {refreshed_token}"}
            response = _post(headers)

        if response.status_code == 200:
            return True, response.json()

        error_detail = "Unknown error"
        try:
            error_data = response.json()
            error_detail = error_data.get("detail", response.text)
        except Exception:
            error_detail = response.text
        return False, f"API Error: {response.status_code} - {error_detail}"

    except requests.exceptions.Timeout:
        return False, "⏱️ Request timeout - query took too long"
    except requests.exceptions.ConnectionError:
        return False, f"🔌 Cannot connect to backend at {BACKEND_URL}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def export_conversation(format_type="json"):
    """Export conversation history."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type == "json":
        data = json.dumps(st.session_state.chat_history, indent=2)
        filename = f"conversation_{timestamp}.json"
        mime = "application/json"
    elif format_type == "txt":
        lines = []
        for msg in st.session_state.chat_history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            lines.append(f"[{msg.get('timestamp', 'N/A')}] {role}:")
            lines.append(msg['content'])
            lines.append("")
        data = "\n".join(lines)
        filename = f"conversation_{timestamp}.txt"
        mime = "text/plain"
    
    return data, filename, mime

def get_query_insights():
    """Analyze query history and provide insights."""
    if not st.session_state.query_history:
        return None
    
    # Most common words
    all_words = []
    for query in st.session_state.query_history:
        words = re.findall(r'\b\w+\b', query.lower())
        all_words.extend([w for w in words if len(w) > 3])
    
    word_counts = Counter(all_words).most_common(10)
    
    return {
        "total_queries": len(st.session_state.query_history),
        "unique_queries": len(set(st.session_state.query_history)),
        "common_terms": word_counts,
        "avg_query_length": sum(len(q) for q in st.session_state.query_history) / len(st.session_state.query_history)
    }

def display_header():
    """Display the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Conversational SIEM Assistant</h1>
        <p>→ for Investigation and Automated Threat Reporting using NLP</p>
        <p>Ask questions in natural language about your security data</p>
        <small>Powered by advanced NLP and multi-SIEM integration</small>
        <div style="margin-top:8px;font-size:13px;opacity:0.9;">
            <strong>SIH 2025 – ISRO (DoS)</strong> · Team Kartavya · Demo-friendly and auditable
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with advanced settings and features."""
    st.sidebar.title("⚙️ Settings & Features")
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4 = st.sidebar.tabs(["🏠 Main", "🎯 Filters", "📊 Analytics", "⚙️ Advanced"])
    
    with tab1:
        # Backend health check
        st.subheader("🔌 Backend Status")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Check", use_container_width=True):
                healthy, health_data = check_backend_health()
                if healthy:
                    st.success("✅ Healthy")
                    if health_data:
                        st.json(health_data)
                else:
                    st.error("❌ Down")
        
        with col2:
            status = "🟢" if st.session_state.backend_healthy else "🔴"
            st.metric("Status", status)
        
        st.divider()
        
        # Conversation controls
        st.subheader("💬 Conversation")
        st.text(f"ID: {st.session_state.conversation_id[:12]}...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New", use_container_width=True):
                st.session_state.conversation_id = f"conv_{int(time.time())}"
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        st.divider()
        
        # Example queries
        st.subheader("💡 Quick Queries")
        examples = [
            "Show failed login attempts",
            "Find high severity alerts",
            "What processes ran today?",
            "Show network connections",
            "Find suspicious activity",
            "List top 10 users by activity",
            "Show authentication failures",
            "Find malware detections"
        ]
        
        for example in examples[:5]:  # Show first 5
            if st.button(f"📝 {example}", key=f"ex_{example}", use_container_width=True):
                st.session_state.pending_query = example
                st.rerun()
        
        with st.expander("More Examples"):
            for example in examples[5:]:
                if st.button(f"📝 {example}", key=f"ex_{example}", use_container_width=True):
                    st.session_state.pending_query = example
                    st.rerun()
    
    with tab2:
        # Advanced filters
        st.subheader("🎯 Query Filters")
        
        st.session_state.filters["time_range"] = st.selectbox(
            "⏰ Time Range",
            ["Last 15 minutes", "Last hour", "Last 6 hours", "Last 24 hours", "Last 7 days", "Last 30 days", "Custom"],
            index=3
        )
        
        st.session_state.filters["severity"] = st.selectbox(
            "⚠️ Severity Level",
            ["All", "Critical", "High", "Medium", "Low", "Info"]
        )
        
        st.session_state.filters["data_source"] = st.selectbox(
            "🔌 Data Source",
            ["All", "Elasticsearch", "Wazuh", "Splunk", "QRadar"]
        )
        # Optional dataset type to improve field selection
        st.session_state.filters["dataset"] = st.selectbox(
            "🧬 Dataset",
            ["Auto", "Windows", "Linux", "Network"],
            index=0
        )
        
        st.session_state.filters["limit"] = st.slider(
            "📊 Max Results",
            min_value=10,
            max_value=1000,
            value=100,
            step=10
        )
        st.session_state.filters["offset"] = st.number_input(
            "↔️ Offset (pagination)", min_value=0, step=50, value=int(st.session_state.filters.get("offset", 0))
        )
        
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.session_state.filters = {
                "time_range": "Last 24 hours",
                "severity": "All",
                "data_source": "All"
            }
            st.rerun()
    
    with tab3:
        # Analytics & Insights
        st.subheader("📊 Session Analytics")
        
        # Basic stats
        st.metric("💬 Total Messages", len(st.session_state.chat_history))
        st.metric("❓ Queries Sent", len([m for m in st.session_state.chat_history if m['role'] == 'user']))
        st.metric("💾 Favorites", len(st.session_state.favorites))
        
        # Query insights
        insights = get_query_insights()
        if insights:
            st.divider()
            st.metric("🔢 Total Queries", insights['total_queries'])
            st.metric("✨ Unique Queries", insights['unique_queries'])
            st.metric("📏 Avg Query Length", f"{insights['avg_query_length']:.0f} chars")
            
            if insights['common_terms']:
                st.subheader("🔥 Top Query Terms")
                for term, count in insights['common_terms'][:5]:
                    st.text(f"{term}: {count}x")
        
        # Export options
        st.divider()
        st.subheader("📥 Export Data")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 JSON", use_container_width=True):
                data, filename, mime = export_conversation("json")
                st.download_button(
                    label="⬇️ Download",
                    data=data,
                    file_name=filename,
                    mime=mime,
                    use_container_width=True
                )
        
        with col2:
            if st.button("📝 TXT", use_container_width=True):
                data, filename, mime = export_conversation("txt")
                st.download_button(
                    label="⬇️ Download",
                    data=data,
                    file_name=filename,
                    mime=mime,
                    use_container_width=True
                )
    
    with tab4:
        st.subheader("🔒 Authentication")

        st.text_input("Username", key="auth_username")
        st.text_input("Password", type="password", key="auth_password")

        if st.session_state.auth_token:
            user_display = st.session_state.auth_user or st.session_state.auth_username
            st.success(f"Authenticated as {user_display}")
            if st.session_state.auth_role:
                st.caption(f"Role: {st.session_state.auth_role}")
            if st.session_state.auth_token_expires_at:
                st.caption(f"Token expires at {st.session_state.auth_token_expires_at}")
        else:
            st.warning("Not authenticated. Queries require a valid token.")
            if st.session_state.auth_initialized and st.session_state.auth_error:
                st.error(st.session_state.auth_error)

        auth_col1, auth_col2 = st.columns(2)
        with auth_col1:
            if st.button("🔐 Login / Refresh Token", use_container_width=True):
                success, message = perform_login()
                if success:
                    st.success("Authenticated successfully!")
                else:
                    st.error(f"Login failed: {message}")

        with auth_col2:
            if st.button("🚪 Logout", use_container_width=True):
                reset_auth_state()
                st.success("Logged out. Token cleared.")

        st.divider()

        # Advanced settings
        st.subheader("⚙️ Advanced Settings")

        # NLP enrichment status
        spacy_enabled = str(os.environ.get("ASSISTANT_USE_SPACY", "")).lower() in ("1", "true", "yes")
        if spacy_enabled:
            st.success("spaCy enrichment: ENABLED")
        else:
            st.info("spaCy enrichment: disabled (optional)")
        
        st.session_state.auto_refresh = st.checkbox(
            "🔄 Auto-refresh results",
            value=st.session_state.auto_refresh
        )
        
        if st.session_state.auto_refresh:
            refresh_interval = st.slider(
                "Refresh interval (seconds)",
                min_value=5,
                max_value=60,
                value=30,
                step=5
            )
        
        st.session_state.dark_mode = st.checkbox(
            "🌙 Dark mode",
            value=st.session_state.dark_mode
        )
        
        show_metadata = st.checkbox("📊 Show detailed metadata", value=True)
        show_raw_json = st.checkbox("🔍 Show raw JSON responses", value=False)
        st.session_state.show_dsl_default = st.checkbox("🧩 Always show generated DSL by default", value=st.session_state.show_dsl_default)
        enable_notifications = st.checkbox("🔔 Enable notifications", value=True)
        
        st.divider()
        
        # Query history
        st.subheader("📜 Query History")
        if st.session_state.query_history:
            for i, query in enumerate(reversed(st.session_state.query_history[-10:])):
                if st.button(f"↩️ {query[:30]}...", key=f"hist_{i}", use_container_width=True):
                    st.session_state.pending_query = query
                    st.rerun()
        else:
            st.info("No query history yet")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.query_history = []
            st.rerun()

def _build_export_pack(message: dict) -> bytes:
    """Build an in-memory ZIP export pack for the given assistant message."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        # Summary
        summary_txt = message.get('summary', '') or message.get('content', '')
        zf.writestr('summary.txt', summary_txt)
        # Results
        results = message.get('results', [])
        try:
            zf.writestr('results.json', json.dumps(results, indent=2, default=str))
        except Exception:
            zf.writestr('results.json', '[]')
        # DSL
        siem_query = message.get('siem_query', {})
        try:
            zf.writestr('siem_query.json', json.dumps(siem_query, indent=2, default=str))
        except Exception:
            zf.writestr('siem_query.json', '{}')
        # Entities
        entities = message.get('entities', {})
        try:
            zf.writestr('entities.json', json.dumps(entities, indent=2, default=str))
        except Exception:
            zf.writestr('entities.json', '{}')
        # Metadata
        meta = message.get('metadata', {})
        try:
            zf.writestr('metadata.json', json.dumps(meta, indent=2, default=str))
        except Exception:
            zf.writestr('metadata.json', '{}')
    buf.seek(0)
    return buf.getvalue()


def display_chat_message(message, index):
    """Display a single chat message with enhanced features."""
    role = message['role']
    content = message['content']
    
    if role == 'user':
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>🧑 You:</strong><br>{content}
            </div>
            """, unsafe_allow_html=True)
        with col2:
            # Add to favorites
            if st.button("⭐", key=f"fav_user_{index}"):
                if content not in st.session_state.favorites:
                    st.session_state.favorites.append(content)
                    st.success("Added to favorites!")
    else:
        # Assistant message
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistant:</strong><br>
        """, unsafe_allow_html=True)
        
        # Display summary/answer
        if 'summary' in message:
            st.markdown(f"**{message['summary']}**")
        elif 'answer' in message:
            st.markdown(message['answer'])
        else:
            st.markdown(content)
        
        # Display metadata badges
        if 'metadata' in message:
            metadata = message['metadata']
            cols = st.columns(4)
            
            with cols[0]:
                if 'intent' in metadata:
                    st.markdown(f'<span class="info-badge intent-badge">Intent: {metadata["intent"]}</span>', unsafe_allow_html=True)
            
            with cols[1]:
                if 'confidence_score' in metadata:
                    confidence = metadata['confidence_score']
                    st.markdown(f'<span class="info-badge confidence-badge">Confidence: {confidence:.0%}</span>', unsafe_allow_html=True)
            
            with cols[2]:
                if 'results_count' in metadata:
                    st.markdown(f'<span class="info-badge">Results: {metadata["results_count"]}</span>', unsafe_allow_html=True)
            
            with cols[3]:
                if 'processing_time_seconds' in metadata:
                    st.markdown(f'<span class="info-badge time-badge">Time: {metadata["processing_time_seconds"]:.2f}s</span>', unsafe_allow_html=True)
        
        # Clarification suggestions
        if message.get('metadata', {}).get('needs_clarification'):
            suggs = message.get('metadata', {}).get('suggestions', [])
            if suggs:
                st.info("The assistant found multiple interpretations. Pick one to refine:")
                cols = st.columns(len(suggs))
                for i, sug in enumerate(suggs):
                    with cols[i]:
                        label = sug.get('intent', 'unknown')
                        score = sug.get('score', 0)
                        if st.button(f"🎯 {label}\n({score:.0%})", key=f"clarify_{index}_{i}"):
                            # Resubmit with forced intent
                            st.session_state.pending_query = message.get('user_query', message.get('content', ''))
                            st.session_state.force_intent = label
                            st.rerun()

        # DSL preview
        if 'siem_query' in message and message['siem_query']:
            with st.expander("🧩 Show Generated DSL", expanded=st.session_state.get("show_dsl_default", False)):
                try:
                    st.json(message['siem_query'])
                except Exception:
                    st.write(message['siem_query'])

        # Display results if available
        if 'results' in message and message['results']:
            with st.expander("📋 View Detailed Results", expanded=False):
                results = message['results']

                # Pagination controls
                pag_cols = st.columns(3)
                with pag_cols[0]:
                    if st.button("⬅️ Prev", key=f"prev_{index}"):
                        current_offset = int(st.session_state.filters.get("offset", 0))
                        page_size = int(st.session_state.filters.get("limit", 100))
                        new_offset = max(0, current_offset - page_size)
                        st.session_state.filters["offset"] = new_offset
                        st.session_state.pending_query = message.get('user_query', '')
                        st.rerun()
                with pag_cols[1]:
                    st.caption(f"Offset: {int(st.session_state.filters.get('offset', 0))}")
                with pag_cols[2]:
                    if st.button("Next ➡️", key=f"next_{index}"):
                        current_offset = int(st.session_state.filters.get("offset", 0))
                        page_size = int(st.session_state.filters.get("limit", 100))
                        st.session_state.filters["offset"] = current_offset + page_size
                        st.session_state.pending_query = message.get('user_query', '')
                        st.rerun()
                
                # Convert to DataFrame
                try:
                    df = pd.DataFrame(results[:100])  # Limit to 100 for display
                    
                    # Format timestamp columns
                    for col in df.columns:
                        if 'timestamp' in col.lower() or col == '@timestamp':
                            try:
                                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                pass
                    
                    # Add search/filter for large datasets
                    if len(df) > 10:
                        search_term = st.text_input("🔍 Search in results:", key=f"search_{index}")
                        if search_term:
                            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                            df = df[mask]
                    
                    st.dataframe(df, use_container_width=True)
                    
                    # Enhanced export options
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 CSV",
                            data=csv,
                            file_name=f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    with col2:
                        json_str = df.to_json(orient='records', indent=2)
                        st.download_button(
                            label="📥 JSON",
                            data=json_str,
                            file_name=f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    with col3:
                        # Export Pack (ZIP) - summary, results.json, siem_query.json, entities.json, metadata.json
                        zip_bytes = _build_export_pack(message)
                        st.download_button(
                            label="📦 Export Pack (ZIP)",
                            data=zip_bytes,
                            file_name=f"export_pack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                    
                    # Quick stats
                    st.divider()
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Rows", len(df))
                    col2.metric("Columns", len(df.columns))
                    if len(df) > 0:
                        col3.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                    
                except Exception as e:
                    st.json(results[:10])  # Fallback to JSON
        
        # Display visualizations
        if 'visualizations' in message and message['visualizations']:
            with st.expander("📊 Interactive Visualizations", expanded=True):
                viz_tabs = st.tabs([f"Chart {i+1}" for i in range(len(message['visualizations']))])
                
                for idx, viz in enumerate(message['visualizations']):
                    with viz_tabs[idx]:
                        try:
                            # Handle different visualization types
                            if viz.get('type') == 'bar':
                                fig = px.bar(
                                    x=viz['x'], 
                                    y=viz['y'], 
                                    title=viz.get('title', 'Bar Chart'),
                                    color_discrete_sequence=['#667eea']
                                )
                                fig.update_layout(hovermode='x unified')
                                st.plotly_chart(fig, use_container_width=True)
                            
                            elif viz.get('type') == 'line':
                                fig = px.line(
                                    x=viz['x'], 
                                    y=viz['y'], 
                                    title=viz.get('title', 'Line Chart'),
                                    line_shape='spline'
                                )
                                fig.update_traces(line_color='#667eea', line_width=3)
                                st.plotly_chart(fig, use_container_width=True)
                            
                            elif viz.get('type') == 'pie':
                                fig = px.pie(
                                    values=viz['values'], 
                                    names=viz['labels'], 
                                    title=viz.get('title', 'Pie Chart'),
                                    hole=0.3
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            elif viz.get('type') == 'heatmap':
                                fig = px.density_heatmap(
                                    x=viz.get('x'), 
                                    y=viz.get('y'),
                                    title=viz.get('title', 'Heatmap')
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            elif viz.get('type') == 'scatter':
                                fig = px.scatter(
                                    x=viz.get('x'), 
                                    y=viz.get('y'),
                                    title=viz.get('title', 'Scatter Plot'),
                                    size=viz.get('size'),
                                    color=viz.get('color')
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # Chart export
                            chart_html = fig.to_html()
                            st.download_button(
                                label="📥 Download Chart",
                                data=chart_html,
                                file_name=f"chart_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                mime="text/html",
                                key=f"download_chart_{index}_{idx}"
                            )
                            
                        except Exception as e:
                            st.warning(f"Could not render visualization: {e}")
        
        # Display entities if available
        if 'entities' in message and message['entities']:
            with st.expander("🏷️ Extracted Entities", expanded=False):
                entities = message['entities']
                if isinstance(entities, list):
                    for entity in entities:
                        st.markdown(f"- **{entity.get('type', 'unknown')}**: {entity.get('value', 'N/A')}")
                elif isinstance(entities, dict):
                    for entity_type, values in entities.items():
                        if values:
                            st.markdown(f"**{entity_type.replace('_', ' ').title()}**: {', '.join(map(str, values))}")
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_realtime_dashboard():
    """Display real-time monitoring dashboard."""
    st.subheader("📡 Real-Time Security Monitoring")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Simulated real-time metrics (would be replaced with actual API calls)
    with col1:
        st.metric(
            label="🚨 Active Alerts",
            value="23",
            delta="+3"
        )
    
    with col2:
        st.metric(
            label="🔐 Failed Logins",
            value="45",
            delta="-12",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="🌐 Network Events",
            value="1,234",
            delta="+156"
        )
    
    with col4:
        st.metric(
            label="⚡ Events/sec",
            value="12.5",
            delta="+2.3"
        )
    
    # Mini timeline chart
    col1, col2 = st.columns(2)
    
    with col1:
        # Simulated alert timeline
        timeline_data = pd.DataFrame({
            'time': pd.date_range(start='now', periods=24, freq='H'),
            'alerts': [5, 7, 3, 12, 8, 15, 9, 6, 4, 11, 13, 8, 7, 9, 14, 6, 8, 10, 12, 7, 9, 11, 8, 6]
        })
        fig = px.line(timeline_data, x='time', y='alerts', title='Alert Timeline (24h)')
        fig.update_traces(line_color='#667eea', fill='tozeroy')
        fig.update_layout(height=250, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Severity distribution
        severity_data = pd.DataFrame({
            'severity': ['Critical', 'High', 'Medium', 'Low'],
            'count': [5, 12, 23, 45]
        })
        fig = px.pie(severity_data, values='count', names='severity', 
                     title='Alert Severity Distribution',
                     color_discrete_sequence=['#ff4444', '#ff8800', '#ffbb00', '#00bb00'])
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function."""
    display_header()
    display_sidebar()
    
    # Check backend on first load
    if 'health_checked' not in st.session_state:
        healthy, _ = check_backend_health()
        st.session_state.health_checked = True
        if not healthy:
            st.warning("⚠️ Backend is not responding. Please start the assistant server: `python assistant/main.py`")
    
    # Mode selection
    mode = st.radio(
        "🎛️ Select Mode:",
        ["💬 Chat Mode", "📊 Dashboard Mode", "🔍 Compare Mode"],
        horizontal=True
    )
    
    st.divider()
    
    if mode == "📊 Dashboard Mode":
        display_realtime_dashboard()
        st.divider()
        
        # Add quick insights
        st.subheader("🎯 Quick Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("🔥 **Top Threat**: Brute force attacks detected from IP 192.168.1.100")
            st.warning("⚠️ **Attention Required**: 5 critical alerts need review")
        
        with col2:
            st.success("✅ **System Health**: All monitoring agents are operational")
            st.info("📈 **Trend**: Failed login attempts decreased by 15% from yesterday")
        
        return
    
    elif mode == "🔍 Compare Mode":
        st.subheader("🔍 Query Comparison Mode")
        st.info("Run multiple queries and compare results side-by-side")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Query 1:", key="compare_query_1", placeholder="e.g., Show alerts from last hour")
            if st.button("🔍 Run Query 1", use_container_width=True):
                st.info("Query 1 results would appear here")
        
        with col2:
            st.text_input("Query 2:", key="compare_query_2", placeholder="e.g., Show alerts from last day")
            if st.button("🔍 Run Query 2", use_container_width=True):
                st.info("Query 2 results would appear here")
        
        st.divider()
        st.info("💡 Comparison feature coming soon!")
        return
    
    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚨 Show Critical Alerts", use_container_width=True):
            st.session_state.pending_query = "Show all critical severity alerts from the last hour"
            st.rerun()
    
    with col2:
        if st.button("🔐 Failed Logins", use_container_width=True):
            st.session_state.pending_query = "Find all failed authentication attempts today"
            st.rerun()
    
    with col3:
        if st.button("🌐 Network Activity", use_container_width=True):
            st.session_state.pending_query = "Show unusual network connections"
            st.rerun()
    
    with col4:
        if st.button("📊 Security Summary", use_container_width=True):
            st.session_state.pending_query = "Give me a security overview for today"
            st.rerun()
    
    st.divider()

    # New top-level tabs for Investigate and Dashboard (Chat remains below for continuity)
    tabs = st.tabs(["🧭 Investigate", "📊 Dashboard", "📑 Reports"])

    with tabs[0]:
        st.subheader("🧭 Guided Investigations")
        st.caption("Use these workflows to quickly ask common security questions with precise filters.")

        inv1, inv2, inv3 = st.columns(3)
        with inv1:
            st.markdown("**Failed Logins**")
            inv_user = st.text_input("Username (optional)", key="inv_user")
            inv_time = st.selectbox("Time", ["Last hour", "Last 24 hours", "Last 7 days"], key="inv_time_failed")
            if st.button("Run", key="inv_failed_run", use_container_width=True):
                q = "Show failed login attempts"
                if inv_user:
                    q += f" for user {inv_user}"
                # map time to filters
                time_map = {"Last hour": "now-1h", "Last 24 hours": "now-1d", "Last 7 days": "now-7d"}
                st.session_state.pending_query = q
                st.session_state.filters["time_window_gte"] = time_map.get(inv_time, "now-1d")
                st.rerun()
        with inv2:
            st.markdown("**Security Alerts**")
            inv_sev = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"], key="inv_sev_alerts")
            inv_time2 = st.selectbox("Time", ["Last hour", "Last 24 hours", "Last 7 days"], key="inv_time_alerts")
            if st.button("Run", key="inv_alerts_run", use_container_width=True):
                q = "Show security alerts"
                st.session_state.pending_query = q
                # map filters
                time_map = {"Last hour": "now-1h", "Last 24 hours": "now-1d", "Last 7 days": "now-7d"}
                st.session_state.filters["time_window_gte"] = time_map.get(inv_time2, "now-1d")
                st.session_state.filters["severity"] = inv_sev
                st.rerun()
        with inv3:
            st.markdown("**Network Activity**")
            inv_ip = st.text_input("IP (optional)", key="inv_ip")
            inv_time3 = st.selectbox("Time", ["Last hour", "Last 24 hours", "Last 7 days"], key="inv_time_net")
            if st.button("Run", key="inv_network_run", use_container_width=True):
                q = "Show network activity"
                if inv_ip:
                    q += f" for IP {inv_ip}"
                time_map = {"Last hour": "now-1h", "Last 24 hours": "now-1d", "Last 7 days": "now-7d"}
                st.session_state.pending_query = q
                st.session_state.filters["time_window_gte"] = time_map.get(inv_time3, "now-1d")
                st.rerun()

    with tabs[1]:
        display_realtime_dashboard()

    with tabs[2]:
        st.subheader("📑 Reports")
        st.caption("Generate ready-to-share security reports with one click.")

        col_a, col_b, col_c = st.columns(3)

        def _run_report(title: str, query: str, filters: dict, limit: int = 200):
            st.info(f"Running: {title}")
            success, resp = query_assistant(query, filters=filters, limit=limit)
            if not success:
                st.error(str(resp))
                return
            results = resp.get('data', resp.get('results', []))
            report_message = {
                'role': 'assistant',
                'content': resp.get('answer', resp.get('summary', title)),
                'summary': resp.get('answer', resp.get('summary', title)),
                'results': results,
                'visualizations': resp.get('visualizations', []),
                'entities': resp.get('entities', {}),
                'siem_query': resp.get('siem_query', {}),
                'metadata': resp.get('metadata', {}),
            }
            st.success("Report generated")
            # Offer export
            pack = _build_export_pack(report_message)
            st.download_button(
                label="📦 Download Report Pack (ZIP)",
                data=pack,
                file_name=f"report_pack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )
            # Show preview table (first 50 rows)
            if results:
                try:
                    df = pd.DataFrame(results[:50])
                    st.dataframe(df, use_container_width=True)
                except Exception:
                    st.json(results[:10])

        with col_a:
            st.markdown("**Failed Logins Report (24h)**")
            if st.button("Generate", key="rpt_failed_24h", use_container_width=True):
                _run_report(
                    title="Failed Logins Report (24h)",
                    query="Show failed login attempts",
                    filters={"time_window_gte": "now-1d"},
                    limit=200,
                )
        with col_b:
            st.markdown("**High Severity Alerts (24h)**")
            if st.button("Generate", key="rpt_alerts_high_24h", use_container_width=True):
                _run_report(
                    title="High Severity Alerts (24h)",
                    query="Show security alerts",
                    filters={"time_window_gte": "now-1d", "severity": "High"},
                    limit=200,
                )
        with col_c:
            st.markdown("**Network Activity Summary (24h)**")
            if st.button("Generate", key="rpt_network_24h", use_container_width=True):
                _run_report(
                    title="Network Activity Summary (24h)",
                    query="Show network activity",
                    filters={"time_window_gte": "now-1d", "index_class": st.session_state.filters.get("dataset", "Auto")},
                    limit=200,
                )

    st.divider()
    
    # Display chat history
    st.subheader("💬 Conversation")
    
    chat_container = st.container()
    with chat_container:
        for idx, message in enumerate(st.session_state.chat_history):
            display_chat_message(message, idx)
    
    # Handle pending query from example buttons
    if 'pending_query' in st.session_state:
        user_input = st.session_state.pending_query
        del st.session_state.pending_query
    else:
        user_input = None
    
    # Command palette info
    with st.expander("⌨️ Command Palette & Shortcuts"):
        st.markdown("""
        <div class="command-palette">
            <h4>🎯 Quick Commands (type in chat)</h4>
            <ul>
                <li><span class="keyboard-shortcut">/help</span> - Show help and shortcuts</li>
                <li><span class="keyboard-shortcut">/clear</span> - Clear conversation</li>
                <li><span class="keyboard-shortcut">/export</span> - Export chat history</li>
                <li><span class="keyboard-shortcut">/stats</span> - Show statistics</li>
                <li><span class="keyboard-shortcut">/critical</span> - Show critical alerts</li>
                <li><span class="keyboard-shortcut">/failed</span> - Show failed logins</li>
                <li><span class="keyboard-shortcut">/network</span> - Network activity</li>
                <li><span class="keyboard-shortcut">/summary</span> - Security summary</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Smart suggestions based on recent queries
    if st.session_state.query_history:
        with st.expander("💡 Smart Suggestions Based on Your Activity"):
            recent_keywords = set()
            for query in st.session_state.query_history[-5:]:
                words = re.findall(r'\b\w+\b', query.lower())
                recent_keywords.update([w for w in words if len(w) > 4])
            
            suggestions = [
                f"Show more details about {kw}" for kw in list(recent_keywords)[:3]
            ]
            
            col1, col2, col3 = st.columns(3)
            for idx, suggestion in enumerate(suggestions):
                with [col1, col2, col3][idx % 3]:
                    if st.button(f"💡 {suggestion}", key=f"suggest_{idx}"):
                        st.session_state.pending_query = suggestion
                        st.rerun()
    
    # Chat input with voice-like placeholder
    user_input = st.chat_input("💭 Ask anything or use /command (e.g., '/help', 'Show failed logins', 'Find threats')...", key="chat_input") or user_input
    
    # Handle command palette
    if user_input and user_input.startswith("/"):
        command = user_input.lower().strip()
        
        if command == "/help":
            st.info("""
            **🎯 Available Commands:**
            - `/clear` - Clear conversation
            - `/export` - Export conversation
            - `/stats` - Show statistics
            - `/critical` - Show critical alerts
            - `/failed` - Show failed logins
            - `/network` - Network activity
            - `/summary` - Security summary
            
            **💡 Tips:**
            - Ask questions naturally in plain English
            - Use filters in the sidebar for precise results
            - Click example queries for quick starts
            - Star your favorite queries for later
            """)
            user_input = None
        
        elif command == "/clear":
            st.session_state.chat_history = []
            st.success("✅ Conversation cleared!")
            st.rerun()
        
        elif command == "/export":
            data, filename, mime = export_conversation("json")
            st.download_button(
                label="📥 Download Conversation",
                data=data,
                file_name=filename,
                mime=mime
            )
            user_input = None
        
        elif command == "/stats":
            insights = get_query_insights()
            if insights:
                st.json(insights)
            else:
                st.info("No statistics available yet")
            user_input = None
        
        elif command == "/critical":
            user_input = "Show all critical severity alerts"
        
        elif command == "/failed":
            user_input = "Show failed login attempts"
        
        elif command == "/network":
            user_input = "Show network activity and connections"
        
        elif command == "/summary":
            user_input = "Give me a security summary for today"
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Show processing indicator with progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 Analyzing query...")
        progress_bar.progress(20)
        time.sleep(0.1)
        
        status_text.text("� Processing with NLP...")
        progress_bar.progress(40)
        
        # Apply filters if set
        filters = None
        if any(v != "All" for v in [st.session_state.filters.get("severity"), st.session_state.filters.get("data_source")]):
            filters = st.session_state.filters
        
        limit = st.session_state.filters.get("limit")
        offset = st.session_state.filters.get("offset", 0)
        force_intent = st.session_state.pop("force_intent", None)
        success, response = query_assistant(user_input, filters, limit=limit, offset=offset, force_intent=force_intent)
        
        progress_bar.progress(80)
        status_text.text("✨ Formatting results...")
        time.sleep(0.1)
        
        progress_bar.progress(100)
        status_text.empty()
        progress_bar.empty()
        
        if success:
            # Add assistant response to history
            # Backend returns 'data' field, map it to 'results' for display
            results_data = response.get('data', response.get('results', []))
            
            assistant_message = {
                'role': 'assistant',
                'content': response.get('answer', response.get('summary', 'Query processed successfully')),
                'summary': response.get('answer', response.get('summary', '')),
                'results': results_data,
                'visualizations': response.get('visualizations', []),
                'entities': response.get('entities', {}),
                'siem_query': response.get('siem_query', {}),
                'user_query': response.get('user_query', user_input),
                'metadata': {
                    'intent': response.get('intent', 'unknown'),
                    'confidence_score': response.get('confidence', response.get('metadata', {}).get('confidence_score', 0)),
                    'results_count': response.get('result_count', len(results_data)),
                    'processing_time_seconds': response.get('execution_time', response.get('metadata', {}).get('processing_time_seconds', 0)),
                    'data_sources': response.get('metadata', {}).get('data_sources', []),
                    'needs_clarification': response.get('metadata', {}).get('needs_clarification', False),
                    'suggestions': response.get('metadata', {}).get('suggestions', [])
                },
                'timestamp': datetime.now().isoformat()
            }
            st.session_state.chat_history.append(assistant_message)
        else:
            # Add error message
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': f"❌ {response}",
                'timestamp': datetime.now().isoformat()
            })
        
        # Rerun to display new messages
        st.rerun()
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🛡️ SIEM NLP Assistant**")
        st.caption("Natural language security insights")
    
    with col2:
        st.markdown("**🏆 SIH 2025**")
        st.caption("Team Kartavya")
    
    with col3:
        st.markdown("**🔗 Quick Links**")
        st.caption(f"[API Docs]({BACKEND_URL}/assistant/docs) | [Health]({BACKEND_URL}/assistant/ping)")

if __name__ == "__main__":
    main()

"""
Streamlit Web Interface for Kartavya SIEM
Deploy this to Streamlit Cloud for instant web access
"""

import streamlit as st
import requests
import json
import subprocess
import threading
import time
import os

# Configure Streamlit page
st.set_page_config(
    page_title="🔒 Kartavya SIEM",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 0.5rem 0;
    }
    .cli-output {
        background: #1a1a1a;
        color: #00ff00;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: monospace;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# Start backend in background (only once)
@st.cache_resource
def start_backend():
    """Start the backend server"""
    def run_backend():
        os.environ['API_HOST'] = '0.0.0.0'
        os.environ['API_PORT'] = '8000'
        os.environ['ENVIRONMENT'] = 'production'
        
        # Install dependencies and start backend
        try:
            subprocess.run(['pip', 'install', '-r', 'backend/requirements.txt'], check=True)
            subprocess.run(['pip', 'install', '-e', 'cli/'], check=True)
            os.chdir('backend')
            subprocess.run(['python', 'main.py'])
        except Exception as e:
            st.error(f"Backend failed to start: {e}")
    
    thread = threading.Thread(target=run_backend, daemon=True)
    thread.start()
    time.sleep(10)  # Give backend time to start
    return True

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🔒 Kartavya SIEM</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Security Information and Event Management")
    
    # Initialize backend
    backend_ready = start_backend()
    
    # Sidebar
    st.sidebar.title("🔧 Control Panel")
    
    # Status check
    st.sidebar.subheader("🟢 System Status")
    
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            st.sidebar.success("✅ Backend API: Healthy")
            backend_healthy = True
        else:
            st.sidebar.error("❌ Backend API: Unhealthy")
            backend_healthy = False
    except:
        st.sidebar.warning("⚠️ Backend API: Starting...")
        backend_healthy = False
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "🤖 AI Chat", "🔍 Events", "⚙️ CLI"])
    
    with tab1:
        st.header("📊 Security Dashboard")
        
        if backend_healthy:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="status-card">
                    <h3>🛡️ Active Alerts</h3>
                    <h2>12</h2>
                    <p>Security incidents detected</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="status-card">
                    <h3>📈 Events Today</h3>
                    <h2>1,247</h2>
                    <p>Security events processed</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="status-card">
                    <h3>🔄 System Health</h3>
                    <h2>98%</h2>
                    <p>Uptime and availability</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Quick API test
            st.subheader("🔗 API Connectivity Test")
            if st.button("Test Backend API"):
                try:
                    response = requests.get("http://localhost:8000/", timeout=5)
                    st.success(f"✅ API Response: {response.status_code}")
                    st.json(response.json())
                except Exception as e:
                    st.error(f"❌ API Error: {e}")
        else:
            st.warning("Backend is starting up. Please wait...")
    
    with tab2:
        st.header("🤖 AI Security Assistant")
        
        if backend_healthy:
            # Chat interface
            user_query = st.text_input("Ask the AI assistant:", placeholder="Show me failed login attempts from last hour")
            
            if st.button("Send Query") and user_query:
                with st.spinner("Processing your query..."):
                    try:
                        response = requests.post(
                            "http://localhost:8000/api/assistant/chat",
                            json={"query": user_query},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.success("✅ Query processed successfully!")
                            
                            # Display results
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("📋 Summary")
                                st.write(result.get("summary", "No summary available"))
                                
                                st.subheader("🎯 Intent & Confidence")
                                st.write(f"**Intent:** {result.get('intent', 'unknown')}")
                                st.write(f"**Confidence:** {result.get('confidence', 0):.1%}")
                            
                            with col2:
                                st.subheader("📊 Results")
                                if result.get("results"):
                                    st.json(result["results"][:5])  # Show first 5 results
                                else:
                                    st.info("No results returned")
                        else:
                            st.error(f"API Error: {response.status_code}")
                    
                    except Exception as e:
                        st.error(f"Request failed: {e}")
        else:
            st.warning("AI Assistant requires backend API to be running")
    
    with tab3:
        st.header("🔍 Security Events")
        
        if backend_healthy:
            col1, col2 = st.columns(2)
            
            with col1:
                event_type = st.selectbox("Event Type", [
                    "authentication", "failed-logins", "successful-logins", 
                    "network-activity", "process-activity", "system-metrics"
                ])
            
            with col2:
                time_range = st.selectbox("Time Range", ["1h", "6h", "24h", "7d"])
            
            if st.button("Fetch Events"):
                with st.spinner("Fetching security events..."):
                    try:
                        response = requests.post(
                            f"http://localhost:8000/api/events/{event_type}",
                            json={"query": "", "time_range": time_range, "limit": 50},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Found {len(result.get('results', {}).get('events', []))} events")
                            
                            # Display events
                            if result.get("results", {}).get("events"):
                                st.subheader("📋 Recent Events")
                                events = result["results"]["events"][:10]  # Show first 10
                                
                                for i, event in enumerate(events):
                                    with st.expander(f"Event {i+1}: {event.get('event', {}).get('action', 'Unknown')}"):
                                        st.json(event)
                            else:
                                st.info("No events found for the selected criteria")
                        else:
                            st.error(f"API Error: {response.status_code}")
                    
                    except Exception as e:
                        st.error(f"Request failed: {e}")
        else:
            st.warning("Event queries require backend API to be running")
    
    with tab4:
        st.header("🖥️ CLI Interface")
        
        st.markdown("""
        ### Quick CLI Commands
        Use these commands to interact with the Kartavya CLI:
        """)
        
        # CLI command input
        cli_command = st.selectbox("Select Command", [
            "kartavya --help",
            "kartavya health",
            "kartavya config show",
            "kartavya chat ask 'show security alerts'",
            "kartavya events auth --time-range 1h",
            "kartavya reports list"
        ])
        
        custom_command = st.text_input("Or enter custom command:", placeholder="kartavya query execute 'your query here'")
        
        command_to_run = custom_command if custom_command else cli_command
        
        if st.button("Execute CLI Command"):
            with st.spinner(f"Executing: {command_to_run}"):
                try:
                    # Set environment for CLI
                    env = os.environ.copy()
                    env['KARTAVYA_API_URL'] = 'http://localhost:8000'
                    env['KARTAVYA_OUTPUT_FORMAT'] = 'json'
                    env['KARTAVYA_COLOR'] = 'false'
                    
                    result = subprocess.run(
                        command_to_run.split(),
                        capture_output=True,
                        text=True,
                        timeout=30,
                        env=env
                    )
                    
                    st.subheader("📤 Command Output")
                    if result.stdout:
                        st.markdown(f'<div class="cli-output">{result.stdout}</div>', unsafe_allow_html=True)
                    
                    if result.stderr:
                        st.subheader("⚠️ Errors")
                        st.error(result.stderr)
                    
                    st.subheader("📊 Execution Info")
                    st.write(f"**Exit Code:** {result.returncode}")
                    st.write(f"**Command:** `{command_to_run}`")
                
                except subprocess.TimeoutExpired:
                    st.error("⏱️ Command timed out (30s limit)")
                except FileNotFoundError:
                    st.error("❌ CLI not installed. Run: `pip install -e cli/`")
                except Exception as e:
                    st.error(f"❌ Execution failed: {e}")
        
        # Installation instructions
        st.subheader("📥 CLI Installation")
        st.code("""
# Install the CLI
pip install -e cli/

# Configure
kartavya setup

# Start using
kartavya chat interactive
        """, language="bash")

    # Footer
    st.markdown("---")
    st.markdown("**🔒 Kartavya SIEM v1.0.0** - Deployed on Streamlit Cloud • [Documentation](#) • [GitHub](#)")

if __name__ == "__main__":
    main()

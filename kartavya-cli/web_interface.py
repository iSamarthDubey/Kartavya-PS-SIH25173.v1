"""
Simple web interface for Kartavya CLI cloud deployment.
Provides a basic web UI for accessing CLI functionality through a browser.
"""

import os
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

from kartavya_cli.core.client import APIClient, APIError
from kartavya_cli.core.config import Config
from kartavya_cli.core.output import OutputFormatter

app = FastAPI(
    title="Kartavya CLI Web Interface",
    description="Web interface for Kartavya SIEM NLP Assistant CLI",
    version="1.0.0"
)

# Templates directory would be created in a real deployment
templates = Jinja2Templates(directory="templates")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment platforms."""
    return {"status": "healthy", "service": "kartavya-cli-web"}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main interface page."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kartavya CLI - Web Interface</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
                color: #333;
            }
            .header {
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                border-radius: 8px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .form-group {
                margin: 15px 0;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #555;
            }
            input[type="text"], textarea, select {
                width: 100%;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                box-sizing: border-box;
            }
            input[type="text"]:focus, textarea:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            .btn {
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 5px;
                transition: background 0.3s;
            }
            .btn:hover {
                background: #5a6fd8;
            }
            .btn-secondary {
                background: #6c757d;
            }
            .btn-secondary:hover {
                background: #5a6268;
            }
            .result {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-top: 20px;
                border-radius: 0 5px 5px 0;
                white-space: pre-wrap;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                max-height: 400px;
                overflow-y: auto;
            }
            .tabs {
                display: flex;
                background: white;
                border-radius: 8px 8px 0 0;
                margin: 20px 0 0 0;
            }
            .tab {
                flex: 1;
                text-align: center;
                padding: 15px;
                cursor: pointer;
                border-bottom: 3px solid transparent;
                transition: all 0.3s;
            }
            .tab.active {
                background: #667eea;
                color: white;
                border-bottom: 3px solid #4c63d2;
            }
            .tab-content {
                display: none;
                background: white;
                padding: 25px;
                border-radius: 0 0 8px 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .tab-content.active {
                display: block;
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .feature-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-left: 4px solid #667eea;
            }
            .feature-title {
                color: #667eea;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #667eea;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                border-left: 4px solid #dc3545;
            }
            .success {
                background: #d4edda;
                color: #155724;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                border-left: 4px solid #28a745;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ Kartavya CLI</h1>
            <p>SIEM NLP Assistant - Web Interface</p>
            <p>Intelligent Security Operations & Threat Hunting</p>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="showTab('chat')">💬 AI Chat</div>
            <div class="tab" onclick="showTab('query')">🔍 Query</div>
            <div class="tab" onclick="showTab('events')">🚨 Events</div>
            <div class="tab" onclick="showTab('about')">ℹ️ About</div>
        </div>

        <!-- Chat Tab -->
        <div id="chat" class="tab-content active">
            <h2>AI Assistant Chat</h2>
            <p>Ask questions about security events, threats, or SIEM operations using natural language.</p>
            
            <form id="chatForm">
                <div class="form-group">
                    <label for="chatMessage">Your Question:</label>
                    <textarea id="chatMessage" name="message" rows="3" placeholder="e.g., Show me failed login attempts from the last hour..."></textarea>
                </div>
                <button type="submit" class="btn">Send Message</button>
            </form>
            
            <div id="chatResult"></div>
        </div>

        <!-- Query Tab -->
        <div id="query" class="tab-content">
            <h2>Execute Queries</h2>
            <p>Execute natural language queries against your SIEM data.</p>
            
            <form id="queryForm">
                <div class="form-group">
                    <label for="queryText">Natural Language Query:</label>
                    <textarea id="queryText" name="query" rows="3" placeholder="e.g., Find network connections to suspicious IPs..."></textarea>
                </div>
                <div class="form-group">
                    <label for="queryLimit">Results Limit:</label>
                    <select id="queryLimit" name="limit">
                        <option value="10">10 results</option>
                        <option value="50" selected>50 results</option>
                        <option value="100">100 results</option>
                    </select>
                </div>
                <button type="submit" class="btn">Execute Query</button>
                <button type="button" class="btn btn-secondary" onclick="translateQuery()">Translate Only</button>
            </form>
            
            <div id="queryResult"></div>
        </div>

        <!-- Events Tab -->
        <div id="events" class="tab-content">
            <h2>Platform Events</h2>
            <p>View and analyze security events from your SIEM platform.</p>
            
            <form id="eventsForm">
                <div class="form-group">
                    <label for="eventType">Event Type:</label>
                    <select id="eventType" name="eventType">
                        <option value="">All Events</option>
                        <option value="authentication">Authentication</option>
                        <option value="network">Network</option>
                        <option value="system">System</option>
                        <option value="security">Security</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="eventLimit">Number of Events:</label>
                    <select id="eventLimit" name="limit">
                        <option value="25">25 events</option>
                        <option value="50" selected>50 events</option>
                        <option value="100">100 events</option>
                    </select>
                </div>
                <button type="submit" class="btn">Get Events</button>
                <button type="button" class="btn btn-secondary" onclick="getFailedLogins()">Failed Logins</button>
                <button type="button" class="btn btn-secondary" onclick="getNetworkEvents()">Network Events</button>
            </form>
            
            <div id="eventsResult"></div>
        </div>

        <!-- About Tab -->
        <div id="about" class="tab-content">
            <h2>About Kartavya CLI</h2>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-title">🤖 AI-Powered Assistant</div>
                    <p>Natural language processing for security queries and threat hunting with intelligent responses.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-title">🔍 Event Analysis</div>
                    <p>Comprehensive platform event analysis with filtering, search, and statistical insights.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-title">📊 Report Generation</div>
                    <p>Automated security reporting with scheduling, export, and customization options.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-title">💬 Query Translation</div>
                    <p>Convert natural language questions into structured database queries automatically.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-title">📈 Dashboard Metrics</div>
                    <p>Real-time system metrics, performance monitoring, and alerting capabilities.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-title">👥 Admin Tools</div>
                    <p>User management, permission control, and comprehensive audit logging.</p>
                </div>
            </div>

            <div class="card">
                <h3>Installation</h3>
                <p>Install Kartavya CLI on your local machine:</p>
                <div class="result">curl -sSL https://install.kartavya.dev | bash</div>
                
                <h3>Usage Examples</h3>
                <div class="result">
# Setup and configuration
kartavya setup --url YOUR_API_URL --api-key YOUR_KEY

# Interactive AI chat
kartavya chat interactive

# Execute queries
kartavya query execute "Show me failed login attempts from last hour"

# Generate reports  
kartavya reports generate security --start-date 2024-01-01

# List events
kartavya events list --type authentication --limit 50
                </div>

                <h3>Documentation & Support</h3>
                <p>📚 Documentation: <a href="https://kartavya-cli.readthedocs.io" target="_blank">https://kartavya-cli.readthedocs.io</a></p>
                <p>💬 Support: <a href="mailto:support@kartavya.dev">support@kartavya.dev</a></p>
                <p>🔧 GitHub: <a href="https://github.com/kartavya-team/kartavya-cli" target="_blank">https://github.com/kartavya-team/kartavya-cli</a></p>
            </div>
        </div>

        <script>
            function showTab(tabName) {
                // Hide all tab contents
                const contents = document.querySelectorAll('.tab-content');
                contents.forEach(content => content.classList.remove('active'));
                
                // Remove active class from all tabs
                const tabs = document.querySelectorAll('.tab');
                tabs.forEach(tab => tab.classList.remove('active'));
                
                // Show selected tab
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');
            }

            // Chat form handler
            document.getElementById('chatForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const message = formData.get('message');
                
                if (!message.trim()) return;
                
                showLoading('chatResult');
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: message})
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showResult('chatResult', result.response, 'success');
                    } else {
                        showResult('chatResult', result.detail || 'Error occurred', 'error');
                    }
                } catch (error) {
                    showResult('chatResult', 'Network error: ' + error.message, 'error');
                }
            });

            // Query form handler
            document.getElementById('queryForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const query = formData.get('query');
                const limit = formData.get('limit');
                
                if (!query.trim()) return;
                
                showLoading('queryResult');
                
                try {
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({query: query, limit: parseInt(limit)})
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        const formatted = Array.isArray(result.results) ? 
                            JSON.stringify(result.results, null, 2) : 
                            JSON.stringify(result, null, 2);
                        showResult('queryResult', formatted, 'success');
                    } else {
                        showResult('queryResult', result.detail || 'Error occurred', 'error');
                    }
                } catch (error) {
                    showResult('queryResult', 'Network error: ' + error.message, 'error');
                }
            });

            // Events form handler
            document.getElementById('eventsForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const eventType = formData.get('eventType');
                const limit = formData.get('limit');
                
                showLoading('eventsResult');
                
                try {
                    const response = await fetch('/api/events', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({event_type: eventType || null, limit: parseInt(limit)})
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        const formatted = Array.isArray(result.events) ? 
                            JSON.stringify(result.events, null, 2) : 
                            JSON.stringify(result, null, 2);
                        showResult('eventsResult', formatted, 'success');
                    } else {
                        showResult('eventsResult', result.detail || 'Error occurred', 'error');
                    }
                } catch (error) {
                    showResult('eventsResult', 'Network error: ' + error.message, 'error');
                }
            });

            function showLoading(elementId) {
                document.getElementById(elementId).innerHTML = 
                    '<div class="loading">⏳ Processing request...</div>';
            }

            function showResult(elementId, content, type) {
                const className = type === 'error' ? 'result error' : 'result success';
                document.getElementById(elementId).innerHTML = 
                    `<div class="${className}">${content}</div>`;
            }

            function translateQuery() {
                const query = document.getElementById('queryText').value;
                if (!query.trim()) return;
                
                showLoading('queryResult');
                
                fetch('/api/translate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                })
                .then(response => response.json())
                .then(result => {
                    if (result.translated_query) {
                        showResult('queryResult', result.translated_query, 'success');
                    } else {
                        showResult('queryResult', 'Translation failed', 'error');
                    }
                })
                .catch(error => {
                    showResult('queryResult', 'Network error: ' + error.message, 'error');
                });
            }

            function getFailedLogins() {
                showLoading('eventsResult');
                
                fetch('/api/events', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({event_type: 'failed_login', limit: 50})
                })
                .then(response => response.json())
                .then(result => {
                    const formatted = JSON.stringify(result.events || result, null, 2);
                    showResult('eventsResult', formatted, 'success');
                })
                .catch(error => {
                    showResult('eventsResult', 'Network error: ' + error.message, 'error');
                });
            }

            function getNetworkEvents() {
                showLoading('eventsResult');
                
                fetch('/api/events', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({event_type: 'network', limit: 50})
                })
                .then(response => response.json())
                .then(result => {
                    const formatted = JSON.stringify(result.events || result, null, 2);
                    showResult('eventsResult', formatted, 'success');
                })
                .catch(error => {
                    showResult('eventsResult', 'Network error: ' + error.message, 'error');
                });
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# API endpoints for the web interface
@app.post("/api/chat")
async def api_chat(request: Request):
    """Chat with AI assistant endpoint."""
    try:
        data = await request.json()
        message = data.get("message", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        client = APIClient()
        result = client.chat_with_assistant(message)
        client.close()
        
        return {"response": result.get("response", "No response received")}
    
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"API Error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def api_query(request: Request):
    """Execute query endpoint."""
    try:
        data = await request.json()
        query = data.get("query", "")
        limit = data.get("limit", 50)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        client = APIClient()
        result = client.execute_query(query)
        client.close()
        
        return {"results": result.get("results", [])}
    
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"API Error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate")
async def api_translate(request: Request):
    """Translate query endpoint."""
    try:
        data = await request.json()
        query = data.get("query", "")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        client = APIClient()
        result = client.translate_query(query)
        client.close()
        
        return {"translated_query": result.get("translated_query", "")}
    
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"API Error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/events")
async def api_events(request: Request):
    """Get events endpoint."""
    try:
        data = await request.json()
        event_type = data.get("event_type")
        limit = data.get("limit", 50)
        
        client = APIClient()
        
        if event_type == 'failed_login':
            events = client.get_failed_login_events(limit=limit)
        elif event_type == 'network':
            events = client.get_network_events(limit=limit)
        elif event_type == 'authentication':
            events = client.get_authentication_events(limit=limit)
        else:
            events = client.get_platform_events(event_type=event_type, limit=limit)
        
        client.close()
        
        return {"events": events}
    
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"API Error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

#!/usr/bin/env python3
"""
📊 Real-time Streaming Dashboard
===============================
WebSocket-based real-time dashboard that streams:
- Live attack chains and security events
- Real-time threat indicators and alerts  
- Dynamic MITRE ATT&CK heatmaps
- Interactive security metrics and analytics
- Live chat assistant responses
"""

import asyncio
import json
import time
import random
import websockets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import uuid
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our enhanced modules
from nlp.security_entities import SecurityNLPRecognizer
from analytics.attack_chains import SimpleAttackChainGenerator


class DashboardEventType(Enum):
    """Types of real-time dashboard events"""
    SECURITY_ALERT = "security_alert"
    ATTACK_CHAIN = "attack_chain"
    THREAT_INDICATOR = "threat_indicator"
    SYSTEM_METRIC = "system_metric"
    CHAT_RESPONSE = "chat_response"
    MITRE_UPDATE = "mitre_update"
    ANALYTICS_UPDATE = "analytics_update"
    STATUS_UPDATE = "status_update"


@dataclass
class DashboardEvent:
    """Real-time dashboard event"""
    event_id: str
    event_type: DashboardEventType
    timestamp: str
    data: Dict[str, Any]
    severity: str = "medium"
    source: str = "kartavya_siem"


class RealTimeMetricsGenerator:
    """Generates realistic real-time security metrics"""
    
    def __init__(self):
        self.baseline_metrics = {
            "events_per_second": 15.0,
            "alerts_per_minute": 3.0,
            "threat_score": 35,
            "active_sessions": 1247,
            "failed_logins": 12,
            "blocked_ips": 45,
            "malware_detections": 2,
            "data_volume_mb": 2890.5
        }
        self.trends = {}
        self.last_update = time.time()
    
    def generate_metrics_update(self) -> Dict[str, Any]:
        """Generate updated metrics with realistic variations"""
        now = time.time()
        time_delta = now - self.last_update
        self.last_update = now
        
        metrics = {}
        
        for metric, baseline in self.baseline_metrics.items():
            # Add realistic variation (±20%)
            variation = random.uniform(-0.2, 0.2)
            new_value = baseline * (1 + variation)
            
            # Apply time-based trends
            if metric not in self.trends:
                self.trends[metric] = random.uniform(-0.01, 0.01)
            
            # Evolve trends slightly
            self.trends[metric] += random.uniform(-0.005, 0.005)
            self.trends[metric] = max(-0.05, min(0.05, self.trends[metric]))
            
            # Apply trend
            new_value *= (1 + self.trends[metric] * time_delta)
            
            # Keep values positive and realistic
            if metric in ["active_sessions", "failed_logins", "blocked_ips"]:
                new_value = max(0, int(new_value))
            elif metric in ["events_per_second", "alerts_per_minute"]:
                new_value = max(0.1, round(new_value, 1))
            else:
                new_value = max(0, round(new_value, 2))
            
            metrics[metric] = new_value
            self.baseline_metrics[metric] = new_value
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "trends": {k: round(v * 100, 2) for k, v in self.trends.items()}
        }


class ThreatIntelGenerator:
    """Generates realistic threat intelligence updates"""
    
    def __init__(self):
        self.ioc_feeds = {
            "malicious_ips": [
                "45.142.214.222", "194.147.85.16", "91.240.118.172",
                "185.220.101.182", "172.67.181.72", "104.21.84.78"
            ],
            "malicious_domains": [
                "malicious-c2.evil.com", "phishing.suspicious.org",
                "update-service.company-cdn.net", "fake-bank.secure-login.net"
            ],
            "file_hashes": [
                "a1b2c3d4e5f6789012345678901234567890abcdef",
                "9f8e7d6c5b4a321098765432109876543210fedc",
                "1a2b3c4d5e6f789012345678901234567890abcd"
            ]
        }
        
        self.threat_campaigns = [
            {"name": "OpShadowStorm", "actor": "APT29", "active": True},
            {"name": "CyberPhoenix", "actor": "Lazarus Group", "active": True},
            {"name": "DarkVortex", "actor": "FIN7", "active": False},
            {"name": "SilentWave", "actor": "APT28", "active": True}
        ]
    
    def generate_threat_intel_update(self) -> Dict[str, Any]:
        """Generate threat intelligence update"""
        update_types = ["new_ioc", "campaign_update", "attribution_update", "yara_rule"]
        update_type = random.choice(update_types)
        
        if update_type == "new_ioc":
            ioc_type = random.choice(list(self.ioc_feeds.keys()))
            ioc_value = random.choice(self.ioc_feeds[ioc_type])
            
            return {
                "type": "new_ioc",
                "ioc_type": ioc_type,
                "value": ioc_value,
                "confidence": random.randint(70, 95),
                "source": random.choice(["VirusTotal", "AlienVault", "ThreatFox", "MalwareBazaar"]),
                "first_seen": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                "threat_types": random.sample(["malware", "phishing", "c2", "exploit"], random.randint(1, 2))
            }
        
        elif update_type == "campaign_update":
            campaign = random.choice(self.threat_campaigns)
            return {
                "type": "campaign_update",
                "campaign_name": campaign["name"],
                "threat_actor": campaign["actor"],
                "status": "active" if campaign["active"] else "dormant",
                "last_activity": datetime.now().isoformat(),
                "targets": random.sample(["financial", "government", "healthcare", "technology"], random.randint(1, 3)),
                "techniques": random.sample(["T1055", "T1059", "T1003", "T1021", "T1566"], random.randint(2, 4))
            }
        
        return {"type": "unknown", "data": "No threat intelligence available"}


class SecurityEventSimulator:
    """Simulates realistic security events for the dashboard"""
    
    def __init__(self):
        self.nlp_recognizer = SecurityNLPRecognizer()
        self.attack_generator = SimpleAttackChainGenerator()
        self.metrics_generator = RealTimeMetricsGenerator()
        self.threat_intel = ThreatIntelGenerator()
        
        self.event_templates = [
            "Failed login attempt from {ip} for user {user}",
            "Malware {malware} detected on host {host}",
            "Suspicious PowerShell execution: {command}",
            "Lateral movement detected from {source_host} to {dest_host}",
            "Data exfiltration attempt to {domain}",
            "Privilege escalation attempt by user {user}",
            "Suspicious network traffic to {ip}:{port}",
            "File integrity violation on {file_path}",
            "Credential dumping activity on {host}",
            "Phishing email detected from {email}"
        ]
    
    def generate_security_event(self) -> DashboardEvent:
        """Generate a realistic security event"""
        template = random.choice(self.event_templates)
        
        # Generate contextual values
        context = {
            "ip": random.choice(["10.0.1.100", "192.168.1.50", "172.16.0.25", "203.0.113.10"]),
            "user": random.choice(["john.doe", "jane.smith", "admin", "sa", "guest"]),
            "malware": random.choice(["Emotet", "Ryuk", "TrickBot", "Cobalt Strike"]),
            "host": random.choice(["WIN-SERVER01", "DESKTOP-ABC123", "LINUX-WS01"]),
            "command": "powershell.exe -EncodedCommand SGV...",
            "source_host": "WIN-CLIENT01",
            "dest_host": "WIN-SERVER02",
            "domain": random.choice(["evil.com", "malicious-c2.net", "phishing.org"]),
            "port": random.choice([443, 80, 8080, 1337, 4444]),
            "file_path": "C:\\Windows\\System32\\config\\SAM",
            "email": "attacker@evil.com"
        }
        
        event_text = template.format(**context)
        
        # Use NLP to extract entities
        analysis = self.nlp_recognizer.analyze_text(event_text)
        
        severity_map = {
            0: "low",
            1: "low", 
            2: "medium",
            3: "high",
            4: "critical"
        }
        
        threat_score = analysis.get("threat_indicators", {}).get("severity_score", 0)
        severity = severity_map.get(min(4, max(0, threat_score // 20)), "medium")
        
        event_data = {
            "message": event_text,
            "entities": analysis["entities"],
            "threat_indicators": analysis["threat_indicators"],
            "mitre_mapping": analysis["mitre_mapping"],
            "context": context,
            "analysis_time_ms": analysis["processing_time_ms"]
        }
        
        return DashboardEvent(
            event_id=str(uuid.uuid4()),
            event_type=DashboardEventType.SECURITY_ALERT,
            timestamp=datetime.now().isoformat(),
            data=event_data,
            severity=severity,
            source="security_monitor"
        )
    
    async def generate_attack_chain_event(self) -> DashboardEvent:
        """Generate an attack chain event"""
        victim = random.choice(self.attack_generator.victim_profiles)
        
        # Randomly select attack type
        attack_methods = [
            self.attack_generator.generate_apt_spearphishing_attack,
            self.attack_generator.generate_ransomware_attack,
            self.attack_generator.generate_insider_threat_scenario
        ]
        
        attack_method = random.choice(attack_methods)
        attack_scenario = await attack_method(victim)
        
        return DashboardEvent(
            event_id=str(uuid.uuid4()),
            event_type=DashboardEventType.ATTACK_CHAIN,
            timestamp=datetime.now().isoformat(),
            data={
                "scenario_name": attack_scenario.name,
                "description": attack_scenario.description,
                "victim": {
                    "username": attack_scenario.victim.username,
                    "hostname": attack_scenario.victim.hostname,
                    "role": attack_scenario.victim.role
                },
                "mitre_tactics": attack_scenario.mitre_tactics,
                "mitre_techniques": attack_scenario.mitre_techniques,
                "event_count": len(attack_scenario.events),
                "duration_minutes": attack_scenario.duration.total_seconds() / 60,
                "timeline": [
                    {
                        "timestamp": event.get("@timestamp"),
                        "action": event.get("event", {}).get("action", "unknown"),
                        "details": event.get("threat", {})
                    }
                    for event in attack_scenario.events[:5]  # First 5 events
                ]
            },
            severity="high" if "APT" in attack_scenario.name or "Ransomware" in attack_scenario.name else "medium",
            source="attack_detector"
        )


class StreamingDashboard:
    """Main streaming dashboard with WebSocket support"""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.event_simulator = SecurityEventSimulator()
        self.running = False
        self.event_queue = queue.Queue()
        
        # Dashboard state
        self.dashboard_state = {
            "total_alerts": 0,
            "active_incidents": 0,
            "mitre_heatmap": {},
            "top_threats": [],
            "system_health": "operational"
        }
    
    async def register_client(self, websocket, path):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        print(f"📱 New client connected: {websocket.remote_address}")
        
        # Send initial dashboard state
        await self.send_to_client(websocket, {
            "type": "dashboard_state",
            "data": self.dashboard_state,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            # Handle client messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    await self.send_to_client(websocket, {
                        "type": "error",
                        "message": "Invalid JSON format"
                    })
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print(f"📱 Client disconnected: {websocket.remote_address}")
    
    async def handle_client_message(self, websocket, data):
        """Handle messages from WebSocket clients"""
        msg_type = data.get("type")
        
        if msg_type == "request_update":
            # Send current metrics
            metrics = self.event_simulator.metrics_generator.generate_metrics_update()
            await self.send_to_client(websocket, {
                "type": "metrics_update",
                "data": metrics
            })
        
        elif msg_type == "chat_query":
            # Simulate chat response
            query = data.get("message", "")
            analysis = self.event_simulator.nlp_recognizer.analyze_text(query)
            
            response_event = DashboardEvent(
                event_id=str(uuid.uuid4()),
                event_type=DashboardEventType.CHAT_RESPONSE,
                timestamp=datetime.now().isoformat(),
                data={
                    "query": query,
                    "response": f"Analyzed query and found {len(analysis['entities'])} security entities.",
                    "entities": analysis["entities"],
                    "suggestions": [
                        "Show me recent alerts",
                        "Hunt for lateral movement",
                        "Analyze authentication failures"
                    ]
                },
                severity="info"
            )
            
            await self.broadcast_event(response_event)
    
    async def send_to_client(self, websocket, data):
        """Send data to a specific client"""
        try:
            await websocket.send(json.dumps(data))
        except websockets.exceptions.ConnectionClosed:
            self.clients.discard(websocket)
    
    async def broadcast_event(self, event: DashboardEvent):
        """Broadcast event to all connected clients"""
        if not self.clients:
            return
        
        message = {
            "type": "dashboard_event",
            "event": asdict(event)
        }
        
        # Update dashboard state
        self.update_dashboard_state(event)
        
        # Send to all clients
        disconnected = set()
        for client in self.clients:
            try:
                await self.send_to_client(client, message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected
    
    def update_dashboard_state(self, event: DashboardEvent):
        """Update internal dashboard state based on event"""
        if event.event_type == DashboardEventType.SECURITY_ALERT:
            self.dashboard_state["total_alerts"] += 1
            
            if event.severity in ["high", "critical"]:
                self.dashboard_state["active_incidents"] += 1
        
        elif event.event_type == DashboardEventType.ATTACK_CHAIN:
            self.dashboard_state["active_incidents"] += 1
            
            # Update MITRE heatmap
            mitre_techniques = event.data.get("mitre_techniques", [])
            for technique in mitre_techniques:
                self.dashboard_state["mitre_heatmap"][technique] = \
                    self.dashboard_state["mitre_heatmap"].get(technique, 0) + 1
    
    async def event_generator_loop(self):
        """Main event generation loop"""
        while self.running:
            try:
                # Generate different types of events
                event_type = random.choices(
                    ["security_alert", "metrics_update", "threat_intel", "attack_chain"],
                    weights=[0.6, 0.2, 0.15, 0.05]
                )[0]
                
                if event_type == "security_alert":
                    event = self.event_simulator.generate_security_event()
                    await self.broadcast_event(event)
                
                elif event_type == "metrics_update":
                    metrics = self.event_simulator.metrics_generator.generate_metrics_update()
                    event = DashboardEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=DashboardEventType.SYSTEM_METRIC,
                        timestamp=datetime.now().isoformat(),
                        data=metrics,
                        severity="info"
                    )
                    await self.broadcast_event(event)
                
                elif event_type == "threat_intel":
                    intel = self.event_simulator.threat_intel.generate_threat_intel_update()
                    event = DashboardEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=DashboardEventType.THREAT_INDICATOR,
                        timestamp=datetime.now().isoformat(),
                        data=intel,
                        severity="medium"
                    )
                    await self.broadcast_event(event)
                
                elif event_type == "attack_chain":
                    event = await self.event_simulator.generate_attack_chain_event()
                    await self.broadcast_event(event)
                
                # Wait before next event (1-5 seconds)
                await asyncio.sleep(random.uniform(1.0, 5.0))
                
            except Exception as e:
                print(f"❌ Error in event generator: {e}")
                await asyncio.sleep(1.0)
    
    async def start_server(self):
        """Start the WebSocket server"""
        print(f"🚀 Starting Streaming Dashboard on {self.host}:{self.port}")
        self.running = True
        
        # Start event generator
        event_task = asyncio.create_task(self.event_generator_loop())
        
        # Start WebSocket server
        server = await websockets.serve(
            self.register_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10
        )
        
        print("📊 Streaming Dashboard is running!")
        print(f"🔗 WebSocket URL: ws://{self.host}:{self.port}")
        print("📱 Clients can connect to receive real-time security events")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Streaming Dashboard...")
            self.running = False
            event_task.cancel()
            server.close()
            await server.wait_closed()


def create_test_client():
    """Create a simple test client to demonstrate the dashboard"""
    client_code = '''
<!DOCTYPE html>
<html>
<head>
    <title>Kartavya SIEM - Real-time Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .header { background: #2d3748; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .metric-card { background: #2d3748; padding: 15px; border-radius: 8px; border-left: 4px solid #4299e1; }
        .events { max-height: 400px; overflow-y: auto; background: #2d3748; padding: 15px; border-radius: 8px; }
        .event { margin-bottom: 10px; padding: 10px; border-radius: 4px; border-left: 4px solid #68d391; }
        .event.high { border-left-color: #f56565; }
        .event.critical { border-left-color: #e53e3e; background: #2d1b1b; }
        .timestamp { color: #a0aec0; font-size: 0.8em; }
        .severity { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; }
        .severity.low { background: #68d391; color: black; }
        .severity.medium { background: #ed8936; color: white; }
        .severity.high { background: #f56565; color: white; }
        .severity.critical { background: #e53e3e; color: white; }
        .chat-box { margin-top: 20px; background: #2d3748; padding: 15px; border-radius: 8px; }
        .chat-input { width: 70%; padding: 8px; border: none; border-radius: 4px; }
        .chat-button { padding: 8px 16px; background: #4299e1; color: white; border: none; border-radius: 4px; margin-left: 10px; cursor: pointer; }
        .status { display: inline-block; padding: 4px 12px; border-radius: 16px; }
        .status.operational { background: #68d391; color: black; }
        .entities { margin-top: 5px; }
        .entity { display: inline-block; background: #4a5568; padding: 2px 8px; margin: 2px; border-radius: 12px; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Kartavya SIEM - Real-time Security Dashboard</h1>
        <div>Status: <span class="status operational" id="status">Operational</span></div>
        <div>Connected: <span id="connection-status">Disconnected</span></div>
    </div>
    
    <div class="metrics" id="metrics">
        <div class="metric-card">
            <h3>Events/Second</h3>
            <div id="events_per_second">0</div>
        </div>
        <div class="metric-card">
            <h3>Active Alerts</h3>
            <div id="total_alerts">0</div>
        </div>
        <div class="metric-card">
            <h3>Active Incidents</h3>
            <div id="active_incidents">0</div>
        </div>
        <div class="metric-card">
            <h3>Threat Score</h3>
            <div id="threat_score">0</div>
        </div>
    </div>
    
    <div class="events">
        <h3>🔴 Live Security Events</h3>
        <div id="events-list"></div>
    </div>
    
    <div class="chat-box">
        <h3>💬 Security Assistant</h3>
        <input type="text" id="chat-input" placeholder="Ask about security events..." class="chat-input">
        <button onclick="sendChatQuery()" class="chat-button">Send</button>
        <div id="chat-responses"></div>
    </div>

    <script>
        let socket;
        let eventCount = 0;
        
        function connect() {
            socket = new WebSocket('ws://localhost:8765');
            
            socket.onopen = function() {
                document.getElementById('connection-status').textContent = 'Connected';
                document.getElementById('connection-status').style.color = '#68d391';
            };
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            socket.onclose = function() {
                document.getElementById('connection-status').textContent = 'Disconnected';
                document.getElementById('connection-status').style.color = '#f56565';
                setTimeout(connect, 3000); // Reconnect after 3 seconds
            };
        }
        
        function handleMessage(data) {
            if (data.type === 'dashboard_event') {
                handleDashboardEvent(data.event);
            } else if (data.type === 'dashboard_state') {
                updateDashboardState(data.data);
            }
        }
        
        function handleDashboardEvent(event) {
            if (event.event_type === 'security_alert') {
                addSecurityEvent(event);
            } else if (event.event_type === 'system_metric') {
                updateMetrics(event.data.metrics);
            } else if (event.event_type === 'attack_chain') {
                addAttackChainEvent(event);
            } else if (event.event_type === 'chat_response') {
                addChatResponse(event);
            }
        }
        
        function addSecurityEvent(event) {
            const eventsList = document.getElementById('events-list');
            const eventDiv = document.createElement('div');
            eventDiv.className = `event ${event.severity}`;
            
            const entities = event.data.entities || [];
            const entitiesHtml = entities.slice(0, 3).map(e => 
                `<span class="entity">${e.type}: ${e.value}</span>`
            ).join(' ');
            
            eventDiv.innerHTML = `
                <div class="timestamp">${new Date(event.timestamp).toLocaleTimeString()}</div>
                <div><span class="severity ${event.severity}">${event.severity.toUpperCase()}</span> ${event.data.message}</div>
                <div class="entities">${entitiesHtml}</div>
            `;
            
            eventsList.insertBefore(eventDiv, eventsList.firstChild);
            
            // Keep only last 50 events
            while (eventsList.children.length > 50) {
                eventsList.removeChild(eventsList.lastChild);
            }
        }
        
        function addAttackChainEvent(event) {
            const eventsList = document.getElementById('events-list');
            const eventDiv = document.createElement('div');
            eventDiv.className = `event ${event.severity}`;
            
            eventDiv.innerHTML = `
                <div class="timestamp">${new Date(event.timestamp).toLocaleTimeString()}</div>
                <div><span class="severity ${event.severity}">ATTACK CHAIN</span> ${event.data.scenario_name}</div>
                <div>${event.data.description}</div>
                <div>Target: ${event.data.victim.username} (${event.data.victim.role})</div>
                <div>MITRE Techniques: ${event.data.mitre_techniques.join(', ')}</div>
            `;
            
            eventsList.insertBefore(eventDiv, eventsList.firstChild);
        }
        
        function updateMetrics(metrics) {
            for (const [key, value] of Object.entries(metrics)) {
                const element = document.getElementById(key);
                if (element) {
                    element.textContent = value;
                }
            }
        }
        
        function updateDashboardState(state) {
            document.getElementById('total_alerts').textContent = state.total_alerts;
            document.getElementById('active_incidents').textContent = state.active_incidents;
        }
        
        function sendChatQuery() {
            const input = document.getElementById('chat-input');
            const query = input.value.trim();
            if (query && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({
                    type: 'chat_query',
                    message: query
                }));
                input.value = '';
            }
        }
        
        function addChatResponse(event) {
            const responsesDiv = document.getElementById('chat-responses');
            const responseDiv = document.createElement('div');
            responseDiv.innerHTML = `
                <div class="timestamp">${new Date(event.timestamp).toLocaleTimeString()}</div>
                <div><strong>Q:</strong> ${event.data.query}</div>
                <div><strong>A:</strong> ${event.data.response}</div>
            `;
            responsesDiv.appendChild(responseDiv);
        }
        
        // Handle chat input enter key
        document.getElementById('chat-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendChatQuery();
            }
        });
        
        // Connect when page loads
        connect();
    </script>
</body>
</html>
    '''
    
    with open("streaming_dashboard_client.html", "w", encoding="utf-8") as f:
        f.write(client_code)
    
    print("📄 Test client created: streaming_dashboard_client.html")


async def main():
    """Run the streaming dashboard"""
    print("📊 KARTAVYA SIEM - REAL-TIME STREAMING DASHBOARD")
    print("=" * 60)
    
    # Create test client HTML file
    create_test_client()
    
    # Create and start dashboard
    dashboard = StreamingDashboard()
    
    try:
        await dashboard.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

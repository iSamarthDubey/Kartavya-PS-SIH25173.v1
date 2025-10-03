#!/usr/bin/env python3
"""
🚀 SIEM NLP Assistant - Complete Application Startup Guide
Run this script to test and start the complete SIEM application.
"""

import os
import sys
import subprocess
import time
import requests
import webbrowser
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color=Colors.WHITE):
    print(f"{color}{text}{Colors.END}")

def print_header(title):
    print_colored("=" * 70, Colors.CYAN)
    print_colored(f" {title} ", Colors.BOLD + Colors.WHITE)
    print_colored("=" * 70, Colors.CYAN)

def check_prerequisites():
    """Check if all required software is installed."""
    print_header("🔍 CHECKING PREREQUISITES")
    
    checks = []
    
    # Check Python
    try:
        python_version = sys.version.split()[0]
        print_colored(f"✅ Python {python_version} - Installed", Colors.GREEN)
        checks.append(True)
    except:
        print_colored("❌ Python - Not found", Colors.RED)
        checks.append(False)
    
    # Check Docker
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_colored(f"✅ Docker - {result.stdout.strip()}", Colors.GREEN)
            checks.append(True)
        else:
            print_colored("❌ Docker - Not working", Colors.RED)
            checks.append(False)
    except FileNotFoundError:
        print_colored("❌ Docker - Not installed", Colors.RED)
        checks.append(False)
    
    # Check Docker Compose
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_colored(f"✅ Docker Compose - {result.stdout.strip()}", Colors.GREEN)
            checks.append(True)
        else:
            print_colored("❌ Docker Compose - Not working", Colors.RED)
            checks.append(False)
    except FileNotFoundError:
        print_colored("❌ Docker Compose - Not installed", Colors.RED)
        checks.append(False)
    
    return all(checks)

def check_ports():
    """Check if required ports are available."""
    print_header("🔌 CHECKING PORTS")
    
    required_ports = {
        8000: "Backend API",
        8501: "Streamlit Frontend", 
        9200: "Elasticsearch",
        5601: "Kibana"
    }
    
    available_ports = []
    
    for port, service in required_ports.items():
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print_colored(f"⚠️  Port {port} ({service}) - In use", Colors.YELLOW)
                available_ports.append(False)
            else:
                print_colored(f"✅ Port {port} ({service}) - Available", Colors.GREEN)
                available_ports.append(True)
        except:
            print_colored(f"⚠️  Port {port} ({service}) - Could not check", Colors.YELLOW)
            available_ports.append(True)
    
    return available_ports

def test_nlp_components():
    """Test NLP components."""
    print_header("🧪 TESTING NLP COMPONENTS")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    try:
        # Import and test components
        sys.path.insert(0, str(backend_dir))
        
        # Test Intent Classifier
        try:
            from nlp.intent_classifier import IntentClassifier
            classifier = IntentClassifier()
            intent, confidence = classifier.classify_intent("Show failed login attempts")
            print_colored(f"✅ Intent Classifier: {intent.value} (confidence: {confidence:.2f})", Colors.GREEN)
        except Exception as e:
            print_colored(f"❌ Intent Classifier failed: {e}", Colors.RED)
            return False
        
        # Test Entity Extractor
        try:
            from nlp.entity_extractor import EntityExtractor
            extractor = EntityExtractor()
            entities = extractor.extract_entities("Show logins from user admin on 192.168.1.100")
            print_colored(f"✅ Entity Extractor: Found {len(entities)} entities", Colors.GREEN)
        except Exception as e:
            print_colored(f"❌ Entity Extractor failed: {e}", Colors.RED)
            return False
        
        # Test Query Builder
        try:
            from query_builder import QueryBuilder
            builder = QueryBuilder()
            query = builder.build_query("Show failed logins")
            print_colored(f"✅ Query Builder: Generated {len(str(query))} char query", Colors.GREEN)
        except Exception as e:
            print_colored(f"❌ Query Builder failed: {e}", Colors.RED)
            return False
        
        print_colored("🎉 All NLP components working!", Colors.GREEN)
        return True
        
    except Exception as e:
        print_colored(f"❌ Component testing failed: {e}", Colors.RED)
        return False

def start_infrastructure():
    """Start Docker infrastructure (Elasticsearch + Kibana)."""
    print_header("🐳 STARTING INFRASTRUCTURE")
    
    docker_dir = Path(__file__).parent / "docker"
    
    if not docker_dir.exists():
        print_colored("❌ Docker directory not found", Colors.RED)
        return False
    
    os.chdir(docker_dir)
    
    print_colored("🔄 Starting Elasticsearch and Kibana...", Colors.YELLOW)
    print_colored("⏱️  This may take 2-3 minutes on first run", Colors.YELLOW)
    
    try:
        # Start only infrastructure services
        subprocess.run([
            'docker-compose', 'up', '-d', 
            'elasticsearch', 'kibana'
        ], check=True)
        
        print_colored("✅ Infrastructure started successfully", Colors.GREEN)
        
        # Wait for Elasticsearch to be ready
        print_colored("⏳ Waiting for Elasticsearch to be ready...", Colors.YELLOW)
        for i in range(30):
            try:
                response = requests.get('http://localhost:9200', timeout=2)
                if response.status_code == 200:
                    print_colored("✅ Elasticsearch is ready!", Colors.GREEN)
                    break
            except:
                time.sleep(2)
                print(".", end="", flush=True)
        else:
            print_colored("⚠️  Elasticsearch may still be starting up", Colors.YELLOW)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Failed to start infrastructure: {e}", Colors.RED)
        return False

def start_backend():
    """Start the FastAPI backend."""
    print_header("⚙️ STARTING BACKEND API")
    
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print_colored("🚀 Starting FastAPI backend on http://localhost:8000", Colors.CYAN)
    
    try:
        # Start backend in background
        process = subprocess.Popen([
            sys.executable, '-c',
            'import uvicorn; from main import app; uvicorn.run(app, host="0.0.0.0", port=8000)'
        ])
        
        # Wait for backend to start
        print_colored("⏳ Waiting for backend to start...", Colors.YELLOW)
        for i in range(15):
            try:
                response = requests.get('http://localhost:8000/health', timeout=2)
                if response.status_code == 200:
                    print_colored("✅ Backend API is ready!", Colors.GREEN)
                    print_colored("📚 API Docs: http://localhost:8000/docs", Colors.BLUE)
                    return process
            except:
                time.sleep(1)
                print(".", end="", flush=True)
        
        print_colored("⚠️  Backend may still be starting up", Colors.YELLOW)
        return process
        
    except Exception as e:
        print_colored(f"❌ Failed to start backend: {e}", Colors.RED)
        return None

def start_frontend():
    """Start the Streamlit frontend."""
    print_header("🌐 STARTING FRONTEND")
    
    ui_dir = Path(__file__).parent / "ui_dashboard"
    
    if not ui_dir.exists():
        print_colored("❌ UI directory not found", Colors.RED)
        return None
    
    os.chdir(ui_dir)
    
    print_colored("🎨 Starting Streamlit frontend on http://localhost:8501", Colors.CYAN)
    
    try:
        # Start Streamlit
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
            '--server.port', '8501',
            '--server.headless', 'true'
        ])
        
        # Wait for frontend to start
        print_colored("⏳ Waiting for frontend to start...", Colors.YELLOW)
        time.sleep(3)
        
        try:
            response = requests.get('http://localhost:8501', timeout=5)
            print_colored("✅ Frontend is ready!", Colors.GREEN)
            print_colored("🌐 Open: http://localhost:8501", Colors.BLUE)
        except:
            print_colored("⚠️  Frontend may still be starting up", Colors.YELLOW)
            print_colored("🌐 Try opening: http://localhost:8501", Colors.BLUE)
        
        return process
        
    except Exception as e:
        print_colored(f"❌ Failed to start frontend: {e}", Colors.RED)
        return None

def show_app_status():
    """Show the status of all services."""
    print_header("📊 APPLICATION STATUS")
    
    services = {
        'http://localhost:9200': 'Elasticsearch',
        'http://localhost:5601': 'Kibana', 
        'http://localhost:8000/health': 'Backend API',
        'http://localhost:8501': 'Frontend'
    }
    
    for url, service in services.items():
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print_colored(f"✅ {service}: Running", Colors.GREEN)
            else:
                print_colored(f"⚠️  {service}: Responding with status {response.status_code}", Colors.YELLOW)
        except:
            print_colored(f"❌ {service}: Not responding", Colors.RED)

def show_next_steps():
    """Show what to do next."""
    print_header("🎯 NEXT STEPS")
    
    print_colored("Your SIEM NLP Assistant is ready! Here's what you can do:", Colors.WHITE)
    print()
    print_colored("1. 🌐 Open the Frontend:", Colors.CYAN)
    print_colored("   http://localhost:8501", Colors.BLUE)
    print()
    print_colored("2. 📚 Explore the API:", Colors.CYAN)
    print_colored("   http://localhost:8000/docs", Colors.BLUE)
    print()
    print_colored("3. 📊 View Kibana (when ready):", Colors.CYAN)
    print_colored("   http://localhost:5601", Colors.BLUE)
    print()
    print_colored("4. 🧪 Test NLP Queries:", Colors.CYAN)
    print_colored('   Try: "Show failed login attempts from last hour"', Colors.WHITE)
    print_colored('   Try: "Find security alerts with high severity"', Colors.WHITE)
    print_colored('   Try: "Get network traffic on port 443"', Colors.WHITE)
    print()
    print_colored("5. 🛑 To stop everything:", Colors.CYAN)
    print_colored("   Press Ctrl+C in this terminal", Colors.WHITE)
    print_colored("   Then run: docker-compose down", Colors.WHITE)

def main():
    """Main function to orchestrate the startup."""
    print_colored(f"""
{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════╗
║                    🚀 SIEM NLP ASSISTANT LAUNCHER 🚀                 ║
║                         SIH 2025 - Team Kartavya                     ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.END}
    """)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print_colored("❌ Prerequisites not met. Please install missing software.", Colors.RED)
        return
    
    # Step 2: Check ports
    check_ports()
    
    # Step 3: Test NLP components
    if not test_nlp_components():
        print_colored("❌ NLP components failed. Cannot continue.", Colors.RED)
        return
    
    # Step 4: Ask user what to start
    print_header("🚀 STARTUP OPTIONS")
    print_colored("What would you like to start?", Colors.WHITE)
    print_colored("1. Complete Application (Recommended)", Colors.GREEN)
    print_colored("2. Backend Only", Colors.YELLOW)
    print_colored("3. Frontend Only", Colors.YELLOW)
    print_colored("4. Infrastructure Only", Colors.YELLOW)
    print_colored("5. Exit", Colors.RED)
    
    choice = input(f"\n{Colors.CYAN}Enter your choice (1-5): {Colors.END}").strip()
    
    processes = []
    
    if choice == "1":
        # Start everything
        print_colored("🚀 Starting complete SIEM NLP Assistant...", Colors.GREEN)
        
        # Start infrastructure
        if start_infrastructure():
            time.sleep(5)  # Give ES time to start
        
        # Start backend
        backend_process = start_backend()
        if backend_process:
            processes.append(backend_process)
            time.sleep(3)  # Give backend time to start
        
        # Start frontend
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(frontend_process)
        
        # Show status
        time.sleep(2)
        show_app_status()
        show_next_steps()
        
        # Open browser
        try:
            webbrowser.open('http://localhost:8501')
        except:
            pass
        
    elif choice == "2":
        backend_process = start_backend()
        if backend_process:
            processes.append(backend_process)
        
    elif choice == "3":
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(frontend_process)
            
    elif choice == "4":
        start_infrastructure()
        
    elif choice == "5":
        print_colored("👋 Goodbye!", Colors.GREEN)
        return
    
    else:
        print_colored("❌ Invalid choice", Colors.RED)
        return
    
    # Keep running until Ctrl+C
    if processes:
        try:
            print_colored(f"\n{Colors.GREEN}✅ Application running! Press Ctrl+C to stop...{Colors.END}")
            for process in processes:
                process.wait()
        except KeyboardInterrupt:
            print_colored(f"\n{Colors.YELLOW}🛑 Shutting down...{Colors.END}")
            for process in processes:
                process.terminate()
            print_colored("👋 Goodbye!", Colors.GREEN)

if __name__ == "__main__":
    main()
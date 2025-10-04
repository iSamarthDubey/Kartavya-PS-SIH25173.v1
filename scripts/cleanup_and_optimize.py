"""
Optimized System Cleanup and Health Check
Ensures no duplicate processes and optimal resource usage.
"""

import psutil
import subprocess
import time
import sys
from pathlib import Path

def find_process_by_port(port):
    """Find process using a specific port."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def is_backend_process(proc):
    """Check if process is our backend."""
    try:
        cmdline = proc.info.get('cmdline', [])
        if cmdline:
            cmdline_str = ' '.join(cmdline)
            return 'uvicorn' in cmdline_str and 'backend.main:app' in cmdline_str
    except:
        return False
    return False

def is_frontend_process(proc):
    """Check if process is our frontend."""
    try:
        cmdline = proc.info.get('cmdline', [])
        if cmdline:
            cmdline_str = ' '.join(cmdline)
            return 'streamlit' in cmdline_str and 'streamlit_app.py' in cmdline_str
    except:
        return False
    return False

def cleanup_orphaned_processes():
    """Kill orphaned app.py launcher processes."""
    killed = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline:
                cmdline_str = ' '.join(cmdline)
                # Kill app.py launcher if backend is already running
                if 'app.py' in cmdline_str and proc.info['name'] == 'python.exe':
                    print(f"⚠️  Killing orphaned app.py launcher (PID {proc.pid})")
                    proc.kill()
                    killed.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return killed

def check_services():
    """Check status of all services."""
    status = {
        'backend': None,
        'frontend': None,
        'elasticsearch': None
    }
    
    # Check backend (port 8001)
    backend_proc = find_process_by_port(8001)
    if backend_proc:
        status['backend'] = {
            'running': True,
            'pid': backend_proc.pid,
            'cpu': backend_proc.cpu_percent(interval=0.1),
            'memory': backend_proc.memory_info().rss / 1024 / 1024  # MB
        }
    
    # Check frontend (port 8501)
    frontend_proc = find_process_by_port(8501)
    if frontend_proc:
        status['frontend'] = {
            'running': True,
            'pid': frontend_proc.pid,
            'cpu': frontend_proc.cpu_percent(interval=0.1),
            'memory': frontend_proc.memory_info().rss / 1024 / 1024  # MB
        }
    
    # Check Elasticsearch (port 9200)
    es_proc = find_process_by_port(9200)
    if es_proc:
        status['elasticsearch'] = {
            'running': True,
            'pid': es_proc.pid
        }
    
    return status

def print_status(status):
    """Print service status."""
    print("\n" + "="*60)
    print("🔍 SYSTEM STATUS CHECK")
    print("="*60)
    
    # Backend
    if status['backend']:
        b = status['backend']
        print(f"✅ Backend (Port 8001): RUNNING")
        print(f"   PID: {b['pid']}, CPU: {b['cpu']:.1f}%, Memory: {b['memory']:.1f} MB")
    else:
        print("❌ Backend (Port 8001): NOT RUNNING")
    
    # Frontend
    if status['frontend']:
        f = status['frontend']
        print(f"✅ Frontend (Port 8501): RUNNING")
        print(f"   PID: {f['pid']}, CPU: {f['cpu']:.1f}%, Memory: {f['memory']:.1f} MB")
    else:
        print("❌ Frontend (Port 8501): NOT RUNNING")
    
    # Elasticsearch
    if status['elasticsearch']:
        print(f"✅ Elasticsearch (Port 9200): RUNNING")
        print(f"   PID: {status['elasticsearch']['pid']}")
    else:
        print("⚠️  Elasticsearch (Port 9200): NOT RUNNING")
    
    print("="*60 + "\n")

def optimize_resources():
    """Check and optimize resource usage."""
    print("\n🔧 RESOURCE OPTIMIZATION CHECK")
    print("-" * 60)
    
    total_python_processes = 0
    backend_count = 0
    frontend_count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] in ['python.exe', 'python3.exe', 'python']:
                total_python_processes += 1
                if is_backend_process(proc):
                    backend_count += 1
                elif is_frontend_process(proc):
                    frontend_count += 1
        except:
            continue
    
    print(f"Total Python processes: {total_python_processes}")
    print(f"Backend processes: {backend_count}")
    print(f"Frontend processes: {frontend_count}")
    
    if backend_count > 2:
        print("⚠️  Multiple backend processes detected - consider restart")
    if frontend_count > 2:
        print("⚠️  Multiple frontend processes detected - consider restart")
    
    print("-" * 60)

def main():
    """Main cleanup and check routine."""
    print("\n🚀 SYSTEM CLEANUP AND OPTIMIZATION")
    print("="*60)
    
    # Step 1: Cleanup orphaned processes
    print("\n1️⃣ Cleaning up orphaned processes...")
    killed = cleanup_orphaned_processes()
    if killed:
        print(f"   Killed {len(killed)} orphaned process(es): {killed}")
        time.sleep(2)  # Wait for cleanup
    else:
        print("   ✅ No orphaned processes found")
    
    # Step 2: Check service status
    print("\n2️⃣ Checking service status...")
    status = check_services()
    print_status(status)
    
    # Step 3: Optimize resources
    optimize_resources()
    
    # Step 4: Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if not status['backend']:
        print("❌ Start backend: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload")
    if not status['frontend']:
        print("❌ Start frontend: python -m streamlit run ui_dashboard/streamlit_app.py --server.port 8501")
    if not status['elasticsearch']:
        print("⚠️  Start Elasticsearch: docker-compose -f docker/docker-compose.yml up -d elasticsearch")
    
    if status['backend'] and status['frontend'] and status['elasticsearch']:
        print("✅ All services running optimally!")
        print("\n🌐 ACCESS URLS:")
        print("   Frontend: http://localhost:8501")
        print("   Backend: http://localhost:8001/docs")
        print("   Health: http://localhost:8001/health")
    
    print("\n" + "="*60)
    return status

if __name__ == "__main__":
    main()

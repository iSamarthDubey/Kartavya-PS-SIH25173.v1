#!/usr/bin/env python3
"""
SIEM NLP Assistant - Best-in-Class Application Launcher

Features:
- Dependency check for uvicorn and streamlit
- Colored output (if colorama is available)
- Configurable ports via environment variables
- Check if backend (port 8001) and frontend (port 8501) are running
- If running and responding with our app, leave them alone
- If running but not our app, kill the process and start ours
- Start backend with uvicorn --reload and frontend with streamlit (file watcher)
- Log backend/frontend output to files for debugging
- Clean shutdown on Ctrl+C
- Optional browser launch for frontend

Usage:
    python app.py

This script is intentionally self-contained and uses only stdlib commands
for port detection and process termination so it works on Windows and Unix.
"""


import sys
import subprocess
import time
import signal
import atexit
import socket
import urllib.request
import urllib.error
import os
from pathlib import Path
from typing import Optional
import webbrowser
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# --- Configurable Ports ---
BACKEND_PORT = int(os.environ.get("SIEM_BACKEND_PORT", 8001))
FRONTEND_PORT = int(os.environ.get("SIEM_FRONTEND_PORT", 8501))
BACKEND_HEALTH_PATH = "/assistant/ping"  # Assistant liveness endpoint (unauthenticated)
STARTUP_TIMEOUT = 30
BACKEND_RELOAD = os.environ.get("SIEM_BACKEND_RELOAD", "false").lower() in {"1", "true", "yes", "on"}
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

started_processes = []


def set_backend_port(port: int) -> None:
    """Update the global backend port and align dependent environment variables."""
    global BACKEND_PORT
    BACKEND_PORT = port
    os.environ["SIEM_BACKEND_PORT"] = str(port)
    os.environ["ASSISTANT_PORT"] = str(port)
    os.environ["ASSISTANT_API_PORT"] = str(port)


set_backend_port(BACKEND_PORT)



# --- Color Output & Checklist Symbols ---
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    TICK = Fore.GREEN + '\u2714' + Style.RESET_ALL  # ✔
    CROSS = Fore.RED + '\u2718' + Style.RESET_ALL   # ✘
    WAIT = Fore.YELLOW + '...' + Style.RESET_ALL
    def cinfo(msg): print(Fore.CYAN + ' ' + msg.lstrip() + Style.RESET_ALL)
    def cgood(msg): print(Fore.GREEN + ' ' + msg.lstrip() + Style.RESET_ALL)
    def cwarn(msg): print(Fore.YELLOW + ' ' + msg.lstrip() + Style.RESET_ALL)
    def cerr(msg): print(Fore.RED + ' ' + msg.lstrip() + Style.RESET_ALL)
    def checklist(msg, status):
        if status == 'ok':
            print(f" {TICK} {msg.lstrip()}")
        elif status == 'fail':
            print(f" {CROSS} {msg.lstrip()}")
        else:
            print(f" {WAIT} {msg.lstrip()}")
except ImportError:
    TICK = '\u2714'
    CROSS = '\u2718'
    WAIT = '...'
    def cinfo(msg): print(msg)
    def cgood(msg): print(msg)
    def cwarn(msg): print(msg)
    def cerr(msg): print(msg)
    def checklist(msg, status):
        if status == 'ok': print(f"  {TICK} {msg}")
        elif status == 'fail': print(f"  {CROSS} {msg}")
        else: print(f"  {WAIT} {msg}")

# --- Simple Progress Bar ---
import sys as _sys
def progress_bar(label, duration=3):
    steps = 20
    for i in range(steps+1):
        bar = '[' + '='*i + ' '*(steps-i) + ']'
        _sys.stdout.write(f"\r {label.lstrip()} {bar} {int(i/steps*100)}%")
        _sys.stdout.flush()
        time.sleep(duration/steps)
    print("\n")

# --- Simple Progress Bar ---
import sys as _sys
def progress_bar(label, duration=3):
    steps = 20
    for i in range(steps+1):
        bar = '[' + '='*i + ' '*(steps-i) + ']'
        _sys.stdout.write(f"\r  {label} {bar} {int(i/steps*100)}%")
        _sys.stdout.flush()
        time.sleep(duration/steps)
    print()

# --- Dependency Check ---


def check_dependencies():
    checklist("Checking dependencies", None)
    missing = []
    try:
        import uvicorn
    except ImportError:
        missing.append("uvicorn")
    try:
        import streamlit
    except ImportError:
        missing.append("streamlit")
    progress_bar("Dependencies", 1.5)
    if missing:
        checklist("Dependencies missing: " + ", ".join(missing), 'fail')
        cinfo("  Install with: pip install " + " ".join(missing))
        sys.exit(1)
    else:
        checklist("All dependencies installed", 'ok')



def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def get_pids_on_port(port):
    """Return a sorted list of PIDs listening on the specified port."""
    try:
        if sys.platform.startswith("win"):
            cmd = f'netstat -ano | findstr :{port}'
            res = run_cmd(cmd)
            out = res.stdout.strip()
            if not out:
                return []
            pids = set()
            for line in out.splitlines():
                parts = line.split()
                if parts:
                    pid = parts[-1]
                    if pid.isdigit():
                        value = int(pid)
                        if value > 0:
                            pids.add(value)
            return sorted(pids)
        else:
            res = run_cmd(f'lsof -ti:{port}')
            out = res.stdout.strip()
            if not out:
                return []
            return sorted({int(pid) for pid in out.splitlines() if pid.strip().isdigit()})
    except Exception:
        return []


def get_pid_on_port(port):
    """Backward compatible helper returning the first PID on a port or None."""
    pids = get_pids_on_port(port)
    return pids[0] if pids else None


def find_available_port(start_port: int, attempts: int = 20) -> Optional[int]:
    """Return the first available port at or above the starting port."""
    port = start_port
    for _ in range(max(1, attempts)):
        if not get_pids_on_port(port):
            return port
        port += 1
    return None

# --- HTTP GET Helper ---
def http_get(url, timeout=3):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read().decode(errors='ignore')
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return "ALIVE"
    except (ConnectionRefusedError, urllib.error.URLError):
        # Connection refused means server not ready yet
        return None
        return None
    except Exception:
        return None

# --- Kill PID Helper ---
def kill_pid(pid):
    try:
        if sys.platform.startswith("win"):
            run_cmd(f'taskkill /F /PID {pid} >nul 2>&1')
        else:
            run_cmd(f'kill -9 {pid} > /dev/null 2>&1')
        cwarn(f"  [CLEANUP] Killed PID {pid}")
        return True
    except Exception as e:
        cwarn(f"  [WARN] Failed to kill {pid}: {e}")
        return False

# --- Backend Health Check ---
def is_our_backend_running():
    pid = get_pid_on_port(BACKEND_PORT)
    if not pid:
        return False, None
    url = f'http://localhost:{BACKEND_PORT}{BACKEND_HEALTH_PATH}'
    body = http_get(url, timeout=2)
    # Recognize our assistant via ping response or generic OpenAPI strings
    if body and ("SIEM NLP Conversational Assistant" in body or "\"service\": \"SIEM NLP Conversational Assistant\"" in body or "OpenAPI" in body or "swagger" in (body.lower() if isinstance(body, str) else "")):
        return True, pid
    return False, pid

# --- Frontend Health Check ---
def is_frontend_running():
    pid = get_pid_on_port(FRONTEND_PORT)
    if not pid:
        return False, None
    url = f'http://localhost:{FRONTEND_PORT}/'
    body = http_get(url, timeout=2)
    if body and ("Streamlit" in body or "streamlit" in body.lower() or body == "ALIVE"):
        return True, pid
    return False, pid


def start_backend():
    cinfo(f"[BACKEND] Starting uvicorn on port {BACKEND_PORT}")
    cmd = [
        sys.executable, "-m", "uvicorn",
        "assistant.main:app",  # Start the Assistant API as the canonical public service
        "--host", "0.0.0.0",
        "--port", str(BACKEND_PORT),
    ]
    if BACKEND_RELOAD:
        cmd.extend([
            "--reload",
            "--reload-dir", "assistant",
            "--reload-dir", "siem_connector",
            "--reload-dir", "backend",
        ])
    else:
        cinfo("  [BACKEND] Reload disabled (set SIEM_BACKEND_RELOAD=1 to enable hot reload)")
    log_file = LOG_DIR / "backend.log"
    p = subprocess.Popen(cmd, stdout=open(log_file, "w"), stderr=subprocess.STDOUT, start_new_session=True)
    started_processes.append(p)
    start = time.time()
    while time.time() - start < STARTUP_TIMEOUT:
        if get_pid_on_port(BACKEND_PORT):
            body = http_get(f'http://localhost:{BACKEND_PORT}{BACKEND_HEALTH_PATH}', timeout=10)  # Increased from 2 to 10 seconds
            if body:
                cgood("  [BACKEND] Started and responding")
                return p
        time.sleep(0.5)
    cerr("  [BACKEND] Failed to start within timeout. See logs/backend.log for details.")
    return None


def boot_backend(max_attempts: int = 3) -> bool:
    """Attempt to start the backend, falling back to alternate ports if needed."""
    attempts = max(1, max_attempts)
    for attempt in range(attempts):
        progress_bar("Starting backend", 2)
        process = start_backend()
        if process:
            return True

        # Try to clean up any lingering listeners on the current port
        lingering = get_pids_on_port(BACKEND_PORT)
        for pid in lingering:
            kill_pid(pid)

        fallback_port = find_available_port(BACKEND_PORT + 1)
        if not fallback_port or fallback_port == BACKEND_PORT:
            break
        cwarn(
            f"  Backend failed to start on port {BACKEND_PORT}; retrying on port {fallback_port}"
        )
        set_backend_port(fallback_port)

    return False


def start_frontend():
    cinfo(f"[FRONTEND] Starting Streamlit on port {FRONTEND_PORT}")
    frontend_script = Path(__file__).parent / "ui_dashboard" / "streamlit_app.py"
    if not frontend_script.exists():
        cerr(f"  [ERROR] Frontend script not found: {frontend_script}")
        return None
    cmd = [sys.executable, "-m", "streamlit", "run", str(frontend_script), "--server.headless", "true", "--server.port", str(FRONTEND_PORT), "--server.fileWatcherType", "auto"]
    log_file = LOG_DIR / "frontend.log"
    p = subprocess.Popen(cmd, stdout=open(log_file, "w"), stderr=subprocess.STDOUT, start_new_session=True)
    started_processes.append(p)
    start = time.time()
    while time.time() - start < STARTUP_TIMEOUT:
        if get_pid_on_port(FRONTEND_PORT):
            cgood("  [FRONTEND] Started and responding")
            return p
        time.sleep(0.5)
    cerr("  [FRONTEND] Failed to start within timeout. See logs/frontend.log for details.")
    return None


def cleanup_started():
    cinfo("\n[SHUTDOWN] Cleaning up started processes...")
    for p in started_processes:
        try:
            p.terminate()
            p.wait(timeout=3)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    started_processes.clear()





def main():
    cinfo("\n=== Application Launcher Module ===\n")
    print("Step-by-step startup checklist:\n")
    check_dependencies()
    print()

    # Backend check
    checklist("Checking backend status", None)
    our_running, pid = is_our_backend_running()
    time.sleep(0.5)
    if our_running:
        checklist(f"Backend already running (PID {pid})", 'ok')
    else:
        occupied_pids = get_pids_on_port(BACKEND_PORT)
        if occupied_pids:
            checklist(
                f"Port {BACKEND_PORT} occupied by PID(s) {', '.join(str(p) for p in occupied_pids)} (not our backend)",
                'fail'
            )
            all_killed = True
            for other_pid in occupied_pids:
                cwarn(f"  Killing PID {other_pid}...")
                killed = kill_pid(other_pid)
                all_killed = all_killed and killed
            time.sleep(0.5)
            if not all_killed and get_pids_on_port(BACKEND_PORT):
                checklist("Could not kill all conflicting backend processes", 'fail')
                fallback_port = find_available_port(BACKEND_PORT + 1)
                if fallback_port and fallback_port != BACKEND_PORT:
                    cwarn(f"  Switching backend to available port {fallback_port}")
                    set_backend_port(fallback_port)
                    if not boot_backend():
                        checklist("Backend failed to start", 'fail')
                    else:
                        checklist(f"Backend started on port {BACKEND_PORT}", 'ok')
                else:
                    cerr("  No alternate port available. Please free the port and retry.")
            else:
                checklist("Killed conflicting backend process(es)", 'ok')
                if boot_backend():
                    checklist(f"Backend started on port {BACKEND_PORT}", 'ok')
                else:
                    checklist("Backend failed to start", 'fail')
        else:
            if boot_backend():
                checklist(f"Backend started on port {BACKEND_PORT}", 'ok')
            else:
                checklist("Backend failed to start", 'fail')
    print()

    # Frontend check
    checklist("Checking frontend status", None)
    our_front_running, fpid = is_frontend_running()
    time.sleep(0.5)
    if our_front_running:
        checklist(f"Frontend already running (PID {fpid})", 'ok')
    else:
        if fpid:
            checklist(f"Port {FRONTEND_PORT} occupied by PID {fpid} (not our frontend)", 'fail')
            cwarn(f"  Killing PID {fpid}...")
            killed = kill_pid(fpid)
            time.sleep(0.5)
            if not killed:
                checklist("Could not kill conflicting frontend process", 'fail')
            else:
                checklist("Killed conflicting frontend process", 'ok')
                progress_bar("Starting frontend", 2)
                p2 = start_frontend()
                if not p2:
                    checklist("Frontend failed to start", 'fail')
                else:
                    checklist("Frontend started", 'ok')
        else:
            progress_bar("Starting frontend", 2)
            p2 = start_frontend()
            if not p2:
                checklist("Frontend failed to start", 'fail')
            else:
                checklist("Frontend started", 'ok')


    # Optional: Ask to open browser for frontend
    print()
    checklist("Browser launch option", None)
    if is_frontend_running()[0]:
        try:
            resp = input("\nOpen frontend in browser? [Y/N]: ").strip().lower()
        except Exception:
            resp = "Y"
        if resp in ("", "Y", "Yes"):
            url = f"http://localhost:{FRONTEND_PORT}/"
            cinfo(f"Opening {url} in browser...")
            webbrowser.open(url)
            checklist("Browser opened", 'ok')
        else:
            checklist("Browser launch skipped", 'ok')
    else:
        checklist("Frontend not running, browser not opened", 'fail')

    cinfo("\nAll steps complete. Press Ctrl+C to stop (will cleanup processes started by this script).\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cinfo("\nReceived interrupt - exiting")
    finally:
        cleanup_started()


if __name__ == '__main__':
    atexit.register(cleanup_started)
    main()

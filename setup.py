
import os
import sys
import subprocess
import platform
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
PYTHON = sys.executable

REQUIREMENTS = [
    PROJECT_ROOT / "requirements.txt",
    PROJECT_ROOT / "backend" / "requirements.txt",
]

# --- Utility Functions ---
def run(cmd, shell=False, check=True, **kwargs):
    print(f"\n>>> Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(cmd, shell=shell, check=check, **kwargs)
        return result
    except Exception as e:
        print(f"[ERROR] Command failed: {e}")
        sys.exit(1)

def pip_install(args):
    run([PYTHON, "-m", "pip"] + args)

def ensure_pip():
    print("\n[Step] Ensuring pip is up to date...")
    pip_install(["install", "--upgrade", "pip"])

def install_requirements():
    for req in REQUIREMENTS:
        if req.exists():
            print(f"\n[Step] Installing requirements from {req} ...")
            pip_install(["install", "--upgrade", "-r", str(req)])
        else:
            print(f"[Skip] {req} not found.")

def install_core_packages():
    print("\n[Step] Ensuring core packages (streamlit, uvicorn, colorama) are installed...")
    pip_install(["install", "--upgrade", "streamlit", "uvicorn", "colorama"])


def check_python_version():
    print("\n[Step] Checking Python version...")
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8+ is required.")
        sys.exit(1)
    print(f"[OK] Python version: {sys.version}")

def check_and_install_docker():
    print("\n[Step] Checking for Docker...")
    try:
        run(["docker", "--version"], check=True)
        print("[OK] Docker is installed.")
    except Exception:
        print("[ERROR] Docker is not installed. Please install Docker Desktop (Windows/Mac) or Docker Engine (Linux) from https://www.docker.com/products/docker-desktop and re-run setup.")
        sys.exit(1)

def run_docker_compose():
    docker_compose_file = PROJECT_ROOT / "docker" / "docker-compose.yml"
    if docker_compose_file.exists():
        try:
            resp = input("\nDo you want to start Docker containers (docker-compose up -d)? [Y/N]: ").strip().lower()
        except Exception:
            resp = "y"
        if resp in ("", "y", "yes"):
            run(["docker", "compose", "-f", str(docker_compose_file), "up", "-d"])
        else:
            print("[Skip] Docker Compose step skipped by user.")
    else:
        print("[Skip] No docker-compose.yml found.")



def main():
    print("""
============================================================
  SIEM NLP Assistant - Automated Setup for Absolute Beginners
============================================================
This script will:
  - Check your Python version
  - Ensure pip is up to date
  - Install all required Python packages
    - Optionally check for Docker and run containers
    - Prompt to launch the app when done

If you get stuck, see the README or ask for help!
------------------------------------------------------------
""")

    check_python_version()
    ensure_pip()
    install_requirements()
    install_core_packages()

    # Docker
    try:
        docker_resp = input("\nDo you want to check for Docker and run containers? [Y/N]: ").strip().lower()
    except Exception:
        docker_resp = "y"
    if docker_resp in ("", "y", "yes"):
        check_and_install_docker()
        run_docker_compose()
    else:
        print("[Skip] Docker setup skipped by user.")

    # (Node.js/npm and platform-specific scripts removed)

    print("""
------------------------------------------------------------
SETUP COMPLETE!

Next steps:
  - If you enabled Docker, make sure Docker Desktop/Engine is running
  - To start the app: python app.py
  - For more info, see the README.md
------------------------------------------------------------
""")
    try:
        launch_resp = input("Do you want to launch the SIEM NLP Assistant now? [Y/N]: ").strip().lower()
    except Exception:
        launch_resp = "y"
    if launch_resp in ("", "y", "yes"):
        print("\nLaunching app.py ...\n")
        run([sys.executable, "app.py"])
    else:
        print("\nYou can start the app anytime with: python app.py\n")

if __name__ == "__main__":
    main()

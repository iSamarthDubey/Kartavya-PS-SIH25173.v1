#!/usr/bin/env python3
"""
SIEM NLP Assistant - Dependency Installation Script
Automated installation for different deployment scenarios
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"⚡ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def install_requirements(env_type="development"):
    """Install requirements based on environment type."""
    
    base_dir = Path(__file__).parent
    
    # Requirements files mapping
    req_files = {
        "development": ["requirements.txt", "requirements-dev.txt"],
        "production": ["requirements-prod.txt"],
        "docker": ["requirements-docker.txt"],
        "backend": ["backend/requirements.txt"],
        "minimal": ["requirements-prod.txt"]
    }
    
    if env_type not in req_files:
        print(f"❌ Unknown environment type: {env_type}")
        print(f"Available types: {', '.join(req_files.keys())}")
        return False
    
    print(f"🚀 Installing dependencies for {env_type.upper()} environment")
    print("=" * 60)
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements files
    success = True
    for req_file in req_files[env_type]:
        req_path = base_dir / req_file
        if req_path.exists():
            cmd = f"{sys.executable} -m pip install -r {req_path}"
            if not run_command(cmd, f"Installing {req_file}"):
                success = False
        else:
            print(f"⚠️  Requirements file not found: {req_path}")
    
    # Install spaCy model if needed
    if env_type in ["development", "production", "backend"]:
        if not run_command(f"{sys.executable} -m spacy download en_core_web_sm", 
                         "Installing spaCy English model"):
            print("⚠️  spaCy model installation failed (you may need to install manually)")
    
    # Download NLTK data if needed
    if env_type in ["development", "production"]:
        nltk_cmd = f"{sys.executable} -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords')\""
        if not run_command(nltk_cmd, "Downloading NLTK data"):
            print("⚠️  NLTK data download failed (you may need to download manually)")
    
    return success


def verify_installation():
    """Verify that key packages are installed correctly."""
    print("\n🔍 Verifying installation...")
    print("=" * 40)
    
    test_imports = [
        ("streamlit", "Streamlit web framework"),
        ("fastapi", "FastAPI REST framework"),
        ("torch", "PyTorch ML framework"),
        ("transformers", "Hugging Face transformers"),
        ("sklearn", "Scikit-learn ML library"),
        ("spacy", "spaCy NLP library"),
        ("elasticsearch", "Elasticsearch client"),
        ("pandas", "Pandas data processing"),
        ("numpy", "NumPy numerical computing")
    ]
    
    failed_imports = []
    
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️  Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("\n🎉 All core packages installed successfully!")
        return True


def main():
    """Main installation script."""
    parser = argparse.ArgumentParser(description="Install SIEM NLP Assistant dependencies")
    parser.add_argument("--env", choices=["development", "production", "docker", "backend", "minimal"],
                       default="development", help="Environment type for installation")
    parser.add_argument("--verify", action="store_true", help="Verify installation after installing")
    parser.add_argument("--force", action="store_true", help="Force reinstall all packages")
    
    args = parser.parse_args()
    
    print("🔧 SIEM NLP Assistant - Dependency Installer")
    print("=" * 50)
    
    # Force reinstall if requested
    if args.force:
        print("🔄 Force reinstalling all packages...")
        cmd = f"{sys.executable} -m pip install --force-reinstall --no-deps"
        # This is a placeholder - you might want to implement full force reinstall logic
    
    # Install requirements
    success = install_requirements(args.env)
    
    # Verify installation if requested
    if args.verify and success:
        success = verify_installation()
    
    if success:
        print("\n🎉 Installation completed successfully!")
        print(f"Environment: {args.env.upper()}")
        print("\n📚 Next steps:")
        print("1. Run: streamlit run ui_dashboard/streamlit_app.py")
        print("2. Or: cd backend && python main.py")
        print("3. Or: docker-compose up (for containerized deployment)")
    else:
        print("\n❌ Installation completed with errors!")
        print("Please check the error messages above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Environment Validation Script
Validates that the environment is ready for comprehensive backend testing.
"""

import sys
import os
import importlib
from pathlib import Path
import subprocess
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Python Version Check...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (compatible)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_required_packages():
    """Check if required packages are installed"""
    print("\n📦 Required Packages Check...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "requests",
        "pydantic",
        "elasticsearch",
        "asyncio",
        "logging",
        "pathlib"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_project_structure():
    """Check if project structure is correct"""
    print("\n📁 Project Structure Check...")
    
    required_paths = [
        "src",
        "src/core", 
        "src/api",
        "src/connectors",
        "src/core/platform",
        "src/core/query",
        "src/core/services",
        "src/api/routes",
        "data/datasets"
    ]
    
    base_path = Path(__file__).parent
    all_present = True
    
    for path in required_paths:
        full_path = base_path / path
        if full_path.exists():
            print(f"   ✅ {path}")
        else:
            print(f"   ❌ {path} (missing)")
            all_present = False
    
    return all_present

def check_configuration_files():
    """Check if configuration files exist"""
    print("\n⚙️ Configuration Files Check...")
    
    config_files = [
        ".env.example",
        "src/core/config.py"
    ]
    
    base_path = Path(__file__).parent
    all_present = True
    
    for config_file in config_files:
        full_path = base_path / config_file
        if full_path.exists():
            print(f"   ✅ {config_file}")
        else:
            print(f"   ❌ {config_file} (missing)")
            all_present = False
    
    return all_present

def check_key_modules():
    """Check if key modules can be imported"""
    print("\n🔧 Key Modules Import Check...")
    
    key_modules = [
        "src.core.config",
        "src.core.platform.detector", 
        "src.core.query.universal_builder",
        "src.core.services.platform_aware_api",
        "src.connectors.multi_source_manager",
        "src.api.main"
    ]
    
    all_importable = True
    
    for module in key_modules:
        try:
            importlib.import_module(module)
            print(f"   ✅ {module}")
        except Exception as e:
            print(f"   ❌ {module} (error: {str(e)[:50]}...)")
            all_importable = False
    
    return all_importable

def check_data_availability():
    """Check if test data is available"""
    print("\n📊 Test Data Availability Check...")
    
    data_paths = [
        "data/datasets",
        "data/datasets/Advanced_SIEM_Dataset",
    ]
    
    base_path = Path(__file__).parent
    data_available = True
    
    for data_path in data_paths:
        full_path = base_path / data_path
        if full_path.exists():
            if full_path.is_dir():
                files = list(full_path.glob("*"))
                print(f"   ✅ {data_path} ({len(files)} files)")
            else:
                print(f"   ✅ {data_path}")
        else:
            print(f"   ⚠️ {data_path} (missing - tests may use mock data)")
    
    # Check for specific dataset file
    dataset_file = base_path / "data/datasets/Advanced_SIEM_Dataset/advanced_siem_dataset.jsonl"
    if dataset_file.exists():
        size_mb = dataset_file.stat().st_size / (1024 * 1024)
        print(f"   ✅ SIEM dataset available ({size_mb:.1f} MB)")
    else:
        print(f"   ⚠️ SIEM dataset not found (will affect some tests)")
    
    return data_available

def check_port_availability():
    """Check if required ports are available"""
    print("\n🌐 Port Availability Check...")
    
    import socket
    
    ports_to_check = [8000, 9200, 55000]  # FastAPI, Elasticsearch, Wazuh
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                print(f"   ⚠️ Port {port} is in use (may conflict with tests)")
            else:
                print(f"   ✅ Port {port} is available")
        except Exception as e:
            print(f"   ❓ Port {port} check failed: {e}")
        finally:
            sock.close()
    
    return True

def check_system_resources():
    """Check system resource availability"""
    print("\n💾 System Resources Check...")
    
    try:
        # Check disk space
        import shutil
        total, used, free = shutil.disk_usage(Path(__file__).parent)
        free_gb = free / (1024**3)
        print(f"   ✅ Disk space: {free_gb:.1f} GB free")
        
        # Check if we can create files
        test_file = Path(__file__).parent / "test_write_permission.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print(f"   ✅ Write permissions: OK")
        except Exception as e:
            print(f"   ❌ Write permissions: {e}")
            
    except Exception as e:
        print(f"   ❓ Resource check failed: {e}")
    
    return True

def run_quick_import_test():
    """Run a quick test to ensure core functionality works"""
    print("\n🧪 Quick Functionality Test...")
    
    try:
        # Test configuration loading
        from src.core.config import Settings
        settings = Settings()
        print("   ✅ Configuration loading")
        
        # Test platform detector
        from src.core.platform.detector import RobustPlatformDetector
        detector = RobustPlatformDetector()
        print("   ✅ Platform detector initialization")
        
        # Test universal query builder
        from src.core.query.universal_builder import UniversalQueryBuilder, QueryIntent
        builder = UniversalQueryBuilder(detector)
        print("   ✅ Universal query builder")
        
        # Test multi-source manager
        from src.connectors.multi_source_manager import MultiSourceManager
        manager = MultiSourceManager()
        print("   ✅ Multi-source manager")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        return False

def generate_environment_report():
    """Generate a comprehensive environment report"""
    
    print("\n" + "="*60)
    print("🔍 KARTAVYA BACKEND ENVIRONMENT VALIDATION REPORT")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages), 
        ("Project Structure", check_project_structure),
        ("Configuration Files", check_configuration_files),
        ("Key Modules", check_key_modules),
        ("Test Data", check_data_availability),
        ("Port Availability", check_port_availability),
        ("System Resources", check_system_resources),
        ("Quick Functionality", run_quick_import_test)
    ]
    
    results = {}
    overall_status = True
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
            if not result:
                overall_status = False
        except Exception as e:
            print(f"\n❌ {check_name} check failed: {e}")
            results[check_name] = False
            overall_status = False
    
    print(f"\n📊 VALIDATION SUMMARY:")
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {check_name}")
    
    print(f"\n🎯 OVERALL STATUS:")
    if overall_status:
        print("   ✅ Environment is ready for comprehensive backend testing!")
        print("   🚀 You can now run: python test_complete_backend.py")
    else:
        print("   ❌ Environment has issues that need to be resolved")
        print("   🔧 Fix the failed checks above before running full tests")
    
    # Save validation report
    report = {
        "validation_time": str(Path(__file__).stat().st_mtime),
        "checks": results,
        "overall_status": overall_status,
        "recommendations": []
    }
    
    if not overall_status:
        report["recommendations"] = [
            "Install missing Python packages with pip",
            "Ensure all project files are present",
            "Check configuration files exist",
            "Verify no conflicts on required ports"
        ]
    
    try:
        with open("environment_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed validation report saved to: environment_validation_report.json")
    except Exception as e:
        print(f"\n⚠️ Could not save validation report: {e}")
    
    print("="*60)
    
    return overall_status

def main():
    """Main validation runner"""
    return 0 if generate_environment_report() else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

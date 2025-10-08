"""
🚀 MVP Setup Script - Complete automated setup for demo
Run this to get a working demo in minutes!
"""

import subprocess
import time
import sys
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def print_banner():
    """Print startup banner."""
    banner = """
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        🚀 SIEM NLP ASSISTANT - MVP SETUP 🚀               ║
║                                                            ║
║        Automated setup for working demo                    ║
║        Smart India Hackathon 2025 - SIH25173             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """
    logger.info(banner)


def run_command(cmd, description, shell=True, check=True):
    """Run a command and handle errors."""
    logger.info(f"\n▶ {description}...")
    logger.info(f"  Command: {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            check=check
        )
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    logger.info(f"  {line}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"  ❌ Failed: {e}")
        if e.stdout:
            logger.error(f"  Output: {e.stdout}")
        if e.stderr:
            logger.error(f"  Error: {e.stderr}")
        return False, None
    except Exception as e:
        logger.error(f"  ❌ Exception: {e}")
        return False, None


def check_docker():
    """Check if Docker is installed and running."""
    logger.info("\n" + "="*60)
    logger.info("STEP 1: Checking Docker")
    logger.info("="*60)
    
    # Check if Docker is installed
    success, _ = run_command("docker --version", "Checking Docker installation", check=False)
    if not success:
        logger.error("\n❌ Docker is not installed!")
        logger.info("\nPlease install Docker Desktop:")
        logger.info("  https://www.docker.com/products/docker-desktop")
        return False
    
    # Check if Docker is running
    success, _ = run_command("docker ps", "Checking Docker daemon", check=False)
    if not success:
        logger.error("\n❌ Docker is not running!")
        logger.info("\nPlease start Docker Desktop and try again.")
        return False
    
    logger.info("\n✅ Docker is installed and running!")
    return True


def start_elasticsearch():
    """Start Elasticsearch using docker-compose."""
    logger.info("\n" + "="*60)
    logger.info("STEP 2: Starting Elasticsearch")
    logger.info("="*60)
    
    # Check if docker-compose.yml exists
    compose_file = Path("docker/docker-compose.yml")
    if not compose_file.exists():
        logger.error(f"❌ Docker compose file not found: {compose_file}")
        return False
    
    # Start only Elasticsearch (not Kibana or other services)
    logger.info("\n🐳 Starting Elasticsearch container...")
    logger.info("   This may take 30-60 seconds on first run...")
    
    success, _ = run_command(
        "docker-compose -f docker/docker-compose.yml up -d elasticsearch",
        "Starting Elasticsearch service"
    )
    
    if not success:
        logger.error("\n❌ Failed to start Elasticsearch!")
        return False
    
    # Wait for Elasticsearch to be ready
    logger.info("\n⏳ Waiting for Elasticsearch to be ready...")
    max_attempts = 30
    for i in range(max_attempts):
        time.sleep(2)
        success, output = run_command(
            "curl -s http://localhost:9200/_cluster/health",
            f"Health check attempt {i+1}/{max_attempts}",
            check=False
        )
        if success and output and "docker-cluster" in output:
            logger.info(f"\n✅ Elasticsearch is ready! (took {(i+1)*2} seconds)")
            return True
        
        if (i + 1) % 5 == 0:
            logger.info(f"   Still waiting... ({i+1}/{max_attempts})")
    
    logger.error(f"\n❌ Elasticsearch did not start after {max_attempts*2} seconds")
    logger.info("\nTroubleshooting:")
    logger.info("  1. Check Docker logs: docker-compose -f docker/docker-compose.yml logs elasticsearch")
    logger.info("  2. Ensure port 9200 is not in use: netstat -ano | findstr :9200")
    logger.info("  3. Try restarting: docker-compose -f docker/docker-compose.yml restart elasticsearch")
    return False


def generate_demo_data():
    """Generate synthetic demo data."""
    logger.info("\n" + "="*60)
    logger.info("STEP 3: Generating Demo Data")
    logger.info("="*60)
    
    success, _ = run_command(
        f"{sys.executable} scripts/create_demo_data.py",
        "Generating 875 synthetic security logs"
    )
    
    if not success:
        logger.error("\n❌ Failed to generate demo data!")
        return False
    
    # Verify file was created
    data_file = Path("datasets/synthetic/demo_security_logs.json")
    if data_file.exists():
        size_mb = data_file.stat().st_size / (1024 * 1024)
        logger.info(f"\n✅ Demo data generated: {data_file} ({size_mb:.2f} MB)")
        return True
    else:
        logger.error(f"\n❌ Demo data file not found: {data_file}")
        return False


def ingest_data():
    """Ingest data into Elasticsearch."""
    logger.info("\n" + "="*60)
    logger.info("STEP 4: Ingesting Data to Elasticsearch")
    logger.info("="*60)
    
    success, _ = run_command(
        f"{sys.executable} scripts/quick_ingest.py",
        "Ingesting demo data to Elasticsearch"
    )
    
    if not success:
        logger.error("\n❌ Failed to ingest data!")
        return False
    
    logger.info("\n✅ Data ingestion complete!")
    return True


def verify_setup():
    """Verify the complete setup."""
    logger.info("\n" + "="*60)
    logger.info("STEP 5: Verifying Setup")
    logger.info("="*60)
    
    checks = []
    
    # Check Elasticsearch
    logger.info("\n🔍 Checking Elasticsearch...")
    success, output = run_command(
        "curl -s http://localhost:9200",
        "Testing Elasticsearch connection",
        check=False
    )
    checks.append(("Elasticsearch", success and "docker-cluster" in output if output else False))
    
    # Check index
    logger.info("\n🔍 Checking data index...")
    success, output = run_command(
        "curl -s http://localhost:9200/security-logs-demo/_count",
        "Checking document count",
        check=False
    )
    checks.append(("Data Index", success and '"count"' in output if output else False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("VERIFICATION RESULTS")
    logger.info("="*60)
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {check_name}: {status}")
        if not passed:
            all_passed = False
    
    return all_passed


def show_next_steps():
    """Show next steps to user."""
    logger.info("\n" + "="*60)
    logger.info("✅ MVP SETUP COMPLETE!")
    logger.info("="*60)
    
    logger.info("\n📌 NEXT STEPS:")
    logger.info("\n1️⃣  Start the application:")
    logger.info("     python app.py")
    logger.info("\n2️⃣  Open browser to:")
    logger.info("     Frontend: http://localhost:8501")
    logger.info("     Backend API: http://localhost:8001/docs")
    logger.info("\n3️⃣  Try these demo queries:")
    logger.info('     - "Show failed login attempts"')
    logger.info('     - "Show malware alerts"')
    logger.info('     - "Show critical security events"')
    logger.info('     - "Show network activity"')
    
    logger.info("\n📊 WHAT'S RUNNING:")
    logger.info("     ✅ Elasticsearch: http://localhost:9200")
    logger.info("     ✅ Demo Data: 875 security logs ingested")
    logger.info("     ✅ Index: security-logs-demo")
    
    logger.info("\n🛠️  USEFUL COMMANDS:")
    logger.info("     Check ES status:  curl http://localhost:9200")
    logger.info("     View logs:        docker-compose -f docker/docker-compose.yml logs -f")
    logger.info("     Stop ES:          docker-compose -f docker/docker-compose.yml down")
    logger.info("     Restart ES:       docker-compose -f docker/docker-compose.yml restart")
    
    logger.info("\n" + "="*60)


def main():
    """Main setup flow."""
    print_banner()
    
    logger.info("\n🎯 This script will:")
    logger.info("   1. Check Docker installation")
    logger.info("   2. Start Elasticsearch")
    logger.info("   3. Generate demo data (875 logs)")
    logger.info("   4. Ingest data to Elasticsearch")
    logger.info("   5. Verify everything works")
    logger.info("\n⏱️  Estimated time: 3-5 minutes")
    
    input("\nPress Enter to start...")
    
    # Execute steps
    steps = [
        (check_docker, "Docker check"),
        (start_elasticsearch, "Elasticsearch startup"),
        (generate_demo_data, "Demo data generation"),
        (ingest_data, "Data ingestion"),
        (verify_setup, "Setup verification")
    ]
    
    for step_func, step_name in steps:
        success = step_func()
        if not success:
            logger.error(f"\n❌ Setup failed at: {step_name}")
            logger.info("\nPlease fix the errors above and run this script again.")
            sys.exit(1)
    
    # Show next steps
    show_next_steps()
    
    logger.info("\n🎉 Ready for demo! Run: python app.py")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

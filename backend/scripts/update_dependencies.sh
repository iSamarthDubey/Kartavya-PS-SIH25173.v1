#!/bin/bash
# Update script for Kartavya SIEM Assistant dependencies
# This script helps upgrade all dependencies to their latest versions

echo "🔄 Updating Kartavya SIEM Assistant Dependencies"
echo "================================================"

# Function to update Python packages
update_python_packages() {
    echo "📦 Updating Python packages..."
    
    # Upgrade pip first
    python -m pip install --upgrade pip
    
    # Install/upgrade packages from requirements.txt
    python -m pip install --upgrade -r requirements.txt
    
    # Update spaCy language model
    python -m spacy download en_core_web_sm --upgrade
    
    echo "✅ Python packages updated"
}

# Function to update Docker images
update_docker_images() {
    echo "🐳 Updating Docker images..."
    
    # Pull latest images
    docker-compose -f docker/docker-compose.yml pull
    
    echo "✅ Docker images updated"
}

# Function to check for outdated packages
check_outdated() {
    echo "🔍 Checking for outdated packages..."
    python -m pip list --outdated
}

# Main execution
case "${1:-all}" in
    "python")
        update_python_packages
        ;;
    "docker")
        update_docker_images
        ;;
    "check")
        check_outdated
        ;;
    "all")
        update_python_packages
        update_docker_images
        ;;
    *)
        echo "Usage: $0 [python|docker|check|all]"
        echo "  python - Update only Python packages"
        echo "  docker - Update only Docker images"
        echo "  check  - Check for outdated packages"
        echo "  all    - Update everything (default)"
        exit 1
        ;;
esac

echo "🎉 Update process completed!"
echo "💡 Remember to test your application after updates"
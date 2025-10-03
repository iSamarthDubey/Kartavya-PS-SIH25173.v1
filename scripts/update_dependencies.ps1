# Update script for Kartavya SIEM Assistant dependencies (Windows PowerShell)
# This script helps upgrade all dependencies to their latest versions

param(
    [string]$Action = "all"
)

Write-Host "🔄 Updating Kartavya SIEM Assistant Dependencies" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Function to update Python packages
function Update-PythonPackages {
    Write-Host "📦 Updating Python packages..." -ForegroundColor Yellow
    
    try {
        # Upgrade pip first
        python -m pip install --upgrade pip
        
        # Install/upgrade packages from requirements.txt
        python -m pip install --upgrade -r requirements.txt
        
        # Update spaCy language model
        python -m spacy download en_core_web_sm --upgrade
        
        Write-Host "✅ Python packages updated" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to update Python packages: $($_.Exception.Message)"
    }
}

# Function to update Docker images
function Update-DockerImages {
    Write-Host "🐳 Updating Docker images..." -ForegroundColor Yellow
    
    try {
        # Pull latest images
        docker-compose -f docker/docker-compose.yml pull
        
        Write-Host "✅ Docker images updated" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to update Docker images: $($_.Exception.Message)"
    }
}

# Function to check for outdated packages
function Check-OutdatedPackages {
    Write-Host "🔍 Checking for outdated packages..." -ForegroundColor Yellow
    python -m pip list --outdated
}

# Main execution
switch ($Action.ToLower()) {
    "python" {
        Update-PythonPackages
    }
    "docker" {
        Update-DockerImages
    }
    "check" {
        Check-OutdatedPackages
    }
    "all" {
        Update-PythonPackages
        Update-DockerImages
    }
    default {
        Write-Host "Usage: .\update_dependencies.ps1 [python|docker|check|all]" -ForegroundColor Cyan
        Write-Host "  python - Update only Python packages" -ForegroundColor White
        Write-Host "  docker - Update only Docker images" -ForegroundColor White
        Write-Host "  check  - Check for outdated packages" -ForegroundColor White
        Write-Host "  all    - Update everything (default)" -ForegroundColor White
        exit 1
    }
}

Write-Host "🎉 Update process completed!" -ForegroundColor Green
Write-Host "💡 Remember to test your application after updates" -ForegroundColor Yellow
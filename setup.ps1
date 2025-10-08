# 🚀 SIH 2025 - KARTAVYA SETUP SCRIPT
# Run this to get everything working!

Write-Host "🏗️  Setting up Kartavya SIH 2025 Project..." -ForegroundColor Green

# Check Python
Write-Host "📍 Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Install Python 3.9+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "📍 Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Install Node.js from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "🐍 Setting up Backend..." -ForegroundColor Cyan
Set-Location backend
if (!(Test-Path "venv")) {
    python -m venv venv
}
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Set-Location ..

# Setup Frontend
Write-Host "⚛️  Setting up Frontend..." -ForegroundColor Cyan
Set-Location frontend
npm install
Set-Location ..

# Create environment files
Write-Host "📝 Creating environment files..." -ForegroundColor Cyan

$backendEnv = @'
# Backend Environment
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/kartavya
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
'@
$backendEnv | Out-File -FilePath "backend\.env" -Encoding UTF8

$frontendEnv = @'
# Frontend Environment
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=development
'@
$frontendEnv | Out-File -FilePath "frontend\.env" -Encoding UTF8

Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Quick Start Commands:" -ForegroundColor Yellow
Write-Host "Backend:  cd backend; .\venv\Scripts\Activate.ps1; python app.py" -ForegroundColor White
Write-Host "Frontend: cd frontend; npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Get OpenAI API key from https://openai.com/api" -ForegroundColor White
Write-Host "2. Set up PostgreSQL + Redis (or use free cloud tiers)" -ForegroundColor White
Write-Host "3. Update .env files with your credentials" -ForegroundColor White

# 🧹 Deep Cleanup Script for Conversational SIEM Assistant
# Run this to remove unnecessary files and reorganize the project

Write-Host "`n🚀 DEEP CLEANUP FOR SIH 2025 PROJECT" -ForegroundColor Cyan
Write-Host "=====================================`n" -ForegroundColor Cyan

# Confirmation
$confirm = Read-Host "This will DELETE unnecessary files and folders. Continue? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Cleanup cancelled." -ForegroundColor Yellow
    exit
}

Write-Host "`n🧹 Starting Deep Cleanup..." -ForegroundColor Green

# Counter for tracking
$deletedCount = 0
$totalSize = 0

# Function to get folder size
function Get-FolderSize {
    param($Path)
    if (Test-Path $Path) {
        $size = (Get-ChildItem -Path $Path -Recurse -Force -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        return [math]::Round($size / 1MB, 2)
    }
    return 0
}

# Remove unnecessary directories
Write-Host "`n📁 Removing unnecessary directories..." -ForegroundColor Yellow

$dirsToDelete = @(
    "web",
    "llm_training", 
    "rag_pipeline",
    "deployment\kubernetes",
    "deployment\terraform",
    "beats-config",
    "scripts",
    ".github"
)

foreach ($dir in $dirsToDelete) {
    if (Test-Path $dir) {
        $size = Get-FolderSize -Path $dir
        $totalSize += $size
        Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  ❌ Deleted: $dir (${size}MB)" -ForegroundColor Red
        $deletedCount++
    }
}

# Remove duplicate/unnecessary files
Write-Host "`n📄 Removing duplicate files..." -ForegroundColor Yellow

$filesToDelete = @(
    "FRONTEND_DEMO_GUIDE.md",
    "FRONTEND_DEVELOPMENT_SUMMARY.md",
    "FRONTEND_README.md",
    "IN-PROGRESS.md",
    "IN_PROGRESS.md",
    "status0.txt",
    "repo-structure.txt",
    "repo-structure-clean.txt",
    "BUILD_VERIFICATION.md",
    "RESTRUCTURING_COMPLETE.md",
    "REPOSITORY_ANALYSIS.md",
    "MVP_IMPLEMENTATION_GUIDE.md",
    "TO-UPDATE.md"
)

foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        $size = [math]::Round((Get-Item $file).Length / 1KB, 2)
        $totalSize += ($size / 1024)
        Remove-Item -Path $file -Force
        Write-Host "  ❌ Deleted: $file (${size}KB)" -ForegroundColor Red
        $deletedCount++
    }
}

# Clean up WARP.md duplicates
Get-ChildItem -Path . -Filter "WARP.md" -Recurse | 
    Where-Object { $_.DirectoryName -ne (Get-Location).Path } | 
    Remove-Item -Force
Write-Host "  ❌ Deleted: WARP.md duplicates" -ForegroundColor Red

# Rename src to backend if exists
Write-Host "`n🔄 Reorganizing structure..." -ForegroundColor Yellow

if (Test-Path "src") {
    if (Test-Path "backend") {
        Write-Host "  ⚠️  Both 'src' and 'backend' exist. Skipping rename." -ForegroundColor Yellow
    } else {
        Rename-Item -Path "src" -NewName "backend"
        Write-Host "  ✅ Renamed: src -> backend" -ForegroundColor Green
    }
}

# Clean up empty directories
Write-Host "`n🗑️  Removing empty directories..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Directory | 
    Where-Object { (Get-ChildItem $_.FullName -Force).Count -eq 0 } | 
    Remove-Item -Force -ErrorAction SilentlyContinue

# Create optimized structure
Write-Host "`n📁 Creating optimized structure..." -ForegroundColor Yellow

$newDirs = @(
    "backend\app\api",
    "backend\app\core\nlp",
    "backend\app\core\query",
    "backend\app\core\context",
    "backend\app\db",
    "backend\app\llm",
    "backend\tests",
    "frontend\app",
    "frontend\components",
    "frontend\lib",
    "docker",
    "data\schemas",
    "docs"
)

foreach ($dir in $newDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ Created: $dir" -ForegroundColor Green
    }
}

# Summary
Write-Host "`n📊 CLEANUP SUMMARY" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host "  📁 Items deleted: $deletedCount" -ForegroundColor White
Write-Host "  💾 Space freed: ${totalSize}MB" -ForegroundColor White
Write-Host "  ✅ Structure optimized" -ForegroundColor Green

# Next steps
Write-Host "`n🎯 NEXT STEPS" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan
Write-Host "  1. Set up MongoDB Atlas (free tier)" -ForegroundColor White
Write-Host "  2. Get Google Gemini API key (free)" -ForegroundColor White
Write-Host "  3. Install Next.js in frontend folder" -ForegroundColor White
Write-Host "  4. Configure backend with MongoDB" -ForegroundColor White
Write-Host "  5. Implement hybrid NLP pipeline" -ForegroundColor White

Write-Host "`n✨ Cleanup Complete! Your project is now optimized for SIH 2025!" -ForegroundColor Green
Write-Host "🚀 Run 'npm install' in frontend and 'pip install -r requirements.txt' in backend to continue.`n" -ForegroundColor Yellow

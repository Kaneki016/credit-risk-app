# PowerShell deployment script for Credit Risk App

param(
    [string]$Environment = "production"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting deployment..." -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Blue

try {
    # Step 1: Pull latest code
    Write-Host "`n📥 Pulling latest code..." -ForegroundColor Blue
    git pull origin main

    # Step 2: Install backend dependencies
    Write-Host "`n📦 Installing backend dependencies..." -ForegroundColor Blue
    pip install -r requirements.txt

    # Step 3: Build frontend
    Write-Host "`n⚛️  Building frontend..." -ForegroundColor Blue
    Push-Location frontend
    npm install
    npm run build
    Pop-Location

    # Step 4: Run tests
    Write-Host "`n🧪 Running tests..." -ForegroundColor Blue
    pytest tests/backend/
    if ($LASTEXITCODE -ne 0) {
        throw "Tests failed!"
    }

    # Step 5: Backup current deployment
    Write-Host "`n💾 Creating backup..." -ForegroundColor Blue
    $BackupDir = "backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    if (Test-Path "models") {
        Copy-Item -Path "models" -Destination $BackupDir -Recurse -ErrorAction SilentlyContinue
    }
    if (Test-Path "logs") {
        Copy-Item -Path "logs" -Destination $BackupDir -Recurse -ErrorAction SilentlyContinue
    }

    # Step 6: Restart services
    Write-Host "`n🔄 Restarting services..." -ForegroundColor Blue
    if ($Environment -eq "docker") {
        docker-compose down
        docker-compose up -d --build
    } else {
        Write-Host "Please restart services manually" -ForegroundColor Yellow
    }

    # Step 7: Health check
    Write-Host "`n🏥 Running health check..." -ForegroundColor Blue
    Start-Sleep -Seconds 5
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        if ($response.status -eq "ok") {
            Write-Host "`n✅ Deployment successful!" -ForegroundColor Green
            Write-Host "API is healthy and running" -ForegroundColor Green
        } else {
            throw "Health check returned unexpected status"
        }
    } catch {
        Write-Host "`n❌ Health check failed!" -ForegroundColor Red
        throw "Deployment verification failed"
    }

    # Step 8: Cleanup
    Write-Host "`n🧹 Cleaning up..." -ForegroundColor Blue
    Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Include *.pyc -Recurse -Force | Remove-Item -Force -ErrorAction SilentlyContinue

    Write-Host "`n✅ Deployment complete!" -ForegroundColor Green
    Write-Host "`n📊 Deployment Summary:" -ForegroundColor Cyan
    Write-Host "  - Environment: $Environment"
    Write-Host "  - Backend: http://localhost:8000"
    Write-Host "  - Frontend: http://localhost:5173"
    Write-Host "  - Health: http://localhost:8000/health"
    Write-Host "  - Docs: http://localhost:8000/docs"

} catch {
    Write-Host "`n❌ Deployment failed: $_" -ForegroundColor Red
    exit 1
}

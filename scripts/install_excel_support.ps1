<#
.SYNOPSIS
    Install Excel support dependencies

.DESCRIPTION
    Installs required packages for Excel file support:
    - Frontend: xlsx package for parsing Excel files
    - Backend: openpyxl package for reading Excel files

.EXAMPLE
    .\scripts\install_excel_support.ps1
#>

Write-Host "Installing Excel Support Dependencies..." -ForegroundColor Green
Write-Host ""

# Check if we're in the project root
if (-not (Test-Path "frontend/package.json")) {
    Write-Host "Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Install frontend dependencies
Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Cyan
Push-Location frontend

try {
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Host "   Running npm install (first time setup)..." -ForegroundColor Yellow
        npm install
    } else {
        Write-Host "   Installing xlsx package..." -ForegroundColor Yellow
        npm install xlsx@^0.18.5
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Frontend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Frontend installation failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

# Install backend dependencies
Write-Host ""
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Cyan

# Check if virtual environment exists
$venvPath = ".venv"
$venvActivate = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $venvActivate)) {
    Write-Host "   ⚠️  Virtual environment not found at $venvPath" -ForegroundColor Yellow
    Write-Host "   Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment and install
try {
    Write-Host "   Activating virtual environment..." -ForegroundColor Yellow
    & $venvActivate
    
    Write-Host "   Installing openpyxl package..." -ForegroundColor Yellow
    pip install openpyxl==3.1.5
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Backend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Backend installation failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
    exit 1
}

# Verify installations
Write-Host ""
Write-Host "🔍 Verifying installations..." -ForegroundColor Cyan

# Check frontend
Push-Location frontend
$xlsxInstalled = npm list xlsx 2>$null
if ($xlsxInstalled -match "xlsx@") {
    Write-Host "   ✅ Frontend: xlsx package installed" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Frontend: xlsx package not found" -ForegroundColor Yellow
}
Pop-Location

# Check backend
$openpyxlCheck = python -c "import openpyxl; print(openpyxl.__version__)" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Backend: openpyxl package installed (version: $openpyxlCheck)" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Backend: openpyxl package not found" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ Excel Support Installation Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Supported file formats:" -ForegroundColor Cyan
Write-Host "  • CSV files (.csv)" -ForegroundColor White
Write-Host "  • Excel files (.xlsx, .xls, .xlsm, .xlsb)" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Start the API: python run.py" -ForegroundColor White
Write-Host "  2. Start the frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host "  3. Upload CSV or Excel files at http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Documentation: docs/EXCEL_SUPPORT_GUIDE.md" -ForegroundColor Yellow
Write-Host ""


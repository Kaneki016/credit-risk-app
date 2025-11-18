<#
.SYNOPSIS
    Install database dependencies for Credit Risk App

.DESCRIPTION
    Installs database dependencies with automatic fallback for Windows issues.
    Tries PostgreSQL first, falls back to SQLite if needed.

.EXAMPLE
    .\scripts\install_database.ps1
#>

Write-Host "Installing Database Dependencies..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not activated" -ForegroundColor Yellow
    Write-Host "   Activating .venv..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

# Try to install psycopg2-binary
Write-Host "1. Attempting to install PostgreSQL driver (psycopg2-binary)..." -ForegroundColor Cyan

try {
    pip install psycopg2-binary==2.9.9 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ PostgreSQL driver installed successfully" -ForegroundColor Green
        $usePostgres = $true
    } else {
        throw "Installation failed"
    }
} catch {
    Write-Host "   ⚠️  PostgreSQL driver installation failed" -ForegroundColor Yellow
    Write-Host "   This is common on Windows without C++ build tools" -ForegroundColor Yellow
    $usePostgres = $false
}

# Install remaining dependencies
Write-Host ""
Write-Host "2. Installing remaining dependencies..." -ForegroundColor Cyan

try {
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Some dependencies failed to install" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Error installing dependencies: $_" -ForegroundColor Red
}

# Configure database
Write-Host ""
Write-Host "3. Configuring database..." -ForegroundColor Cyan

$envFile = ".env"

if ($usePostgres) {
    Write-Host "   ✅ PostgreSQL driver available" -ForegroundColor Green
    Write-Host ""
    Write-Host "   You can use PostgreSQL:" -ForegroundColor Cyan
    Write-Host "   Add to .env file:" -ForegroundColor White
    Write-Host '   DATABASE_URL="postgresql://postgres:password@localhost:5432/credit_risk_db"' -ForegroundColor Gray
} else {
    Write-Host "   ℹ️  Using SQLite (recommended for Windows development)" -ForegroundColor Cyan
    
    # Update .env to use SQLite
    if (Test-Path $envFile) {
        $envContent = Get-Content $envFile -Raw
        
        # Check if DATABASE_URL exists
        if ($envContent -match "DATABASE_URL=") {
            # Update existing
            $envContent = $envContent -replace 'DATABASE_URL=.*', 'DATABASE_URL=sqlite:///./credit_risk.db'
        } else {
            # Add new
            $envContent += "`nDATABASE_URL=sqlite:///./credit_risk.db`n"
        }
        
        Set-Content -Path $envFile -Value $envContent
        Write-Host "   ✅ Updated .env to use SQLite" -ForegroundColor Green
    } else {
        # Create new .env
        "DATABASE_URL=sqlite:///./credit_risk.db" | Out-File -FilePath $envFile -Encoding utf8
        Write-Host "   ✅ Created .env with SQLite configuration" -ForegroundColor Green
    }
}

# Setup database
Write-Host ""
Write-Host "4. Setting up database..." -ForegroundColor Cyan

try {
    python scripts/setup_database.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Database setup complete" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Database setup had issues (may still work)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Database setup error: $_" -ForegroundColor Yellow
    Write-Host "   You can try running: python scripts/setup_database.py" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

if ($usePostgres) {
    Write-Host "Database: PostgreSQL (recommended for production)" -ForegroundColor Cyan
    Write-Host "  • Install PostgreSQL: https://www.postgresql.org/download/" -ForegroundColor White
    Write-Host "  • Configure .env with your PostgreSQL credentials" -ForegroundColor White
} else {
    Write-Host "Database: SQLite (perfect for development)" -ForegroundColor Cyan
    Write-Host "  • No additional setup required" -ForegroundColor White
    Write-Host "  • Database file: ./credit_risk.db" -ForegroundColor White
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Start API: python run.py" -ForegroundColor White
Write-Host "  2. Test database: curl http://localhost:8000/db/health" -ForegroundColor White
Write-Host "  3. View docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

if (-not $usePostgres) {
    Write-Host "Note: For production, consider PostgreSQL" -ForegroundColor Yellow
    Write-Host "See: WINDOWS_POSTGRESQL_FIX.md for PostgreSQL setup" -ForegroundColor Yellow
    Write-Host ""
}


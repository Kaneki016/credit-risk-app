<#
.SYNOPSIS
    Start development services for Credit Risk App

.DESCRIPTION
    PowerShell helper to start the development services in separate terminals.
    - Starts FastAPI backend (uvicorn) in one window
    - Starts React frontend (Vite) in another window
    - Automatically activates virtual environment
    - Designed for local development on Windows

.PARAMETER BackendModule
    The Python module path for the FastAPI app (default: backend.api.main:app)

.PARAMETER BackendPort
    Port for the backend API (default: 8000)

.PARAMETER Reload
    Enable auto-reload for backend (default: true)

.PARAMETER RunInCurrentWindow
    Run services in current window instead of opening new windows

.EXAMPLE
    .\scripts\dev_start.ps1
    Start both backend and frontend in separate windows

.EXAMPLE
    .\scripts\dev_start.ps1 -BackendPort 8080
    Start with backend on port 8080

.EXAMPLE
    .\scripts\dev_start.ps1 -RunInCurrentWindow
    Run in current window (blocks until stopped)

.NOTES
    Prerequisites:
    - Python virtual environment at .venv/
    - Node.js and npm installed
    - Run 'pip install -r requirements.txt' first
    - Run 'npm install' in frontend/ first
#>

param(
    [string]$BackendModule = "backend.api.main:app",
    [int]$BackendPort = 8000,
    [switch]$Reload = $true,
    [switch]$RunInCurrentWindow
)

function Get-FrontendPackageManager {
    $cwd = Join-Path -Path (Get-Location) -ChildPath "frontend"
    if (Test-Path (Join-Path $cwd 'pnpm-lock.yaml')) { return 'pnpm' }
    if (Test-Path (Join-Path $cwd 'yarn.lock')) { return 'yarn' }
    if (Test-Path (Join-Path $cwd 'package-lock.json')) { return 'npm' }
    return 'npm'
}

Write-Host "Starting development services..." -ForegroundColor Green

# Check if virtual environment exists
$venvPath = Join-Path -Path (Get-Location) -ChildPath ".venv"
$venvActivate = Join-Path -Path $venvPath -ChildPath "Scripts\Activate.ps1"

if (-not (Test-Path $venvActivate)) {
    Write-Host "Warning: Virtual environment not found at $venvPath" -ForegroundColor Yellow
    Write-Host "Please create it first: python -m venv .venv" -ForegroundColor Yellow
}

# Check if .env file exists
$envFile = Join-Path -Path (Get-Location) -ChildPath ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "Warning: .env file not found. Gemini features may not work." -ForegroundColor Yellow
    Write-Host "Create .env file with: GEMINI_API_KEY=your-key-here" -ForegroundColor Yellow
}

# Build uvicorn command
$reloadFlag = if ($Reload) { "--reload" } else { "" }
$uvicornCmd = "uvicorn $BackendModule --port $BackendPort $reloadFlag --host 0.0.0.0"

# Start backend (uvicorn via python)
if ($RunInCurrentWindow) {
    Write-Host "Starting backend ($uvicornCmd) in current window..." -ForegroundColor Cyan
    if (Test-Path $venvActivate) {
        & $venvActivate
    }
    Invoke-Expression $uvicornCmd
} else {
    Write-Host "Opening new PowerShell window for backend..." -ForegroundColor Cyan
    $backendScript = @"
Write-Host 'Starting Backend API...' -ForegroundColor Cyan
cd '$(Get-Location)'
if (Test-Path '$venvActivate') {
    & '$venvActivate'
    Write-Host 'Virtual environment activated' -ForegroundColor Green
}
Write-Host 'Running: $uvicornCmd' -ForegroundColor Yellow
$uvicornCmd
"@
    Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-Command', $backendScript) -WorkingDirectory (Get-Location) -WindowStyle Normal
}

# Start React frontend
$frontendDir = Join-Path -Path (Get-Location) -ChildPath 'frontend'
if (Test-Path (Join-Path $frontendDir 'package.json')) {
    $pm = Get-FrontendPackageManager
    switch ($pm) {
        'pnpm' { $startCmd = 'pnpm run dev' }
        'yarn' { $startCmd = 'yarn dev' }
        default { $startCmd = 'npm run dev' }
    }

    # Check if node_modules exists
    $nodeModules = Join-Path -Path $frontendDir -ChildPath 'node_modules'
    if (-not (Test-Path $nodeModules)) {
        Write-Host "Warning: node_modules not found. Run 'npm install' in frontend directory first." -ForegroundColor Yellow
    }

    if ($RunInCurrentWindow) {
        Write-Host "Starting frontend ($startCmd) in current window (path: $frontendDir)" -ForegroundColor Cyan
        Push-Location $frontendDir
        Invoke-Expression $startCmd
        Pop-Location
    } else {
        Write-Host "Opening new PowerShell window for frontend using $pm..." -ForegroundColor Cyan
        $frontendScript = @"
Write-Host 'Starting Frontend Dev Server...' -ForegroundColor Cyan
cd '$frontendDir'
Write-Host 'Running: $startCmd' -ForegroundColor Yellow
$startCmd
"@
        Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-Command', $frontendScript) -WorkingDirectory $frontendDir -WindowStyle Normal
    }
} else {
    Write-Host "Warning: frontend/package.json not found. Skipping frontend startup." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Dev services started!" -ForegroundColor Green
Write-Host "   Backend API: http://localhost:$BackendPort" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:${BackendPort}/docs" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Close the spawned windows to stop the services." -ForegroundColor Yellow

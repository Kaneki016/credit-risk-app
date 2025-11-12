<#
PowerShell helper to start the development services in separate terminals.
- Starts FastAPI (uvicorn) and Streamlit in separate PowerShell windows.
- Designed for local development on Windows.
#>

param(
    [string]$BackendModule = "api:app",
    [int]$BackendPort = 8000,
    [switch]$Reload = $true,
    [string]$StreamlitArgs = "run app.py",
    [switch]$UseReact,
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

# Build uvicorn args using python -m uvicorn for environment consistency
$uvicornArgs = "$BackendModule"
if ($Reload) { $uvicornArgs += " --reload" }
$uvicornArgs += " --port $BackendPort"

# Start backend (uvicorn via python)
if ($RunInCurrentWindow) {
    Write-Host "Starting backend (python -m uvicorn $uvicornArgs) in current window..." -ForegroundColor Cyan
    python -m uvicorn $uvicornArgs
} else {
    Write-Host "Opening new PowerShell window for backend (python -m uvicorn $uvicornArgs)" -ForegroundColor Cyan
    Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-Command',"cd '$(Get-Location)'; python -m uvicorn $uvicornArgs") -WorkingDirectory (Get-Location) -WindowStyle Normal
}

# Prepare frontend start
$frontendDir = Join-Path -Path (Get-Location) -ChildPath 'frontend'
if ($UseReact.IsPresent -or (Test-Path (Join-Path $frontendDir 'package.json'))) {
    $pm = Get-FrontendPackageManager
    switch ($pm) {
        'pnpm' { $startCmd = 'pnpm run dev' }
        'yarn' { $startCmd = 'yarn dev' }
        default { $startCmd = 'npm run dev' }
    }

    if ($RunInCurrentWindow) {
        Write-Host "Starting frontend ($startCmd) in current window (path: $frontendDir)" -ForegroundColor Cyan
        Push-Location $frontendDir
        iex $startCmd
        Pop-Location
    } else {
        Write-Host "Opening new PowerShell window for frontend using $pm..." -ForegroundColor Cyan
        # Use cd then run to ensure correct working directory
        Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-Command',"cd '$frontendDir'; $startCmd") -WorkingDirectory $frontendDir -WindowStyle Normal
    }
} else {
    # Fallback to Streamlit (run via python -m streamlit for environment consistency)
    if ($RunInCurrentWindow) {
        Write-Host "Starting Streamlit in current window: python -m streamlit $StreamlitArgs" -ForegroundColor Cyan
        python -m streamlit $StreamlitArgs
    } else {
        Write-Host "Opening new PowerShell window for Streamlit..." -ForegroundColor Cyan
        Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-Command',"cd '$(Get-Location)'; python -m streamlit $StreamlitArgs") -WorkingDirectory (Get-Location) -WindowStyle Normal
    }
}

Write-Host "Dev services started. Close the spawned windows to stop them." -ForegroundColor Green

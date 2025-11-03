<#
PowerShell helper to start the development services in separate terminals.
- Starts FastAPI (uvicorn) and Streamlit in separate PowerShell windows.
- Designed for local development on Windows.
#>

param(
    [string]$uvicornArgs = "api:app --reload",
    [string]$streamlitArgs = "run app.py",
    [switch]$useReact
)

# Start Uvicorn in a new PowerShell window
Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-Command',"uvicorn $uvicornArgs") -WindowStyle Normal

# Start frontend: prefer React dev server if present and $useReact specified or frontend exists
$frontendPkg = Join-Path -Path (Get-Location) -ChildPath "frontend\package.json"
if ($useReact.IsPresent -or (Test-Path $frontendPkg)) {
    Write-Host "Starting React frontend (vite) in a new PowerShell window..." -ForegroundColor Cyan
    # Use npm --prefix to avoid changing the caller cwd
    Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-Command',"npm --prefix ./frontend run dev") -WindowStyle Normal
} else {
    # Fallback to starting Streamlit for legacy workflows
    Write-Host "Starting Streamlit frontend in a new PowerShell window..." -ForegroundColor Cyan
    Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-Command',"streamlit $streamlitArgs") -WindowStyle Normal
}

Write-Host "Started uvicorn and streamlit in separate PowerShell windows. Close the windows to stop them." -ForegroundColor Green

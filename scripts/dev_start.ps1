<#
PowerShell helper to start the development services in separate terminals.
- Starts FastAPI (uvicorn) and Streamlit in separate PowerShell windows.
- Designed for local development on Windows.
#>

param(
    [string]$uvicornArgs = "api:app --reload",
    [string]$streamlitArgs = "run app.py"
)

# Start Uvicorn in a new PowerShell window
Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-Command',"uvicorn $uvicornArgs") -WindowStyle Normal

# Start Streamlit in a new PowerShell window
Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-Command',"streamlit $streamlitArgs") -WindowStyle Normal

Write-Host "Started uvicorn and streamlit in separate PowerShell windows. Close the windows to stop them." -ForegroundColor Green

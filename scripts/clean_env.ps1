# PowerShell script to clean up Python environment

# List of packages to keep (core dependencies from requirements.txt)
$keep_packages = @(
    "numpy",
    "pandas",
    "scikit-learn",
    "scipy",
    "xgboost",
    "shap",
    "fastapi",
    "uvicorn",
    "starlette",
    "httpx",
    "pydantic",
    "requests",
    "streamlit",
    "streamlit-lottie",
    "python-dotenv",
    "joblib",
    "tqdm",
    "PyYAML",
    "matplotlib",
    "seaborn",
    "pytest"
)

Write-Host "Starting environment cleanup..."

# Get list of installed packages
$installed = pip list --format=json | ConvertFrom-Json
$to_remove = @()

foreach ($pkg in $installed) {
    if ($pkg.name -notin $keep_packages) {
        $to_remove += $pkg.name
    }
}

if ($to_remove.Count -eq 0) {
    Write-Host "No unnecessary packages found to remove."
} else {
    Write-Host "The following packages will be removed:"
    $to_remove | ForEach-Object { Write-Host "  - $_" }
    
    Write-Host "`nUninstalling packages..."
    pip uninstall -y $to_remove

    Write-Host "`nInstalling/Updating required packages from requirements.txt..."
    pip install -r ../requirements.txt
}

Write-Host "`nCleanup completed!"
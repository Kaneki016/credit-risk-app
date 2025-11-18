# Project Cleanup Plan

## Overview
This document outlines the cleanup of unused scripts and files to maintain a tidy project structure.

## Files to Remove

### 1. Obsolete Reorganization Scripts (Root Directory)
These scripts were used for one-time reorganization and are no longer needed:
- ✅ `cleanup_old_files.py` - One-time cleanup script (already executed)
- ✅ `reorganize.py` - One-time reorganization script (already executed)

### 2. Duplicate Model Files (Root Directory)
Model files should only exist in `models/` directory:
- ✅ `credit_risk_model.pkl` - Duplicate (exists in models/)
- ✅ `feature_names.pkl` - Duplicate (exists in models/)
- ✅ `scaler.pkl` - Duplicate (exists in models/)

### 3. Unused/Redundant Scripts
Scripts that are either unused or have better alternatives:
- ⚠️ `scripts/clean_env.ps1` - Rarely used, manual pip management is better
- ⚠️ `scripts/setup-cicd.sh` - Replaced by `.github/workflows/test.yml`

### 4. Database File (Optional)
- ⚠️ `credit_risk.db` - SQLite database (should be in .gitignore, can be regenerated)

## Files to Keep

### Essential Scripts
- ✅ `scripts/dev_start.ps1` - Active development tool
- ✅ `scripts/deploy.ps1` - Deployment automation
- ✅ `scripts/deploy.sh` - Linux deployment
- ✅ `scripts/install_database.ps1` - Database setup
- ✅ `scripts/install_excel_support.ps1` - Excel support setup
- ✅ `scripts/setup_database.py` - Database initialization
- ✅ `scripts/README.md` - Documentation

### Essential Root Files
- ✅ `run.py` - Main entry point for API
- ✅ `.env` - Environment configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `docker-compose.yml` - Docker configuration
- ✅ `Dockerfile` - Docker image definition

## Recommended Actions

### Immediate (Safe to Delete)
1. Remove obsolete reorganization scripts
2. Remove duplicate model files from root
3. Update .gitignore to prevent future duplicates

### Optional (Consider)
1. Remove `scripts/clean_env.ps1` if not used
2. Remove `scripts/setup-cicd.sh` (replaced by GitHub Actions)
3. Ensure `credit_risk.db` is in .gitignore

### Update .gitignore
Add these patterns if not already present:
```
# Model files (should only be in models/)
/*.pkl
/*.db

# Temporary/cache files
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Build artifacts
dist/
build/
*.egg-info/
```

## Project Structure After Cleanup

```
credit-risk-app/
├── backend/              # Backend application
│   ├── api/             # API routes
│   ├── core/            # Core configuration
│   ├── database/        # Database models
│   ├── models/          # ML models
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── frontend/            # React frontend
├── tests/               # Test suite
├── scripts/             # Utility scripts (cleaned)
│   ├── dev_start.ps1
│   ├── deploy.ps1
│   ├── deploy.sh
│   ├── install_database.ps1
│   ├── install_excel_support.ps1
│   ├── setup_database.py
│   └── README.md
├── docs/                # Documentation
├── examples/            # Example scripts
├── models/              # Trained models (only location)
├── data/                # Training data
├── logs/                # Application logs
├── .github/             # GitHub Actions
├── run.py               # Main entry point
├── requirements.txt     # Dependencies
├── pytest.ini           # Test configuration
└── README.md            # Project documentation
```

## Benefits

1. **Cleaner Root Directory** - Only essential files at root level
2. **No Duplicates** - Model files only in `models/` directory
3. **Clear Purpose** - Each remaining file has a clear purpose
4. **Better Organization** - Logical grouping of related files
5. **Easier Navigation** - Less clutter, easier to find files
6. **Reduced Confusion** - No obsolete scripts to confuse developers

## Verification Steps

After cleanup:
1. ✅ Run tests: `pytest`
2. ✅ Start API: `python run.py`
3. ✅ Check model loading works
4. ✅ Verify no import errors
5. ✅ Test development workflow with `scripts/dev_start.ps1`

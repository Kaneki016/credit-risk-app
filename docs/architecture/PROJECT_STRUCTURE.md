# Credit Risk App - Project Structure

## Overview
Clean, organized project structure after comprehensive cleanup.

## Directory Tree

```
credit-risk-app/
│
├── 📁 .github/                    # GitHub Actions & CI/CD
│   └── workflows/
│       ├── ci.yml                 # Continuous integration
│       └── test.yml               # Automated testing
│
├── 📁 backend/                    # Backend Python application
│   ├── api/                       # FastAPI routes
│   │   ├── routes/               # Route modules
│   │   ├── __init__.py
│   │   └── main.py               # FastAPI app instance
│   ├── core/                     # Core configuration
│   │   ├── config.py             # Settings & environment
│   │   ├── logging_setup.py      # Logging configuration
│   │   ├── schemas.py            # Pydantic schemas
│   │   └── __init__.py
│   ├── database/                 # Database layer
│   │   ├── config.py             # DB configuration
│   │   ├── crud.py               # CRUD operations
│   │   ├── models.py             # SQLAlchemy models
│   │   └── __init__.py
│   ├── models/                   # ML models & predictors
│   │   ├── predictor.py          # Main predictor
│   │   ├── dynamic_predictor.py  # Dynamic input handler
│   │   ├── training.py           # Model training
│   │   ├── gemini_base.py        # Gemini AI base
│   │   ├── gemini_predictor.py   # AI predictor
│   │   ├── gemini_feature_engineer.py
│   │   ├── gemini_mitigation_guide.py
│   │   └── __init__.py
│   ├── services/                 # Business logic
│   │   ├── imputation.py         # Data imputation
│   │   ├── retraining.py         # Model retraining
│   │   ├── database_retraining.py
│   │   └── __init__.py
│   ├── utils/                    # Utility functions
│   │   └── __init__.py
│   └── __init__.py
│
├── 📁 frontend/                   # React frontend application
│   ├── dist/                     # Build output (gitignored)
│   ├── docs/                     # Frontend documentation
│   │   ├── CSV_FEATURE_GUIDE.md
│   │   └── UI_GUIDE.md
│   ├── node_modules/             # Dependencies (gitignored)
│   ├── public/                   # Static assets
│   │   └── sample_data.csv
│   ├── src/                      # Source code
│   │   ├── components/           # React components
│   │   ├── styles/               # CSS styles
│   │   ├── utils/                # Utilities
│   │   ├── App.jsx               # Main app component
│   │   ├── main.jsx              # Entry point
│   │   └── styles.css            # Global styles
│   ├── index.html                # HTML template
│   ├── package.json              # Node dependencies
│   ├── package-lock.json         # Lock file
│   ├── vite.config.js            # Vite configuration
│   └── README.md                 # Frontend docs
│
├── 📁 tests/                      # Test suite
│   ├── backend/                  # Backend tests
│   │   ├── test_dynamic_api.py   # API integration tests
│   │   └── __init__.py
│   ├── frontend/                 # Frontend tests (placeholder)
│   │   └── __init__.py
│   ├── test_predictor.py         # Predictor unit tests
│   ├── test_retrain_agent.py     # Model artifact tests
│   ├── README.md                 # Test documentation
│   └── __init__.py
│
├── 📁 scripts/                    # Utility scripts
│   ├── deploy.ps1                # Windows deployment
│   ├── deploy.sh                 # Linux/Mac deployment
│   ├── dev_start.ps1             # Start dev servers
│   ├── install_database.ps1      # Database setup
│   ├── install_excel_support.ps1 # Excel support
│   ├── setup_database.py         # DB initialization
│   └── README.md                 # Scripts documentation
│
├── 📁 docs/                       # Project documentation
│   ├── api/                      # API documentation
│   │   ├── DYNAMIC_INPUT_GUIDE.md
│   │   └── GETTING_STARTED_DYNAMIC.md
│   ├── features/                 # Feature guides
│   │   ├── CSV_FEATURE_SUMMARY.md
│   │   ├── CSV_QUICKSTART.md
│   │   └── DYNAMIC_INPUT_SUMMARY.md
│   ├── guides/                   # How-to guides
│   │   ├── FRONTEND_MIGRATION.md
│   │   └── UI_IMPROVEMENTS.md
│   ├── CLEANUP_SUMMARY.md        # Cleanup documentation
│   ├── PROJECT_CLEANUP_PLAN.md   # Cleanup plan
│   ├── TEST_CLEANUP_SUMMARY.md   # Test cleanup
│   └── [other docs...]
│
├── 📁 examples/                   # Example scripts
│   ├── dynamic_input_examples.py
│   ├── test_database_retraining.py
│   ├── test_feature_engineering.py
│   ├── test_gemini_predictor.py
│   └── test_mitigation_guide.py
│
├── 📁 data/                       # Training data (gitignored)
│   ├── credit_risk_dataset.csv
│   └── training_data_*.csv
│
├── 📁 models/                     # Trained models (gitignored)
│   ├── credit_risk_model.pkl
│   ├── scaler.pkl
│   ├── feature_names.json
│   ├── feature_statistics.json
│   ├── manifest.json
│   └── [versioned models...]
│
├── 📁 model_cards/                # Model documentation (gitignored)
│   ├── model_card_*.md
│   └── model_card_*.html
│
├── 📁 logs/                       # Application logs (gitignored)
│   └── app.log
│
├── 📄 .dockerignore               # Docker ignore patterns
├── 📄 .env                        # Environment variables (gitignored)
├── 📄 .gitignore                  # Git ignore patterns
├── 📄 docker-compose.yml          # Docker composition
├── 📄 Dockerfile                  # Docker image definition
├── 📄 env.example                 # Environment template
├── 📄 LICENSE                     # MIT License
├── 📄 pytest.ini                  # Pytest configuration
├── 📄 README.md                   # Project documentation
├── 📄 requirements.txt            # Python dependencies
├── 📄 run.py                      # Main entry point
└── 📄 PROJECT_STRUCTURE.md        # This file
```

## Key Directories

### Backend (`backend/`)
Python FastAPI application with ML models and business logic.

**Key Files:**
- `api/main.py` - FastAPI application instance
- `models/predictor.py` - Main credit risk predictor
- `database/models.py` - Database schema
- `core/config.py` - Configuration management

### Frontend (`frontend/`)
React application with Vite build system.

**Key Files:**
- `src/App.jsx` - Main application component
- `src/main.jsx` - Application entry point
- `vite.config.js` - Build configuration

### Tests (`tests/`)
Pytest-based test suite with unit and integration tests.

**Key Files:**
- `test_predictor.py` - Predictor unit tests
- `backend/test_dynamic_api.py` - API integration tests
- `pytest.ini` - Test configuration (in root)

### Scripts (`scripts/`)
Utility scripts for development and deployment.

**Key Files:**
- `dev_start.ps1` - Start development servers
- `deploy.ps1` / `deploy.sh` - Deployment automation
- `setup_database.py` - Database initialization

### Documentation (`docs/`)
Comprehensive project documentation.

**Sections:**
- `api/` - API documentation
- `features/` - Feature guides
- `guides/` - How-to guides

## Root Files

### Configuration
- `.env` - Environment variables (create from `env.example`)
- `pytest.ini` - Test configuration
- `docker-compose.yml` - Container orchestration
- `Dockerfile` - Container image

### Documentation
- `README.md` - Main project documentation
- `LICENSE` - MIT License
- `PROJECT_STRUCTURE.md` - This file

### Entry Points
- `run.py` - Start the API server
- `requirements.txt` - Python dependencies

### Ignore Files
- `.gitignore` - Git ignore patterns
- `.dockerignore` - Docker ignore patterns

## File Counts

```
Root Directory:     12 files
Scripts:            7 files
Backend:            ~30 files
Frontend:           ~20 files
Tests:              6 files
Documentation:      ~20 files
Examples:           5 files
```

## Quick Start

### Development
```bash
# Start both servers
.\scripts\dev_start.ps1

# Or manually:
python run.py                    # Backend
cd frontend && npm run dev       # Frontend
```

### Testing
```bash
pytest                           # All tests
pytest -m unit                   # Unit tests only
pytest -m "not requires_api"     # Skip API tests
```

### Deployment
```bash
# Windows
.\scripts\deploy.ps1

# Linux/Mac
./scripts/deploy.sh
```

## Notes

- All model files are in `models/` directory only
- Database file (`credit_risk.db`) is gitignored
- Virtual environment (`.venv/`) is gitignored
- Frontend build output (`frontend/dist/`) is gitignored
- Logs directory is gitignored

## Maintenance

This structure is designed to be:
- **Clean** - No duplicate or obsolete files
- **Organized** - Logical grouping of related files
- **Scalable** - Easy to add new features
- **Maintainable** - Clear separation of concerns
- **Documented** - Comprehensive documentation

Last updated: 2024-11-19

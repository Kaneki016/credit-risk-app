# 🏦 Credit Risk Prediction System

> AI-powered credit risk assessment with explainable predictions, intelligent automation, and comprehensive data management

A modern full-stack application for loan default risk prediction featuring XGBoost machine learning, SHAP explainability, CSV batch processing, dynamic schema management, and AI-generated insights.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [System Overview](#-system-overview)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Development](#-development)
- [Documentation](#-documentation)
- [Support](#-support)

---

## ✨ Features

### 🎯 Core Prediction Engine
- **XGBoost Classifier**: High-performance gradient boosting model for credit default risk.
- **Dynamic Input Handling**: Accepts flexible CSV schemas and partial data with intelligent imputation.
- **Multiple Prediction Modes**: Single-row predictions and batch processing from uploaded CSVs.
- **Risk Classification**: Three-tier risk levels (Low 🟢 / Medium 🟠 / High 🔴) with probabilities and binary decision.
- **Prediction History Storage**: Every prediction (single + batch) is persisted for future retraining.

### 📊 Data Management
- **CSV Upload & Mapping**: Upload loan application CSV files and map columns to the dynamic schema.
- **Dynamic Schema Support**: Backend feature mappers adapt to different column names and structures.
- **Row Navigation**: Step through CSV rows for single predictions or process all rows in one batch.
- **Admin Import**: Import historical / external data into the database to seed and enrich retraining data.
- **Export Batch Results**: Download batch prediction outputs as CSV from the UI.

### 🤖 AI-Powered Features
- **SHAP Explainability**: Per-prediction feature importance for transparent decision support.
- **LLM Explanations (Single Predictions)**: Natural-language explanations and mitigation suggestions for single predictions via OpenRouter.
- **Token-Efficient Batch Mode**: Batch processing skips LLM explanations by default to save API usage (can be enabled via API if needed).
- **Robust AI Client**: Centralized OpenRouter client with retries and guardrails for empty/invalid responses.

### 🔧 Model Management & Retraining
- **Prediction Storage for Learning**: All predictions are stored with features, outputs, and optional outcomes/feedback.
- **Hybrid Retraining Data**: Retraining can combine original dataset (`credit_risk_dataset.csv`) with accumulated prediction data.
- **Retraining Readiness Checks**: API exposes whether enough labeled data/feedback exists before training.
- **Model Metrics & Manifest**: Each retraining run stores metrics and updates a manifest for version tracking.
- **Model Health & Reload**: Endpoints to inspect model state (files, features, load status) and reload models after retraining.

### 🛠️ Admin Panel
- **Import Data Tab**: Upload CSVs, map columns, and import data into the database with clear progress feedback.
- **Train Model Tab**: Manually trigger retraining using current database data (plus original dataset, if enabled).
- **Status Tab**: View API and model health, plus basic system status used by operations.
- **Manage Tab**: Safely clear or reset the database with detailed deletion summaries and schema-reset support.

### 💬 Interactive Chatbot
- **In-App Assistant**: Chatbot embedded in the UI to explain features and guide users.
- **Usage Guidance**: Helps users understand prediction results, fields, and admin workflows.
- **Lightweight by Design**: Focused on guidance rather than heavy database querying to keep behavior predictable.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd credit-risk-app
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .\.venv\Scripts\Activate.ps1
   # Linux/Mac:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment** (Optional - for AI features)
   ```bash
   # Copy example environment file
   cp env.example .env
   
   # Edit .env and add your API key(s)
   # OpenRouter (recommended) - Get key from: https://openrouter.ai/keys
   # Gemini (fallback) - Get key from: https://aistudio.google.com/app/apikey
   # Note: System works without API keys using rule-based fallbacks
   ```

5. **Start the application**
   
   **Option A: Automated (Windows)**
   ```powershell
   .\scripts\dev_start.ps1
   ```
   
   **Option B: Manual (All platforms)**
   ```bash
   # Terminal 1 - Backend
   python run.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

6. **Access the application**
   - **Frontend**: http://localhost:5173
   - **API Docs**: http://localhost:8000/docs
   - **API ReDoc**: http://localhost:8000/redoc

---

## 🎯 System Overview

### What This System Does

The Credit Risk Prediction System is a full-stack solution for assessing loan default risk and continuously improving the model over time. It combines:

1. **Risk Assessment**: An XGBoost model predicts default probability and risk level for each loan application.
2. **Explainability**: SHAP values highlight which features drove the decision for transparent, auditable results.
3. **AI Insights**: An LLM (via OpenRouter) turns numeric outputs into human-readable explanations and risk mitigation advice for single predictions.
4. **Batch Processing**: Efficiently runs predictions on entire CSV files and provides structured, downloadable results.
5. **Data Management & Retraining**: Stores predictions in a database and can retrain using both the **original dataset** and **new, labeled predictions**.
6. **Interactive Interface**: A React frontend with Admin Panel and chatbot makes the system accessible to non-technical users.

### How It Works

1. **Input**: User uploads a CSV or sends JSON with loan application data (complete or partial).
2. **Preprocessing & Imputation**: The backend normalizes column names, validates inputs, and fills missing values using training statistics.
3. **Prediction**: The XGBoost-based predictor calculates a probability of default, risk category, and binary decision.
4. **Explainability**: SHAP values are computed to quantify each feature’s contribution to the prediction.
5. **AI Enhancement (Single Predictions)**: An LLM generates a narrative explanation and suggested mitigation actions.
6. **Storage & Feedback Loop**: Each prediction (features + outputs + optional real outcome) is saved to the database, making it available for future retraining.
7. **Retraining**: When enough feedback is collected, the admin can trigger retraining, which merges original training data with new, real-world data to update the model.

---

## 📖 Usage Guide

### Web Interface

#### Prediction View

1. **Upload CSV File**
   - Use the main upload area (e.g., “📊 Credit Risk CSV Analyzer”) to select a CSV file.
   - The system analyzes column names and displays them in a dynamic form.

2. **Single-Row Predictions**
   - Navigate between rows using Previous/Next controls in the left panel.
   - Adjust field values as needed and submit for a **single prediction**.
   - The right panel shows:
     - Risk level and default probability.
     - Binary prediction (default / no default).
     - SHAP-based feature importance.
     - **AI explanation text** and suggested mitigation steps.

3. **Batch Processing**
   - Choose the batch processing option to run predictions on all rows.
   - The backend skips LLM explanations by default to save tokens, but still computes core risk outputs.
   - The right panel switches to a **Batch Results** view with:
     - Total, success, and error counts.
     - A table of row-by-row risk level, probability, and prediction.
     - A **Download CSV** button for exporting batch results.

#### Admin Panel

1. **Import Data Tab**
   - Upload CSV files containing historical or production-like data.
   - Map CSV columns to database fields via the column mapping UI.
   - Run the import and see how many rows were successfully stored.
   - Imported data populates the database to support later retraining.

2. **Train Model Tab (Manual Retraining)**
   - View current **model state** (whether predictors are loaded, feature counts, manifest info).
   - Trigger retraining using the data currently stored in the database (optionally combined with the original dataset).
   - After retraining, see a summary message and key metrics (e.g., accuracy, F1 score).

3. **Status Tab**
   - Check **API server** and **model service** status.
   - View human-readable status messages and last-checked timestamps.

4. **Manage Tab**
   - Clear predictions, loan applications, and model metrics from the database.
   - Optionally drop and recreate tables for a clean schema reset.
   - See a detailed summary of how many records were deleted per table.

### Chatbot Assistant

Click the **💬** button in the bottom-right corner to open the chatbot:

- **Feature Guidance**: Ask how to use prediction, batch processing, or admin tools.
- **Result Interpretation**: Get explanations of fields, risk levels, and mitigation concepts.
- **Lightweight Help**: Designed as an in-app assistant rather than a full analytics/query engine.

---

## 🔌 API Documentation

### Core Endpoints

#### Prediction Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/predict_risk` | POST | Single prediction (complete data required) |
| `/api/v1/predict_risk_dynamic` | POST | Single prediction (partial data accepted, auto-imputation) |
| `/api/v1/predict_risk_batch` | POST | Batch prediction for multiple applications |

#### Model Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | API health check |
| `/model/health` | GET | Model health check |
| `/model/state` | GET | Detailed model state information |
| `/model/reload` | POST | Reload model from disk |

#### Data Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/db/import_csv` | POST | Import CSV data for retraining |
| `/api/v1/db/schema/{table_name}` | GET | Get database table schema |
| `/api/v1/db/clear` | DELETE | Clear all database data |

#### Model Training & Retraining

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/db/retrain` | POST | Retrain model using stored predictions (and optionally original dataset) |
| `/api/v1/db/retraining/status` | GET | Check whether there is sufficient data/feedback for retraining |

#### Chatbot

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chatbot/query` | POST | Query the AI chatbot |

### Example API Calls

#### Single Prediction (Dynamic Input)
```bash
curl -X POST "http://localhost:8000/api/v1/predict_risk_dynamic" \
  -H "Content-Type: application/json" \
  -d '{
    "person_income": 50000,
    "loan_amnt": 10000,
    "loan_int_rate": 10.5,
    "home_ownership": "RENT"
  }'
```

#### Batch Prediction
```bash
curl -X POST "http://localhost:8000/api/v1/predict_risk_batch?include_explanations=false" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "person_age": 30,
      "person_income": 50000,
      "loan_amnt": 10000
    },
    {
      "person_age": 25,
      "person_income": 35000,
      "loan_amnt": 15000
    }
  ]'
```

For complete API documentation, visit http://localhost:8000/docs when the server is running.

---

## 📁 Project Structure

```
credit-risk-app/
├── 📁 backend/                    # Python FastAPI application
│   ├── api/                       # API routes and endpoints
│   │   ├── routes/                # Route modules
│   │   │   ├── prediction.py      # Prediction endpoints
│   │   │   ├── model.py           # Model management
│   │   │   ├── data_management.py # Data import/export
│   │   │   ├── retraining.py      # Model retraining
│   │   │   └── chatbot.py         # Chatbot API
│   │   └── main.py                # FastAPI app initialization
│   ├── core/                      # Configuration and schemas
│   ├── database/                  # Database models and CRUD
│   ├── models/                    # ML models and predictors
│   ├── services/                  # Business logic
│   └── utils/                     # Utility functions
│
├── 📁 frontend/                   # React application
│   ├── src/
│   │   ├── components/             # React components
│   │   │   ├── csv/               # CSV upload and processing
│   │   │   ├── admin/             # Admin panel
│   │   │   ├── chatbot/           # Chatbot interface
│   │   │   ├── form/              # Form components
│   │   │   └── results/           # Result display
│   │   ├── styles/                # CSS stylesheets
│   │   └── utils/                 # Frontend utilities
│   └── public/                    # Static assets
│
├── 📁 tests/                      # Test suite
│   ├── backend/                   # Backend tests
│   └── test_*.py                  # Unit tests
│
├── 📁 scripts/                    # Utility scripts
│   ├── dev_start.ps1              # Start development servers
│   ├── setup_database.py          # Database initialization
│   ├── testing/                   # Test utilities
│   └── utilities/                 # Helper scripts
│
├── 📁 docs/                       # Documentation
│   ├── api/                       # API documentation
│   ├── features/                  # Feature guides
│   ├── architecture/              # System architecture
│   └── getting-started/           # Getting started guides
│
├── 📁 examples/                   # Example scripts
├── 📁 models/                     # Trained models (gitignored)
├── 📁 data/                       # Training data (gitignored)
│
├── 📄 run.py                      # Main entry point
├── 📄 requirements.txt            # Python dependencies
├── 📄 pytest.ini                  # Test configuration
└── 📄 README.md                   # This file
```

See [docs/architecture/PROJECT_STRUCTURE.md](docs/architecture/PROJECT_STRUCTURE.md) for detailed structure documentation.

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
#Supabase API
DATABASE_URL=

#OPENROUTER_API_KEY
OPENROUTER_API_KEY=
```

### Model Configuration

Edit `backend/core/config.py` to customize:
- Risk thresholds
- Model file paths
- Logging settings
- Feature statistics

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Types
```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"

# Verbose output
pytest -v
```

### Test Coverage
```bash
pytest --cov=backend --cov-report=html
```

See [tests/README.md](tests/README.md) for detailed testing guide.

---

## 🛠️ Development

### Scripts

```bash
# Start development servers (Windows)
.\scripts\dev_start.ps1

# Setup database
python scripts/setup_database.py

# Import data and retrain model
python scripts/import_and_retrain.py

# Install Excel support
.\scripts\install_excel_support.ps1
```

### Code Quality

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

---

## 📚 Documentation

### Getting Started
- [Getting Started Guide](docs/getting-started/GETTING_STARTED.md) - Quick start for new users
- [API Quick Reference](docs/api/API_QUICK_REFERENCE.md) - API endpoints and usage

### Features
- [Admin Panel Guide](docs/features/ADMIN_PANEL_GUIDE.md) - Admin panel usage
- [Chatbot Guide](docs/features/CHATBOT_GUIDE.md) - Chatbot commands and usage
- [New Features Guide](docs/features/NEW_FEATURES_GUIDE.md) - Latest features and updates

### Architecture
- [Project Structure](docs/architecture/PROJECT_STRUCTURE.md) - System design and architecture

### Development
- [Test Documentation](tests/README.md) - Testing guide
- [Scripts Documentation](scripts/README.md) - Utility scripts

---

## 🆘 Support

### Common Issues

**Issue: Virtual environment not activating**
```bash
# Windows
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry activation
.\.venv\Scripts\Activate.ps1
```

**Issue: Port already in use**
```bash
# Windows
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Linux/Mac
lsof -ti:8000 | xargs kill
```

**Issue: Module not found**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or for frontend
cd frontend && npm install
```

**Issue: Model not loading**
```bash
# Check if model files exist
ls models/

# Train a new model via Admin Panel
# Or check logs for specific errors
```

### Getting Help

- 📖 Check [Documentation](docs/)
- 🐛 Report bugs via Issues
- 💬 Ask questions in Discussions
- 📧 Contact maintainers

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Write tests for new features
- Follow PEP 8 style guide
- Update documentation
- Add type hints

---

## 📝 License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.

See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **XGBoost** - Machine learning framework
- **FastAPI** - Modern Python web framework
- **React** - Frontend library
- **SHAP** - Model explainability
- **OpenRouter** - AI API access
- **Framer Motion** - Animation library

---

## 📊 Project Status

- ✅ Core prediction functionality
- ✅ CSV upload and batch processing
- ✅ AI-powered SHAP explanations
- ✅ Dynamic input system with imputation
- ✅ Model retraining with feedback loop
- ✅ Admin panel with data management
- ✅ Chatbot assistant
- ✅ Comprehensive testing
- ✅ Dynamic schema management
- ✅ Flexible model training

---

<div align="center">

**Made with ❤️ for better credit risk assessment**

[⬆ Back to Top](#-credit-risk-prediction-system)

</div>

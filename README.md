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
- **XGBoost Classifier** - High-performance gradient boosting model for accurate risk assessment
- **Dynamic Input Handling** - Accepts partial data with intelligent imputation using historical statistics
- **Multiple Prediction Modes** - Single predictions, batch processing, and CSV upload support
- **Risk Classification** - Three-tier risk levels: Low Risk 🟢, Borderline Risk 🟠, High Risk 🔴

### 📊 Data Management
- **CSV Batch Processing** - Upload and process multiple loan applications simultaneously
- **Dynamic Schema** - Automatically adapts to new CSV column structures
- **Intelligent Field Mapping** - Fuzzy matching and auto-detection of CSV columns to database fields
- **Row Navigation** - Process CSV rows individually or batch process all at once
- **Data Import/Export** - Import historical data for retraining, export predictions

### 🤖 AI-Powered Features
- **SHAP Explainability** - Visual and numerical explanations showing feature importance
- **AI-Generated Insights** - Natural language explanations of predictions (OpenRouter/Gemini)
- **Risk Mitigation Advice** - Actionable recommendations to reduce default risk
- **Chatbot Assistant** - Interactive AI assistant for database queries and system guidance

### 🔧 Model Management
- **Flexible Training** - Train models with any CSV structure, automatic feature detection
- **Model Retraining** - Automated retraining pipeline with feedback loop
- **Model State Monitoring** - Real-time model health and status tracking
- **Model Reloading** - Hot-reload models without restarting the API
- **Training History** - Track model versions, training dates, and performance metrics

### 🛠️ Admin Panel
- **Data Import** - Import CSV files with column mapping and schema management
- **Model Training** - Train new models with custom parameters
- **Database Management** - Clear data, view statistics, manage schema
- **System Status** - Monitor API health, model state, and system metrics
- **Status Dashboard** - Real-time monitoring of predictions, risk distribution, and feedback

### 💬 Interactive Chatbot
- **Database Queries** - Query database statistics and recent predictions
- **Model Information** - Get model performance metrics and training status
- **System Guidance** - Interactive help for using features
- **Quick Actions** - One-click access to common queries

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

The Credit Risk Prediction System is a comprehensive solution for assessing loan default risk. It combines traditional machine learning with modern AI capabilities to provide:

1. **Risk Assessment**: Predicts the probability of loan default using an XGBoost model trained on historical loan data
2. **Explainability**: Uses SHAP values to show which factors contribute most to each prediction
3. **AI Insights**: Generates human-readable explanations and actionable advice
4. **Batch Processing**: Handles multiple loan applications efficiently via CSV upload
5. **Data Management**: Imports historical data, manages database schema, and supports model retraining
6. **Interactive Interface**: User-friendly web interface with admin panel and chatbot assistant

### How It Works

1. **Input**: User provides loan application data (complete or partial)
2. **Imputation**: Missing values are intelligently filled using historical statistics
3. **Prediction**: XGBoost model calculates default probability
4. **Explanation**: SHAP values identify key contributing factors
5. **AI Enhancement**: Optional AI generates natural language explanations
6. **Output**: Risk level, probability, explanations, and mitigation advice

---

## 📖 Usage Guide

### Web Interface

#### Prediction View

1. **Upload CSV File**
   - Click "📊 Credit Risk CSV Analyzer" or drag-and-drop CSV file
   - System automatically detects and maps columns
   - View mapped fields in the form

2. **Process Applications**
   - **Single Row**: Navigate through rows using Previous/Next buttons
   - **Batch Process**: Click "Process All Rows" to predict all applications
   - View predictions with SHAP explanations and AI insights

3. **View Results**
   - Risk level (Low/Borderline/High)
   - Default probability percentage
   - SHAP feature importance visualization
   - AI-generated explanation
   - Risk mitigation suggestions

4. **Download Results**
   - Export predictions as CSV with all details

#### Admin Panel

1. **Import Data Tab**
   - Upload CSV files for historical data import
   - Map CSV columns to database fields
   - Choose to replace or extend schema
   - View import statistics

2. **Train Model Tab**
   - Upload training CSV (any structure)
   - System auto-detects target column and features
   - Train new model with custom parameters
   - View model state and training metrics
   - Reload model to activate changes

3. **Status Tab**
   - View database statistics
   - Check API and model health
   - Monitor system status
   - View recent predictions

### Chatbot Assistant

Click the **💬** button in the bottom-right corner to open the chatbot:

- **Quick Actions**: Database Stats, Recent Predictions, Model Performance, Help
- **Natural Queries**: Ask questions like "show database statistics" or "how many predictions do I have?"
- **System Guidance**: Get help on using features and understanding results

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

#### Model Training

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/db/retrain` | POST | Retrain model from database |
| `/api/v1/db/retraining/status` | GET | Get retraining status |

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
# AI API Keys (Optional - for AI-powered explanations and chatbot)
# OpenRouter (recommended) - Get key from: https://openrouter.ai/keys
OPENROUTER_API_KEY=your-openrouter-key-here
OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free  # Optional, defaults to free model

# Gemini (legacy fallback) - Get key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your-gemini-key-here

# Feature toggles
ENABLE_SHAP_EXPLANATIONS=true  # Enable AI explanations in predictions
ENABLE_CHATBOT=true            # Enable chatbot feature

# Database (Optional - defaults to SQLite)
DATABASE_URL=sqlite:///./credit_risk.db
# Or PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/credit_risk_db

# API Configuration (Optional)
API_HOST=0.0.0.0
API_PORT=8000
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

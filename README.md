# 🏦 Credit Risk Prediction System

> AI-powered credit risk assessment with explainable predictions and intelligent automation

A modern full-stack application for loan default risk prediction featuring traditional ML (XGBoost), SHAP explainability, and CSV batch processing with AI-generated insights.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)

---

## ✨ Features

### 🎯 ML Prediction Model
- **XGBoost Classifier** - Fast, accurate predictions with SHAP explanations
- **AI-Powered Insights** - Natural language explanations and risk mitigation advice
- **Explainable AI** - SHAP values show which features drive each decision

### 📊 Smart Data Handling
- **CSV Upload** - Batch process loan applications from CSV files
- **Dynamic Input** - Accepts partial data with intelligent imputation
- **Auto Field Detection** - Automatically maps CSV columns to model features
- **Row Navigation** - Navigate through CSV rows or batch process all at once

### 🤖 AI-Powered Features
- **SHAP Explanations** - Visual and textual explanations of predictions
- **Risk Mitigation Advice** - AI-generated recommendations to reduce default risk
- **Natural Language Insights** - Human-readable reasoning for predictions

### 🔧 Developer Tools
- **REST API** - Comprehensive FastAPI backend
- **Modern UI** - React frontend with Vite and Framer Motion
- **Model Retraining** - Automated retraining with feedback loop
- **Logging & Monitoring** - Comprehensive logging and model cards

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

4. **Configure environment** (Optional - for AI explanations)
   ```bash
   # Copy example environment file
   cp env.example .env
   
   # Edit .env and add your Gemini API key for AI-powered explanations
   # Get key from: https://aistudio.google.com/app/apikey
   # Note: AI explanations will use fallback logic if no API key is provided
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
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs
   - API ReDoc: http://localhost:8000/redoc

---

## 📖 Usage

### Web Interface

1. **CSV Upload**
   - Upload CSV file with loan applications
   - Navigate through rows one-by-one or batch process all
   - View predictions with SHAP explanations and AI insights
   - Download results as CSV with all predictions

### API Usage

#### Batch Prediction (CSV Data)
```bash
curl -X POST "http://localhost:8000/predict_risk_batch" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "person_age": 30,
      "person_income": 50000,
      "loan_amnt": 10000,
      "loan_int_rate": 10.5
    },
    {
      "person_age": 25,
      "person_income": 35000,
      "loan_amnt": 15000
    }
  ]'
```

#### Single Prediction (Partial Data Accepted)
```bash
curl -X POST "http://localhost:8000/predict_risk_dynamic" \
  -H "Content-Type: application/json" \
  -d '{
    "person_income": 50000,
    "loan_amnt": 10000
  }'
```

See [API Documentation](http://localhost:8000/docs) for complete endpoint reference.

---

## 📁 Project Structure

```
credit-risk-app/
├── 📁 backend/              # Python FastAPI application
│   ├── api/                 # API routes and endpoints
│   ├── core/                # Configuration and schemas
│   ├── database/            # Database models and CRUD
│   ├── models/              # ML models and predictors
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
│
├── 📁 frontend/             # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── styles/          # CSS styles
│   │   └── utils/           # Frontend utilities
│   └── public/              # Static assets
│
├── 📁 tests/                # Test suite
│   ├── backend/             # Backend tests
│   └── test_*.py            # Unit tests
│
├── 📁 scripts/              # Utility scripts
│   ├── dev_start.ps1        # Start development servers
│   ├── deploy.ps1/.sh       # Deployment scripts
│   └── setup_database.py    # Database initialization
│
├── 📁 docs/                 # Documentation
│   ├── api/                 # API documentation
│   ├── features/            # Feature guides
│   └── guides/              # How-to guides
│
├── 📁 examples/             # Example scripts
├── 📁 models/               # Trained models (gitignored)
├── 📁 data/                 # Training data (gitignored)
├── 📁 logs/                 # Application logs (gitignored)
│
├── 📄 run.py                # Main entry point
├── 📄 requirements.txt      # Python dependencies
├── 📄 pytest.ini            # Test configuration
└── 📄 README.md             # This file
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure documentation.

---

## 🔌 API Endpoints

### Prediction Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict_risk_dynamic` | POST | Single prediction (partial data accepted) |
| `/predict_risk_batch` | POST | Batch prediction for CSV uploads |

### Model Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/trigger_retrain` | POST | Trigger model retraining |
| `/reload_model` | POST | Reload model from disk |
| `/health` | GET | Check API and model status |

### Database (Optional)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/db/health` | GET | Check database connection |
| `/db/predictions` | GET | Get prediction history |
| `/db/predictions/{id}/feedback` | POST | Submit feedback |
| `/db/retrain` | POST | Retrain from database |
| `/db/statistics` | GET | Get database statistics |

See [API Documentation](http://localhost:8000/docs) for interactive API explorer.

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

# Exclude API tests (require running server)
pytest -m "not requires_api"

# Verbose output
pytest -v
```

### Test Coverage
```bash
pytest --cov=backend --cov-report=html
```

See [Test Documentation](tests/README.md) for detailed testing guide.

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Gemini AI (Optional - for AI-powered explanations and advice)
# If not provided, system will use rule-based fallback logic
GEMINI_API_KEY=your-api-key-here

# Database (Optional - defaults to SQLite)
DATABASE_URL=sqlite:///./credit_risk.db
# Or PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/credit_risk_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Model Configuration

Edit `backend/core/config.py` to customize:
- Risk thresholds
- Model file paths
- Logging settings
- Webhook URLs

---

## 📚 Documentation

### Getting Started
- [Quick Start Guide](GETTING_STARTED.md)
- [CSV Upload Guide](docs/features/CSV_QUICKSTART.md)
- [Project Structure](PROJECT_STRUCTURE.md)

### Features
- [Dynamic Input System](docs/api/DYNAMIC_INPUT_GUIDE.md)
- [CSV Feature Guide](docs/features/CSV_FEATURE_SUMMARY.md)
- [SHAP Explainability](docs/features/SHAP_GUIDE.md)

### Development
- [Test Documentation](tests/README.md)
- [Scripts Documentation](scripts/README.md)
- [CI/CD Guide](docs/CICD_GUIDE.md)
- [Database Setup](docs/DATABASE_RETRAINING_GUIDE.md)

### Deployment
- [Deployment Scripts](scripts/README.md)
- [PostgreSQL Setup](docs/POSTGRESQL_INTEGRATION_GUIDE.md)

---

## 🐳 Docker Deployment

### Quick Deploy
```bash
python run.py
```

### Build and Run
```bash
# Build image
docker build -t credit-risk-app .

# Run container
docker run -p 8000:8000 -p 5173:5173 credit-risk-app
```

### Environment Variables
```bash
python run.py
```

---

## 🛠️ Development

### Scripts

```bash
# Start development servers (Windows)
.\scripts\dev_start.ps1

# Deploy (Windows)
.\scripts\deploy.ps1

# Deploy (Linux/Mac)
./scripts/deploy.sh

# Setup database
python scripts/setup_database.py

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

### Getting Help

- 📖 Check [Documentation](docs/)
- 🐛 Report bugs via Issues
- 💬 Ask questions in Discussions
- 📧 Contact maintainers

---

## 🙏 Acknowledgments

- **XGBoost** - Machine learning framework
- **FastAPI** - Modern Python web framework
- **React** - Frontend library
- **SHAP** - Model explainability
- **Google Gemini** - AI-powered explanations (optional)

---

## 📊 Project Status

- ✅ Core prediction functionality
- ✅ CSV upload and batch processing
- ✅ AI-powered SHAP explanations
- ✅ Dynamic input system with imputation
- ✅ Model retraining with feedback loop
- ✅ Comprehensive testing
- ✅ Docker deployment
- 🚧 Advanced analytics dashboard (planned)
- 🚧 Real-time monitoring (planned)

---

<div align="center">

**Made with ❤️ for better credit risk assessment**

[⬆ Back to Top](#-credit-risk-prediction-system)

</div>

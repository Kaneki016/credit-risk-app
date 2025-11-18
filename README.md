# 🏦 Credit Risk Prediction System

> AI-powered credit risk assessment with explainable predictions and intelligent automation

A modern full-stack application for loan default risk prediction featuring traditional ML (XGBoost), Gemini AI integration, SHAP explainability, and comprehensive automation tools.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)

---

## ✨ Features

### 🎯 Dual Prediction Models
- **Traditional ML (XGBoost)** - Fast, offline predictions with SHAP explanations
- **Gemini AI** - Natural language explanations and mitigation strategies (no training needed)
- **Model Comparison** - Side-by-side comparison of both approaches

### 📊 Smart Data Handling
- **CSV Upload** - Batch process loan applications from CSV files
- **Dynamic Input** - Accepts partial data with intelligent imputation
- **Auto Field Detection** - Automatically maps CSV columns to model features

### 🤖 AI-Powered Features
- **Feature Engineering** - Automatic feature generation and analysis
- **Risk Mitigation Plans** - Personalized strategies to reduce default risk
- **Natural Explanations** - Human-readable reasoning for predictions

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

4. **Configure environment** (Optional - for Gemini AI features)
   ```bash
   # Copy example environment file
   cp env.example .env
   
   # Edit .env and add your Gemini API key
   # Get key from: https://aistudio.google.com/app/apikey
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

1. **Manual Entry Mode**
   - Fill in loan application details
   - Get instant risk prediction
   - View SHAP explanations

2. **CSV Upload Mode**
   - Upload CSV file with loan applications
   - Navigate through rows or batch process
   - Download results as CSV

### API Usage

#### Standard Prediction
```bash
curl -X POST "http://localhost:8000/predict_risk" \
  -H "Content-Type: application/json" \
  -d '{
    "person_age": 30,
    "person_income": 50000,
    "loan_amnt": 10000,
    "loan_int_rate": 10.5,
    ...
  }'
```

#### Dynamic Prediction (Partial Data)
```bash
curl -X POST "http://localhost:8000/predict_risk_dynamic" \
  -H "Content-Type: application/json" \
  -d '{
    "person_income": 50000,
    "loan_amnt": 10000
  }'
```

#### Gemini AI Prediction
```bash
curl -X POST "http://localhost:8000/predict_risk_gemini" \
  -H "Content-Type: application/json" \
  -d '{
    "person_age": 30,
    "person_income": 50000,
    ...
  }'
```

See [API Documentation](docs/api/DYNAMIC_INPUT_GUIDE.md) for complete endpoint reference.

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
| `/predict_risk` | POST | Standard prediction (all fields required) |
| `/predict_risk_dynamic` | POST | Dynamic prediction (partial data accepted) |
| `/predict_risk_gemini` | POST | AI-powered prediction with explanations |
| `/predict_risk_compare` | POST | Compare ML and Gemini predictions |

### AI Features
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/get_mitigation_plan` | POST | Get risk mitigation strategies |
| `/analyze_features` | POST | AI-powered data analysis |
| `/engineer_features` | POST | Automatic feature generation |

### Model Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/trigger_retrain` | POST | Trigger model retraining |
| `/health` | GET | Check API and model status |

### Database (Optional)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/db/health` | GET | Check database connection |
| `/db/predictions` | GET | Get prediction history |
| `/db/predictions/{id}/feedback` | POST | Submit feedback |
| `/db/retrain` | POST | Retrain from database |

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
# Gemini AI (Optional - for AI features)
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
- [Quick Start Guide](docs/api/GETTING_STARTED_DYNAMIC.md)
- [CSV Upload Guide](docs/features/CSV_QUICKSTART.md)
- [Project Structure](PROJECT_STRUCTURE.md)

### Features
- [Dynamic Input System](docs/api/DYNAMIC_INPUT_GUIDE.md)
- [CSV Feature Guide](docs/features/CSV_FEATURE_SUMMARY.md)
- [Gemini AI Predictor](docs/GEMINI_PREDICTOR_GUIDE.md)
- [Feature Engineering](docs/FEATURE_ENGINEERING_GUIDE.md)

### Development
- [Test Documentation](tests/README.md)
- [Scripts Documentation](scripts/README.md)
- [CI/CD Guide](docs/CICD_GUIDE.md)
- [Database Setup](docs/DATABASE_RETRAINING_GUIDE.md)

### Deployment
- [Docker Deployment](docker-compose.yml)
- [Deployment Scripts](scripts/README.md)
- [PostgreSQL Setup](docs/POSTGRESQL_INTEGRATION_GUIDE.md)

---

## 🐳 Docker Deployment

### Quick Deploy
```bash
docker-compose up -d
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
docker-compose up -d --env-file .env
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
- **Google Gemini** - AI-powered features
- **SHAP** - Model explainability

---

## 📊 Project Status

- ✅ Core prediction functionality
- ✅ CSV upload and batch processing
- ✅ Gemini AI integration
- ✅ Dynamic input system
- ✅ Model retraining
- ✅ Comprehensive testing
- ✅ Docker deployment
- 🚧 Advanced analytics dashboard (planned)
- 🚧 Multi-model ensemble (planned)

---

<div align="center">

**Made with ❤️ for better credit risk assessment**

[⬆ Back to Top](#-credit-risk-prediction-system)

</div>

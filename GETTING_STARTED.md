# 🚀 Getting Started Guide

Welcome to the Credit Risk Prediction System! This guide will help you get up and running in minutes.

---

## 📋 Prerequisites Checklist

Before you begin, make sure you have:

- [ ] **Python 3.10 or higher** installed
  - Check: `python --version`
  - Download: https://www.python.org/downloads/

- [ ] **Node.js 18 or higher** installed
  - Check: `node --version`
  - Download: https://nodejs.org/

- [ ] **Git** installed (optional, for cloning)
  - Check: `git --version`
  - Download: https://git-scm.com/

- [ ] **Terminal/Command Prompt** access
  - Windows: PowerShell (recommended) or CMD
  - Mac/Linux: Terminal

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Get the Code

```bash
# If you have Git
git clone <repository-url>
cd credit-risk-app

# Or download and extract the ZIP file
```

### Step 2: Set Up Python Backend

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Windows CMD:
.\.venv\Scripts\activate.bat

# Mac/Linux:
source .venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

**Troubleshooting:**
- If activation fails on Windows, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- If pip is slow, try: `pip install -r requirements.txt --no-cache-dir`

### Step 3: Set Up Frontend

```bash
cd frontend
npm install
cd ..
```

**Troubleshooting:**
- If npm is slow, try: `npm install --legacy-peer-deps`
- If you get permission errors, try running as administrator

### Step 4: Start the Application

**Option A: Automated Start (Windows)**
```powershell
.\scripts\dev_start.ps1
```
This opens two windows - one for backend, one for frontend.

**Option B: Manual Start (All Platforms)**

Terminal 1 - Backend:
```bash
python run.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### Step 5: Open Your Browser

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

---

## 🎯 First Steps

### 1. Try a Prediction

1. Open http://localhost:5173
2. Fill in the loan application form
3. Click "Predict Risk"
4. View the results and explanations

### 2. Try CSV Upload

1. Click "CSV Upload" tab
2. Upload a CSV file (or use the sample)
3. Navigate through rows or batch process
4. Download results

### 3. Explore the API

1. Open http://localhost:8000/docs
2. Try the `/predict_risk` endpoint
3. Click "Try it out"
4. Enter sample data and execute

---

## 🔑 Optional: Enable AI Features

To use Gemini AI features (natural language explanations, mitigation plans):

1. **Get API Key**
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with Google account
   - Create API key

2. **Configure Environment**
   ```bash
   # Copy example file
   cp env.example .env
   
   # Edit .env file
   # Add: GEMINI_API_KEY=your-api-key-here
   ```

3. **Restart Backend**
   ```bash
   # Stop the backend (Ctrl+C)
   # Start it again
   python run.py
   ```

4. **Try AI Features**
   - Use `/predict_risk_gemini` endpoint
   - Get mitigation plans with `/get_mitigation_plan`

---

## 📊 Sample Data

### Manual Entry Example

```json
{
  "person_age": 30,
  "person_income": 50000,
  "person_emp_length": 36,
  "loan_amnt": 10000,
  "loan_int_rate": 10.5,
  "loan_percent_income": 0.20,
  "cb_person_cred_hist_length": 5,
  "home_ownership": "RENT",
  "loan_intent": "PERSONAL",
  "loan_grade": "B",
  "default_on_file": "N"
}
```

### CSV Example

Create a file `sample.csv`:

```csv
person_age,person_income,loan_amnt,loan_int_rate,home_ownership,loan_grade
30,50000,10000,10.5,RENT,B
25,35000,15000,12.0,RENT,C
45,75000,20000,8.5,OWN,A
```

---

## 🧪 Verify Installation

### Check Backend

```bash
# Test API health
curl http://localhost:8000/health

# Or open in browser
# http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "timestamp": "2024-11-19T..."
}
```

### Check Frontend

1. Open http://localhost:5173
2. You should see the Credit Risk Prediction interface
3. Try filling in the form

### Run Tests

```bash
# Run quick tests
pytest -m unit

# Run all tests
pytest
```

---

## 🎓 Next Steps

### Learn the Basics

1. **Read Documentation**
   - [API Guide](docs/api/DYNAMIC_INPUT_GUIDE.md)
   - [CSV Upload Guide](docs/features/CSV_QUICKSTART.md)
   - [Project Structure](PROJECT_STRUCTURE.md)

2. **Try Different Features**
   - Standard predictions
   - Dynamic input (partial data)
   - Gemini AI predictions
   - CSV batch processing

3. **Explore the API**
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Advanced Topics

1. **Database Setup**
   - [Database Guide](docs/DATABASE_RETRAINING_GUIDE.md)
   - Run: `python scripts/setup_database.py`

2. **Model Retraining**
   - [Retraining Guide](docs/DATABASE_RETRAINING_GUIDE.md)
   - Use: `/trigger_retrain` endpoint

3. **Deployment**
   - [Docker Deployment](docker-compose.yml)
   - [CI/CD Guide](docs/CICD_GUIDE.md)

---

## 🆘 Troubleshooting

### Backend Won't Start

**Error: "Port 8000 already in use"**
```bash
# Windows
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Mac/Linux
lsof -ti:8000 | xargs kill
```

**Error: "Module not found"**
```bash
# Make sure virtual environment is activated
# Windows:
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: "Model file not found"**
```bash
# Check if models directory exists
ls models/

# If missing, the app will create it on first run
# Or download pre-trained models
```

### Frontend Won't Start

**Error: "Port 5173 already in use"**
```bash
# Kill the process
# Windows:
Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process

# Mac/Linux:
lsof -ti:5173 | xargs kill
```

**Error: "node_modules not found"**
```bash
cd frontend
npm install
```

**Error: "npm command not found"**
- Install Node.js from https://nodejs.org/
- Restart your terminal

### Virtual Environment Issues

**Windows: "Execution policy" error**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Can't activate virtual environment**
```bash
# Delete and recreate
rm -rf .venv
python -m venv .venv
```

### API Returns Errors

**"LLM explanation disabled"**
- This is normal if you haven't set up Gemini API key
- Add `GEMINI_API_KEY` to `.env` file to enable

**"Model not loaded"**
- Check `models/` directory exists
- Check model files are present
- Restart the backend

---

## 💡 Tips for New Users

### Development Workflow

1. **Keep terminals open**
   - One for backend
   - One for frontend
   - One for commands

2. **Use the automated script** (Windows)
   ```powershell
   .\scripts\dev_start.ps1
   ```

3. **Check logs** when something goes wrong
   - Backend: Terminal output
   - Frontend: Browser console (F12)
   - Application: `logs/app.log`

### Best Practices

1. **Always activate virtual environment** before running Python commands
2. **Use the API docs** (http://localhost:8000/docs) to test endpoints
3. **Start with manual entry** before trying CSV upload
4. **Read error messages** - they usually tell you what's wrong

### Useful Commands

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check Python version
python --version

# Check Node version
node --version

# List installed Python packages
pip list

# Update dependencies
pip install -r requirements.txt --upgrade

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## 📚 Additional Resources

### Documentation
- [README.md](README.md) - Main documentation
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Project organization
- [docs/](docs/) - Detailed guides

### Examples
- [examples/](examples/) - Example scripts
- [frontend/public/sample_data.csv](frontend/public/sample_data.csv) - Sample CSV

### Scripts
- [scripts/README.md](scripts/README.md) - Script documentation
- [scripts/dev_start.ps1](scripts/dev_start.ps1) - Development starter

---

## ✅ Success Checklist

You're ready to go when you can:

- [ ] Start the backend (`python run.py`)
- [ ] Start the frontend (`npm run dev`)
- [ ] Access the web interface (http://localhost:5173)
- [ ] Make a prediction through the UI
- [ ] Access API docs (http://localhost:8000/docs)
- [ ] Run tests (`pytest -m unit`)

---

## 🎉 You're All Set!

Congratulations! You've successfully set up the Credit Risk Prediction System.

**What's Next?**
- Try making predictions
- Upload a CSV file
- Explore the API
- Read the documentation
- Customize the configuration

**Need Help?**
- Check [Troubleshooting](#-troubleshooting)
- Read [Documentation](docs/)
- Check [Common Issues](#-troubleshooting)

---

<div align="center">

**Happy Predicting! 🚀**

[⬆ Back to Top](#-getting-started-guide)

</div>

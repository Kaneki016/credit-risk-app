
# Credit Risk App — Full Stack (FastAPI + React)

Agentic Credit Risk Prediction — a modern full-stack app for loan default risk prediction, SHAP explainability, and automation integration.

## Features

- Beautiful React frontend (`frontend/`) built with Vite
- FastAPI backend (`api.py`) serving ML predictions and explanations
- SHAP explainability, LLM explanations, and operational notes
- n8n workflow integration (optional)
- Logging, model cards, and retraining support

## Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Windows PowerShell (for dev script)

## Quick Start (Development)

1. Create and activate Python virtual environment:
	 ```powershell
	 python -m venv .venv
	 .\.venv\Scripts\Activate.ps1
	 pip install -r requirements.txt
	 ```

2. Install frontend dependencies:
	 ```powershell
	 cd frontend
	 npm install
	 cd ..
	 ```

3. Start both servers (opens two PowerShell windows):
	 ```powershell
	 .\scripts\dev_start.ps1
	 ```
	 - Or start manually:
		 ```powershell
		 uvicorn api:app --reload --host 0.0.0.0 --port 8000
		 cd frontend
		 npm run dev
		 ```

4. Open [http://localhost:5173](http://localhost:5173) in your browser for the React UI.

## API Endpoints

- Main prediction: `POST /predict_risk` (see `api.py`)
- n8n webhook: see `config.py` for URL

## Frontend Usage

- The React app (`frontend/`) collects applicant data and POSTs to the backend API.
- By default, it uses the n8n webhook URL from `config.py`. To call FastAPI directly, edit `frontend/src/components/Form.jsx`:
	```js
	const API_WEBHOOK = 'http://localhost:8000/predict_risk'
	```

## Configuration

### Environment Variables

1. **Gemini API Key (for LLM explanations)**:
   - Create a `.env` file in the project root (copy from `env.example`)
   - Get your API key from: https://aistudio.google.com/app/apikey
   - Add to `.env`: `GEMINI_API_KEY="your-api-key-here"`
   - **Note**: Without this key, LLM explanations will be disabled and show "LLM explanation disabled (no API key)"

### Other Configuration

- Edit `config.py` to change webhook URLs, model filenames, log paths, and risk thresholds.
- Place model artifacts in the project root or update paths in `config.py`:
	- `credit_risk_model.pkl`
	- `scaler.pkl`
	- `feature_names.json`

## Logging & Artifacts

- Logs: `logs/app.log` (rotating file handler)
- Prediction logs: `prediction_logs.csv` (generated at runtime)
- Model cards: `model_cards/`

## Repository Hygiene

- `.gitignore` excludes venv, logs, data, notebooks, model artifacts, and frontend build files.
- See `CLEANUP.md` for safe removal of large or sensitive files from git history.

## License

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.
{


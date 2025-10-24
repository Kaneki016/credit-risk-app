# credit-risk-app

Agentic Credit Risk Prediction — a small Streamlit front-end + FastAPI prediction service that
lets you predict loan default risk, view SHAP explanations, and integrate with automation tools
like n8n.

Features

- Interactive Streamlit UI (`app.py`) to collect applicant data and display results
- FastAPI prediction endpoint (`api.py`) that loads the model via `predictor.py` and returns
	a prediction, SHAP explanation and an optional LLM explanation
- SHAP explainability support and logging
- Small dev helpers: `scripts/test_predictor.py`, `scripts/dev_start.ps1`

Prerequisites

- Python 3.10+ recommended
- Windows PowerShell for the provided dev script (POSIX shells will work too)

Quick start (local)

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install requirements:

```powershell
pip install -r requirements.txt
```

3. Start both services using the helper (opens two PowerShell windows):

```powershell
.\scripts\dev_start.ps1
```

Or start them manually in separate shells:

```powershell
# Start FastAPI (local dev)
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Start Streamlit
streamlit run app.py
```

Quick test (no Streamlit / n8n)

```powershell
python .\scripts\test_predictor.py
```

Configuration

- Edit `config.py` to change `N8N_WEBHOOK_URL`, model filenames, `LOG_PATH`, and `FLAG_THRESHOLD`.
- Place model artifacts in the project root (or update `config.py`):
	- `credit_risk_model.pkl`
	- `scaler.pkl`
	- `feature_names.pkl`

n8n integration

- The Streamlit app posts a JSON payload to `N8N_WEBHOOK_URL`. The API expects a `LoanApplication`-shaped
	payload; fields used by the predictor are:

```json
{
	"person_age": 30,
	"person_income": 50000.0,
	"person_emp_length": 12.0,
	"loan_amnt": 10000.0,
	"loan_int_rate": 10.0,
	"loan_percent_income": 0.25,
	"cb_person_cred_hist_length": 5,
	"home_ownership": "RENT",
	"loan_intent": "PERSONAL",
	"loan_grade": "A",
	"default_on_file": "N"
}
```

- The API returns a JSON object containing (at minimum):
	- `risk_level` (string)
	- `probability_default_percent` (0-100)
	- `binary_prediction` (0 or 1)
	- `shap_explanation` (flat dict feature -> shap value)
	- `llm_explanation` (optional string)

Logging and artifacts

- App logs are written to `logs/app.log` (rotating file handler). Use `Get-Content .\logs\app.log -Wait` to follow logs.
- Prediction calls are appended to `prediction_logs.csv` by default. This file is generated at runtime.

Repository hygiene & cleanup

- `.gitignore` has been updated to exclude `.venv/`, `prediction_logs.csv`, `logs/`, `data/` and `notebooks/`.
- If you previously committed `prediction_logs.csv` or large assets, see `CLEANUP.md` for safe `git rm --cached` and move commands.

Development tips

- Use `scripts/dev_start.ps1` to start both services on Windows.
- Use `scripts/test_predictor.py` to verify model loading without running the UI or n8n.
- Central config is in `config.py` — change webhook URLs and filenames there.

License

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.


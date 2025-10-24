# config.py
"""Central configuration for the credit-risk-app project.
Keep environment-specific or secret values out of source control in production.
"""

# n8n webhook (used by Streamlit frontend)
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/6c5765f3-1d52-4d65-be13-c37133a73bf1"

# Local log file used by prediction logging
LOG_PATH = "prediction_logs.csv"

# Threshold for flagging high risk (probability of default)
FLAG_THRESHOLD = 0.6

# Model artifact filenames (relative to project root)
MODELS_DIR = "models"
MODEL_PKL = "models/credit_risk_model.pkl"
SCALER_PKL = "models/scaler.pkl"
FEATURE_NAMES_PKL = "models/feature_names.json"

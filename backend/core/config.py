# config.py
"""Central configuration for the credit-risk-app project.
Keep environment-specific or secret values out of source control in production.
"""

# API endpoint for frontend
API_BASE_URL = "http://localhost:8000"

# Local log file used by prediction logging
LOG_PATH = "prediction_logs.csv"

# Threshold for flagging high risk (probability of default)
FLAG_THRESHOLD = 0.6

# Model artifact filenames (relative to project root)
import os
from pathlib import Path

# Get project root (3 levels up from this file: backend/core/config.py -> project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PKL = str(MODELS_DIR / "credit_risk_model.pkl")
SCALER_PKL = str(MODELS_DIR / "scaler.pkl")
FEATURE_NAMES_PKL = str(MODELS_DIR / "feature_names.json")

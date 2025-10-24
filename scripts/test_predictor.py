"""Small helper to validate that the predictor loads and produces an output.
Run with: python scripts/test_predictor.py (from project root)

This script adjusts sys.path so it can import modules from the project root even when
executed from the `scripts/` folder.
"""
import sys
from pathlib import Path
import json

# Ensure project root is on sys.path so `from predictor import ...` works when running
# this script directly (python scripts/test_predictor.py)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from predictor import CreditRiskPredictor

sample_input = {
    "person_age": 30,
    "person_income": 50000.0,
    "person_emp_length": 12.0,
    "loan_amnt": 10000.0,
    "loan_int_rate": 10.0,
    "loan_percent_income": 0.2,
    "cb_person_cred_hist_length": 5,
    "person_home_ownership_RENT": 1,
    "loan_intent_PERSONAL": 1,
    "loan_grade_A": 1,
    "cb_person_default_on_file_N": 1
}

if __name__ == '__main__':
    pred = None
    try:
        predictor = CreditRiskPredictor()
        print("Model and artifacts loaded successfully.")
        risk_level, prob, pred = predictor.predict(sample_input)
        print("Prediction:")
        print(json.dumps({
            "risk_level": risk_level,
            "probability": prob,
            "binary_prediction": pred
        }, indent=2))
    except Exception as e:
        print("Predictor failed:", e)
        raise

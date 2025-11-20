"""Simple integration test to validate predictor loads and produces an output.

Run with: pytest -q (or `python -m pytest -q` from project root).
"""

import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path so imports work when running tests
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.models.predictor import CreditRiskPredictor


@pytest.mark.unit
def test_predictor_smoke():
    """Test that the predictor can load and make predictions."""
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
        "cb_person_default_on_file_N": 1,
    }

    predictor = CreditRiskPredictor()
    risk_level, prob, pred = predictor.predict(sample_input)

    # Basic assertions: probability in [0,1], pred is 0/1
    assert 0.0 <= prob <= 1.0, f"Probability {prob} not in valid range [0,1]"
    assert pred in (0, 1), f"Prediction {pred} not in valid set {{0, 1}}"
    assert risk_level in ["Low Risk 🟢", "Medium Risk 🟡", "High Risk 🔴"], f"Risk level '{risk_level}' not recognized"

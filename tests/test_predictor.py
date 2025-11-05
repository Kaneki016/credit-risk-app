"""Simple integration test to validate predictor loads and produces an output.

Run with: pytest -q (or `python -m pytest -q` from project root).

The original helper lived in `scripts/test_predictor.py` — moving it into `tests/`
so it can run as part of the project's test suite.
"""
import sys
from pathlib import Path
import json

# Ensure project root is on sys.path so imports work when running tests
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from predictor import CreditRiskPredictor


def test_predictor_smoke():
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

    predictor = CreditRiskPredictor()
    risk_level, prob, pred = predictor.predict(sample_input)
    # Basic assertions: probability in [0,1], pred is 0/1
    assert 0.0 <= prob <= 1.0
    assert pred in (0, 1)

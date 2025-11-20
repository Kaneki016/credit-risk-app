#!/usr/bin/env python3
"""
Integration test script for the dynamic prediction API.
Demonstrates various input scenarios with partial/complete data.

Note: This is a manual integration test that requires the API to be running.
Run the API first: python run.py
Then run this script: python tests/backend/test_dynamic_api.py

For automated testing, use pytest with proper fixtures and mocking.
"""

import requests
import json
from typing import Dict, Any
import pytest

API_BASE = "http://localhost:8000"


def print_response(title: str, response: Dict[str, Any]):
    """Pretty print API response."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")
    print(json.dumps(response, indent=2))
    print()


@pytest.mark.integration
@pytest.mark.requires_api
def test_complete_data():
    """Test with complete data (all fields provided)."""
    data = {
        "person_age": 30,
        "person_income": 50000.0,
        "person_emp_length": 24.0,
        "loan_amnt": 10000.0,
        "loan_int_rate": 10.0,
        "loan_percent_income": 0.20,
        "cb_person_cred_hist_length": 5.0,
        "home_ownership": "RENT",
        "loan_intent": "PERSONAL",
        "loan_grade": "B",
        "default_on_file": "N",
    }

    response = requests.post(f"{API_BASE}/predict_risk_dynamic", json=data)
    print_response("TEST 1: Complete Data", response.json())


@pytest.mark.integration
@pytest.mark.requires_api
def test_minimal_data():
    """Test with minimal data (only critical fields)."""
    data = {"person_income": 60000.0, "loan_amnt": 15000.0}

    response = requests.post(f"{API_BASE}/predict_risk_dynamic", json=data)
    result = response.json()
    print_response("TEST 2: Minimal Data (Only Income & Loan Amount)", result)

    # Show what was imputed
    if "imputation_log" in result:
        print("Imputed fields:")
        for log_entry in result["imputation_log"]:
            print(f"  - {log_entry}")


@pytest.mark.integration
@pytest.mark.requires_api
def test_partial_data_with_derivation():
    """Test with data that allows derivation (loan_percent_income can be calculated)."""
    data = {"person_age": 45, "person_income": 80000.0, "loan_amnt": 20000.0, "loan_grade": "C", "home_ownership": "OWN"}

    response = requests.post(f"{API_BASE}/predict_risk_dynamic", json=data)
    result = response.json()
    print_response("TEST 3: Partial Data with Derivable Fields", result)

    # Check if loan_percent_income was derived
    if "input_features_imputed" in result:
        derived = result["input_features_imputed"].get("loan_percent_income")
        expected = 20000.0 / 80000.0
        print(f"loan_percent_income derived: {derived} (expected: {expected})")


@pytest.mark.integration
@pytest.mark.requires_api
def test_high_risk_scenario():
    """Test a high-risk loan scenario."""
    data = {
        "person_age": 22,
        "person_income": 25000.0,
        "loan_amnt": 30000.0,
        "loan_int_rate": 18.5,
        "cb_person_cred_hist_length": 1.0,
        "default_on_file": "Y",
        "loan_grade": "F",
    }

    response = requests.post(f"{API_BASE}/predict_risk_dynamic", json=data)
    result = response.json()
    print_response("TEST 4: High Risk Scenario", result)

    # Show remediation suggestion
    if "remediation_suggestion" in result and result["remediation_suggestion"]:
        print("Remediation Suggestion:")
        print(f"  {result['remediation_suggestion']}")


@pytest.mark.integration
@pytest.mark.requires_api
def test_low_risk_scenario():
    """Test a low-risk loan scenario."""
    data = {
        "person_age": 40,
        "person_income": 120000.0,
        "loan_amnt": 15000.0,
        "loan_int_rate": 6.5,
        "person_emp_length": 120.0,
        "cb_person_cred_hist_length": 15.0,
        "home_ownership": "OWN",
        "loan_grade": "A",
        "default_on_file": "N",
    }

    response = requests.post(f"{API_BASE}/predict_risk_dynamic", json=data)
    result = response.json()
    print_response("TEST 5: Low Risk Scenario", result)


@pytest.mark.integration
@pytest.mark.requires_api
def test_extra_fields():
    """Test with extra fields that aren't in the model (should be ignored)."""
    data = {
        "person_income": 55000.0,
        "loan_amnt": 12000.0,
        "loan_grade": "B",
        # Extra fields not in model
        "applicant_name": "John Doe",
        "application_id": "APP-12345",
        "requested_date": "2024-01-15",
    }

    response = requests.post(f"{API_BASE}/predict_risk_dynamic", json=data)
    result = response.json()
    print_response("TEST 6: Data with Extra Fields (Should Be Ignored)", result)


@pytest.mark.integration
@pytest.mark.requires_api
def test_edge_cases():
    """Test edge cases and boundary values."""
    data = {
        "person_age": 18,  # Minimum age
        "person_income": 15000.0,  # Low income
        "loan_amnt": 50000.0,  # Large loan relative to income
        "loan_int_rate": 25.0,  # High interest rate
        "cb_person_cred_hist_length": 0.5,  # Very short credit history
    }

    response = requests.post(f"{API_BASE}/predict_risk_dynamic", json=data)
    result = response.json()
    print_response("TEST 7: Edge Cases & Boundary Values", result)

    # Check for drift warnings
    if "data_drift_warnings" in result and result["data_drift_warnings"]:
        print("Data Drift Warnings:")
        for warning in result["data_drift_warnings"]:
            print(f"  - {warning}")


def compare_endpoints():
    """Compare standard vs dynamic endpoint with same data."""
    data = {
        "person_age": 35,
        "person_income": 65000.0,
        "person_emp_length": 36.0,
        "loan_amnt": 18000.0,
        "loan_int_rate": 11.5,
        "loan_percent_income": 0.28,
        "cb_person_cred_hist_length": 7.0,
        "home_ownership": "MORTGAGE",
        "loan_intent": "HOMEIMPROVEMENT",
        "loan_grade": "C",
        "default_on_file": "N",
    }

    # Standard endpoint
    response1 = requests.post(f"{API_BASE}/predict_risk", json=data)
    result1 = response1.json()

    # Dynamic endpoint
    response2 = requests.post(f"{API_BASE}/predict_risk_dynamic", json=data)
    result2 = response2.json()

    print(f"\n{'='*80}")
    print("  COMPARISON: Standard vs Dynamic Endpoint")
    print(f"{'='*80}")
    print(f"Standard endpoint risk: {result1.get('risk_level')}")
    print(f"Dynamic endpoint risk:  {result2.get('risk_level')}")
    print(f"Standard probability:   {result1.get('probability_default_percent')}%")
    print(f"Dynamic probability:    {result2.get('probability_default_percent')}%")
    print(f"Results match: {result1.get('risk_level') == result2.get('risk_level')}")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  DYNAMIC PREDICTION API TEST SUITE")
    print("=" * 80)
    print(f"Testing API at: {API_BASE}")

    # Check if API is running
    try:
        health = requests.get(f"{API_BASE}/health")
        if health.status_code != 200:
            print("ERROR: API is not healthy!")
            return
    except Exception as e:
        print(f"ERROR: Cannot connect to API: {e}")
        print("Make sure the API is running: uvicorn api:app --reload")
        return

    tests = [
        ("Complete Data", test_complete_data),
        ("Minimal Data", test_minimal_data),
        ("Partial Data with Derivation", test_partial_data_with_derivation),
        ("High Risk Scenario", test_high_risk_scenario),
        ("Low Risk Scenario", test_low_risk_scenario),
        ("Extra Fields", test_extra_fields),
        ("Edge Cases", test_edge_cases),
        ("Endpoint Comparison", compare_endpoints),
    ]

    for name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {e}")

    print("\n" + "=" * 80)
    print("  TEST SUITE COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

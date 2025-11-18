"""
Quick examples of using the dynamic input API.
Copy and paste these into your code or use as reference.
"""

import requests

API_URL = "http://localhost:8000/predict_risk_dynamic"

# Example 1: Minimal input - just income and loan amount
def minimal_example():
    """Send only the most critical fields."""
    response = requests.post(API_URL, json={
        "person_income": 60000.0,
        "loan_amnt": 15000.0
    })
    return response.json()

# Example 2: Partial input with some context
def partial_example():
    """Send some fields, let the system fill in the rest."""
    response = requests.post(API_URL, json={
        "person_age": 35,
        "person_income": 75000.0,
        "loan_amnt": 20000.0,
        "loan_grade": "B",
        "home_ownership": "OWN"
    })
    return response.json()

# Example 3: High risk scenario
def high_risk_example():
    """Test a risky loan application."""
    response = requests.post(API_URL, json={
        "person_age": 22,
        "person_income": 25000.0,
        "loan_amnt": 30000.0,
        "loan_int_rate": 18.5,
        "default_on_file": "Y",
        "loan_grade": "F"
    })
    result = response.json()
    
    # Print key information
    print(f"Risk Level: {result['risk_level']}")
    print(f"Probability: {result['probability_default_percent']}%")
    if result.get('remediation_suggestion'):
        print(f"Suggestion: {result['remediation_suggestion']}")
    
    return result

# Example 4: Progressive data collection
def progressive_collection_example():
    """Simulate collecting data progressively over multiple steps."""
    
    # Step 1: Initial inquiry with just basic info
    step1 = requests.post(API_URL, json={
        "person_income": 55000.0,
        "loan_amnt": 12000.0
    }).json()
    print(f"Step 1 Risk: {step1['risk_level']}")
    
    # Step 2: Add more details
    step2 = requests.post(API_URL, json={
        "person_income": 55000.0,
        "loan_amnt": 12000.0,
        "person_age": 32,
        "home_ownership": "RENT",
        "loan_grade": "C"
    }).json()
    print(f"Step 2 Risk: {step2['risk_level']}")
    
    # Step 3: Complete application
    step3 = requests.post(API_URL, json={
        "person_income": 55000.0,
        "loan_amnt": 12000.0,
        "person_age": 32,
        "home_ownership": "RENT",
        "loan_grade": "C",
        "person_emp_length": 48.0,
        "loan_int_rate": 11.0,
        "cb_person_cred_hist_length": 6.0,
        "loan_intent": "DEBTCONSOLIDATION",
        "default_on_file": "N"
    }).json()
    print(f"Step 3 Risk: {step3['risk_level']}")
    
    return step1, step2, step3

# Example 5: Batch processing with varying completeness
def batch_processing_example():
    """Process multiple applications with different levels of completeness."""
    applications = [
        {"person_income": 45000, "loan_amnt": 8000},
        {"person_income": 70000, "loan_amnt": 15000, "loan_grade": "B"},
        {"person_income": 90000, "loan_amnt": 25000, "person_age": 40, "home_ownership": "OWN"},
    ]
    
    results = []
    for i, app in enumerate(applications, 1):
        response = requests.post(API_URL, json=app)
        result = response.json()
        print(f"Application {i}: {result['risk_level']} ({result['probability_default_percent']}%)")
        results.append(result)
    
    return results

# Example 6: Check what was imputed
def check_imputation_example():
    """See exactly what fields were filled in automatically."""
    response = requests.post(API_URL, json={
        "person_income": 50000.0,
        "loan_amnt": 10000.0,
        "loan_grade": "B"
    })
    result = response.json()
    
    print("Original input:")
    print(result['input_features_original'])
    
    print("\nImputed values:")
    print(result['input_features_imputed'])
    
    print("\nImputation log:")
    for log_entry in result['imputation_log']:
        print(f"  - {log_entry}")
    
    return result

if __name__ == "__main__":
    print("Dynamic Input API Examples\n")
    
    print("1. Minimal Example:")
    result = minimal_example()
    print(f"   Risk: {result['risk_level']}\n")
    
    print("2. Partial Example:")
    result = partial_example()
    print(f"   Risk: {result['risk_level']}\n")
    
    print("3. High Risk Example:")
    high_risk_example()
    print()
    
    print("4. Progressive Collection:")
    progressive_collection_example()
    print()
    
    print("5. Batch Processing:")
    batch_processing_example()
    print()
    
    print("6. Check Imputation:")
    check_imputation_example()

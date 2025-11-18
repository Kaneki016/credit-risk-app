#!/usr/bin/env python3
"""
Test script for Gemini predictor.
Compare traditional ML model with Gemini AI predictions.
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

# Sample test cases
test_cases = [
    {
        "name": "Low Risk - Stable Applicant",
        "data": {
            "person_age": 35,
            "person_income": 75000,
            "person_emp_length": 60,
            "loan_amnt": 15000,
            "loan_int_rate": 8.5,
            "loan_percent_income": 0.20,
            "cb_person_cred_hist_length": 10,
            "home_ownership": "OWN",
            "loan_intent": "HOMEIMPROVEMENT",
            "loan_grade": "A",
            "default_on_file": "N"
        }
    },
    {
        "name": "High Risk - Previous Default",
        "data": {
            "person_age": 22,
            "person_income": 28000,
            "person_emp_length": 6,
            "loan_amnt": 20000,
            "loan_int_rate": 18.5,
            "loan_percent_income": 0.71,
            "cb_person_cred_hist_length": 1,
            "home_ownership": "RENT",
            "loan_intent": "PERSONAL",
            "loan_grade": "F",
            "default_on_file": "Y"
        }
    },
    {
        "name": "Borderline - Mixed Signals",
        "data": {
            "person_age": 28,
            "person_income": 45000,
            "person_emp_length": 18,
            "loan_amnt": 18000,
            "loan_int_rate": 12.0,
            "loan_percent_income": 0.40,
            "cb_person_cred_hist_length": 4,
            "home_ownership": "RENT",
            "loan_intent": "DEBTCONSOLIDATION",
            "loan_grade": "C",
            "default_on_file": "N"
        }
    }
]

def test_gemini_only():
    """Test Gemini predictor only."""
    print("\n" + "="*80)
    print("GEMINI AI PREDICTOR TEST")
    print("="*80)
    
    for test_case in test_cases:
        print(f"\n📋 Test Case: {test_case['name']}")
        print("-" * 80)
        
        try:
            start = time.time()
            response = requests.post(
                f"{API_BASE}/predict_risk_gemini",
                json=test_case['data'],
                timeout=30
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {result['status']}")
                print(f"🎯 Risk Level: {result['risk_level']}")
                print(f"📊 Probability: {result['probability_default_percent']}%")
                print(f"🔮 Confidence: {result.get('confidence', 'N/A')}%")
                print(f"⏱️  Latency: {elapsed:.2f}s")
                print(f"\n💡 Key Factors:")
                for factor in result.get('key_factors', []):
                    print(f"   • {factor}")
                print(f"\n📝 Explanation:")
                print(f"   {result.get('explanation', 'N/A')[:200]}...")
                if result.get('remediation_suggestion'):
                    print(f"\n🔧 Remediation:")
                    print(f"   {result['remediation_suggestion'][:200]}...")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_comparison():
    """Test both models and compare."""
    print("\n" + "="*80)
    print("MODEL COMPARISON TEST")
    print("="*80)
    
    for test_case in test_cases:
        print(f"\n📋 Test Case: {test_case['name']}")
        print("-" * 80)
        
        try:
            start = time.time()
            response = requests.post(
                f"{API_BASE}/predict_risk_compare",
                json=test_case['data'],
                timeout=30
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                
                ml = result['traditional_ml']
                gemini = result['gemini_ai']
                comp = result['comparison']
                
                print(f"⏱️  Total Latency: {elapsed:.2f}s\n")
                
                print("🤖 Traditional ML (XGBoost):")
                print(f"   Risk: {ml['risk_level']}")
                print(f"   Probability: {ml['probability_default_percent']}%")
                print(f"   Prediction: {ml['binary_prediction']}")
                
                print(f"\n🧠 Gemini AI:")
                print(f"   Risk: {gemini['risk_level']}")
                print(f"   Probability: {gemini['probability_default_percent']}%")
                print(f"   Prediction: {gemini['binary_prediction']}")
                print(f"   Confidence: {gemini.get('confidence', 'N/A')}%")
                
                print(f"\n📊 Comparison:")
                print(f"   Agreement: {'✅ Yes' if comp['predictions_agree'] else '❌ No'}")
                print(f"   Probability Difference: {comp['probability_difference']}%")
                print(f"   Agreement Level: {comp['agreement_level']}")
                print(f"   Recommendation: {comp['recommendation']}")
                
                if not comp['predictions_agree']:
                    print(f"\n⚠️  Models disagree - manual review recommended!")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_minimal_data():
    """Test with minimal data (dynamic imputation)."""
    print("\n" + "="*80)
    print("MINIMAL DATA TEST (Dynamic Imputation)")
    print("="*80)
    
    minimal_data = {
        "person_income": 50000,
        "loan_amnt": 10000
    }
    
    print(f"\n📋 Input: {json.dumps(minimal_data, indent=2)}")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{API_BASE}/predict_risk_gemini",
            json=minimal_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result['status']}")
            print(f"🎯 Risk Level: {result['risk_level']}")
            print(f"📊 Probability: {result['probability_default_percent']}%")
            
            print(f"\n🔄 Imputed Fields:")
            for log in result.get('imputation_log', []):
                print(f"   • {log}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Run all tests."""
    print("\n🚀 Starting Gemini Predictor Tests")
    print("Make sure the API is running: python run.py\n")
    
    # Check API health
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not healthy!")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure to run: python run.py")
        return
    
    # Run tests
    test_gemini_only()
    test_comparison()
    test_minimal_data()
    
    print("\n" + "="*80)
    print("✅ All tests complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

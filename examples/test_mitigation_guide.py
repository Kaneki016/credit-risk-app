"""
Test script for Gemini Mitigation Guide.
Demonstrates how to generate personalized risk mitigation strategies.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.gemini_predictor import GeminiCreditRiskPredictor
from backend.models.gemini_mitigation_guide import GeminiMitigationGuide
import json


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_mitigation_guide():
    """Test the mitigation guide with various risk scenarios."""
    
    print_section("Gemini Mitigation Guide Test")
    
    # Initialize predictors
    try:
        predictor = GeminiCreditRiskPredictor()
        mitigation_guide = GeminiMitigationGuide()
        print("✅ Gemini services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("\nMake sure GEMINI_API_KEY is set in your .env file")
        return
    
    # Test scenarios
    scenarios = [
        {
            "name": "High Risk - Large Loan",
            "data": {
                "person_age": 25,
                "person_income": 35000,
                "person_emp_length": 1,
                "loan_amnt": 25000,
                "loan_int_rate": 18.5,
                "loan_percent_income": 0.71,
                "cb_person_cred_hist_length": 1,
                "home_ownership": "RENT",
                "loan_intent": "PERSONAL",
                "loan_grade": "D",
                "default_on_file": "Y"
            }
        },
        {
            "name": "Borderline Risk - Medium Loan",
            "data": {
                "person_age": 30,
                "person_income": 50000,
                "person_emp_length": 3,
                "loan_amnt": 15000,
                "loan_int_rate": 12.5,
                "loan_percent_income": 0.30,
                "cb_person_cred_hist_length": 3,
                "home_ownership": "RENT",
                "loan_intent": "EDUCATION",
                "loan_grade": "C",
                "default_on_file": "N"
            }
        }
    ]
    
    for scenario in scenarios:
        print_section(f"Scenario: {scenario['name']}")
        
        print("\n📋 Applicant Data:")
        print(json.dumps(scenario['data'], indent=2))
        
        try:
            # Get risk assessment
            print("\n🔍 Getting risk assessment...")
            risk_level, prob, pred, full_result = predictor.predict(scenario['data'])
            
            print(f"\n📊 Risk Assessment:")
            print(f"  Risk Level: {risk_level}")
            print(f"  Default Probability: {prob*100:.1f}%")
            print(f"  Prediction: {'Will Default' if pred == 1 else 'Will Repay'}")
            print(f"\n  Key Factors:")
            for factor in full_result.get('key_factors', [])[:5]:
                print(f"    • {factor}")
            
            # Generate mitigation plan
            print("\n💡 Generating mitigation plan...")
            mitigation_plan = mitigation_guide.generate_mitigation_plan(
                input_data=scenario['data'],
                risk_assessment=full_result
            )
            
            print(f"\n🎯 Mitigation Strategy:")
            print(f"  Overall: {mitigation_plan.get('overall_strategy', 'N/A')}")
            
            print(f"\n⚡ Immediate Actions:")
            for action in mitigation_plan.get('immediate_actions', [])[:3]:
                print(f"  • {action.get('action', 'N/A')}")
                print(f"    Impact: {action.get('impact', 'N/A')}")
                print(f"    Timeline: {action.get('timeline', 'N/A')}")
            
            print(f"\n📅 Short-Term Goals:")
            for goal in mitigation_plan.get('short_term_goals', [])[:2]:
                print(f"  • {goal.get('goal', 'N/A')}")
                print(f"    Timeline: {goal.get('timeline', 'N/A')}")
            
            print(f"\n🎓 Long-Term Improvements:")
            for improvement in mitigation_plan.get('long_term_improvements', [])[:2]:
                print(f"  • {improvement.get('improvement', 'N/A')}")
                print(f"    Benefit: {improvement.get('benefit', 'N/A')}")
            
            print(f"\n🔄 Alternative Options:")
            for option in mitigation_plan.get('alternative_options', [])[:3]:
                print(f"  • {option}")
            
            print(f"\n📈 Estimated Risk Reduction: {mitigation_plan.get('estimated_risk_reduction', 'N/A')}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print_section("Test Complete")
    print("\n✅ Mitigation guide test completed successfully!")
    print("\nNext steps:")
    print("  1. Review the generated mitigation plans")
    print("  2. Test with your own scenarios")
    print("  3. Integrate into your application workflow")
    print("  4. Use POST /get_mitigation_plan endpoint in production")


if __name__ == "__main__":
    test_mitigation_guide()

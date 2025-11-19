"""
Test New Features
Tests the clear database and flexible training features.
"""

import pandas as pd
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


def test_flexible_training():
    """Test flexible model training with a sample CSV."""
    print("=" * 70)
    print("TEST: Flexible Model Training")
    print("=" * 70)
    
    # Create sample training data
    sample_data = pd.DataFrame({
        'loan_status': ['default', 'no_default', 'default', 'no_default', 'default'] * 20,
        'income': [35000, 75000, 28000, 90000, 42000] * 20,
        'loan_amount': [15000, 20000, 25000, 18000, 22000] * 20,
        'credit_score': [650, 720, 580, 750, 680] * 20,
        'employment_years': [2, 8, 1, 10, 5] * 20,
        'home_ownership': ['RENT', 'MORTGAGE', 'RENT', 'OWN', 'MORTGAGE'] * 20,
        'loan_purpose': ['PERSONAL', 'HOME', 'DEBT', 'BUSINESS', 'EDUCATION'] * 20
    })
    
    # Save to CSV
    csv_path = Path("data/test_training_data.csv")
    csv_path.parent.mkdir(exist_ok=True)
    sample_data.to_csv(csv_path, index=False)
    
    print(f"\n✓ Created sample training data: {len(sample_data)} rows")
    print(f"  Columns: {list(sample_data.columns)}")
    print(f"  Target: loan_status")
    print(f"  Features: {len(sample_data.columns) - 1}")
    
    # Test training
    print("\n→ Sending training request...")
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': ('test_data.csv', f, 'text/csv')}
            response = requests.post(f"{BASE_URL}/train/flexible", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Training Successful!")
            print(f"\nMetrics:")
            print(f"  Accuracy: {result['result']['metrics']['accuracy']:.4f}")
            print(f"  AUC-ROC: {result['result']['metrics']['auc_roc']:.4f}")
            print(f"  F1 Score: {result['result']['metrics']['f1_score']:.4f}")
            
            print(f"\nDetected Features:")
            print(f"  Target: {result['result']['preprocessing_info']['target_column']}")
            print(f"  Numeric: {len(result['result']['preprocessing_info']['numeric_features'])}")
            print(f"  Categorical: {len(result['result']['preprocessing_info']['categorical_features'])}")
            print(f"  Total Features: {result['result']['preprocessing_info']['n_features']}")
            
            return True
        else:
            print(f"\n❌ Training Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n⚠️  Backend not running. Start with: python run.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_clear_database():
    """Test database clearing (with confirmation)."""
    print("\n" + "=" * 70)
    print("TEST: Clear Database")
    print("=" * 70)
    
    print("\n⚠️  This test will clear the database!")
    print("Make sure you're testing with non-production data.")
    
    response = input("\nProceed with database clear test? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Test skipped.")
        return False
    
    try:
        print("\n→ Sending clear database request...")
        response = requests.delete(f"{BASE_URL}/db/clear?confirm=true")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Database Cleared Successfully!")
            print(f"\nDeleted Records:")
            for table, count in result['deleted'].items():
                print(f"  {table}: {count}")
            print(f"\nTotal Deleted: {result['total_deleted']}")
            return True
        else:
            print(f"\n❌ Clear Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n⚠️  Backend not running. Start with: python run.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_api_endpoints():
    """Test that new endpoints are available."""
    print("\n" + "=" * 70)
    print("TEST: API Endpoints")
    print("=" * 70)
    
    endpoints = [
        ("POST", "/train/flexible", "Flexible Training"),
        ("DELETE", "/db/clear", "Clear Database")
    ]
    
    try:
        # Get OpenAPI schema
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get('paths', {})
            
            print("\n✓ Checking endpoints...")
            for method, path, name in endpoints:
                if path in paths and method.lower() in paths[path]:
                    print(f"  ✓ {name}: {method} {path}")
                else:
                    print(f"  ✗ {name}: {method} {path} - NOT FOUND")
            
            return True
        else:
            print(f"\n⚠️  Could not fetch API schema: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n⚠️  Backend not running. Start with: python run.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("NEW FEATURES TEST SUITE")
    print("=" * 70)
    print("\nTesting new features:")
    print("  1. Flexible Model Training")
    print("  2. Clear Database")
    print("  3. API Endpoints")
    
    # Test API endpoints first
    test_api_endpoints()
    
    # Test flexible training
    training_success = test_flexible_training()
    
    # Test clear database (optional)
    clear_success = test_clear_database()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Flexible Training: {'✅ PASSED' if training_success else '❌ FAILED'}")
    print(f"Clear Database: {'✅ PASSED' if clear_success else '⏭️  SKIPPED'}")
    print("=" * 70)
    
    if training_success:
        print("\n✅ New features are working correctly!")
        print("\nNext steps:")
        print("  1. Open frontend: http://localhost:5173")
        print("  2. Go to Admin Panel")
        print("  3. Try the new 'Train Model' and 'Manage' tabs")
    else:
        print("\n⚠️  Some tests failed. Check the backend logs.")

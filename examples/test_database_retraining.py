"""
Test script for database retraining.
Demonstrates how to retrain the model using database data.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import pandas as pd
from backend.database import SessionLocal, crud
from backend.services.database_retraining import DatabaseRetrainer
import random


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def create_sample_predictions_with_feedback():
    """Create sample predictions with feedback for testing."""
    
    print_section("Creating Sample Predictions with Feedback")
    
    db = SessionLocal()
    
    try:
        # Sample data
        samples = [
            {
                "input_features": {
                    "person_age": 30,
                    "person_income": 50000,
                    "person_emp_length": 36,
                    "loan_amnt": 10000,
                    "loan_int_rate": 10.5,
                    "loan_percent_income": 0.20,
                    "cb_person_cred_hist_length": 5,
                    "home_ownership": "RENT",
                    "loan_intent": "PERSONAL",
                    "loan_grade": "B",
                    "default_on_file": "N"
                },
                "risk_level": "Low Risk 🟢",
                "probability_default": 0.15,
                "binary_prediction": 0,
                "actual_outcome": 0  # Did not default
            },
            {
                "input_features": {
                    "person_age": 25,
                    "person_income": 35000,
                    "person_emp_length": 12,
                    "loan_amnt": 25000,
                    "loan_int_rate": 18.5,
                    "loan_percent_income": 0.71,
                    "cb_person_cred_hist_length": 2,
                    "home_ownership": "RENT",
                    "loan_intent": "PERSONAL",
                    "loan_grade": "D",
                    "default_on_file": "Y"
                },
                "risk_level": "High Risk 🔴",
                "probability_default": 0.85,
                "binary_prediction": 1,
                "actual_outcome": 1  # Did default
            },
            {
                "input_features": {
                    "person_age": 45,
                    "person_income": 75000,
                    "person_emp_length": 120,
                    "loan_amnt": 15000,
                    "loan_int_rate": 8.5,
                    "loan_percent_income": 0.20,
                    "cb_person_cred_hist_length": 10,
                    "home_ownership": "OWN",
                    "loan_intent": "EDUCATION",
                    "loan_grade": "A",
                    "default_on_file": "N"
                },
                "risk_level": "Low Risk 🟢",
                "probability_default": 0.10,
                "binary_prediction": 0,
                "actual_outcome": 0  # Did not default
            }
        ]
        
        # Create multiple predictions
        created_count = 0
        for i in range(50):  # Create 50 samples
            sample = random.choice(samples)
            
            prediction_data = {
                "input_features": sample["input_features"],
                "risk_level": sample["risk_level"],
                "probability_default": sample["probability_default"],
                "binary_prediction": sample["binary_prediction"],
                "model_type": "traditional",
                "actual_outcome": sample["actual_outcome"]
            }
            
            crud.create_prediction(db, prediction_data)
            created_count += 1
        
        print(f"\n✅ Created {created_count} sample predictions with feedback")
        
    finally:
        db.close()


def test_retraining_status():
    """Test checking retraining status."""
    
    print_section("Checking Retraining Status")
    
    db = SessionLocal()
    
    try:
        retrainer = DatabaseRetrainer(min_samples=10, min_feedback_ratio=0.1)
        status = retrainer.check_retraining_readiness(db)
        
        print(f"\n📊 Retraining Status:")
        print(f"  Ready: {'✅ Yes' if status['is_ready'] else '❌ No'}")
        print(f"  Total Predictions: {status['total_predictions']}")
        print(f"  Predictions with Feedback: {status['feedback_count']}")
        print(f"  Feedback Ratio: {status['feedback_ratio']:.1%}")
        print(f"  Minimum Required: {status['min_samples_required']} samples")
        print(f"  Minimum Feedback Ratio: {status['min_feedback_ratio_required']:.1%}")
        
        if not status['is_ready']:
            print(f"\n⚠️  Not Ready:")
            print(f"  Need {status['samples_needed']} more samples")
            print(f"  Need {status['feedback_needed']} more feedback entries")
        
        return status['is_ready']
        
    finally:
        db.close()


def test_export_training_data():
    """Test exporting training data."""
    
    print_section("Exporting Training Data")
    
    db = SessionLocal()
    
    try:
        retrainer = DatabaseRetrainer()
        output_path = retrainer.export_training_data(db)
        
        print(f"\n✅ Training data exported to: {output_path}")
        
        # Load and show preview
        df = pd.read_csv(output_path)
        print(f"\n📋 Data Preview:")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print(f"\n  First 3 rows:")
        print(df.head(3).to_string(index=False))
        
        return output_path
        
    finally:
        db.close()


def test_model_retraining():
    """Test model retraining."""
    
    print_section("Retraining Model")
    
    db = SessionLocal()
    
    try:
        retrainer = DatabaseRetrainer(min_samples=10, min_feedback_ratio=0.1)
        
        print("\n⚙️  Starting retraining...")
        result = retrainer.retrain_model(db, test_size=0.2, save_model=True)
        
        print(f"\n✅ Retraining Complete!")
        print(f"\n📊 Results:")
        print(f"  Status: {result['status']}")
        print(f"  Training Samples: {result['training_samples']}")
        print(f"  Test Samples: {result['test_samples']}")
        print(f"  Features: {result['features_count']}")
        print(f"  Model Version: {result['model_version']}")
        
        print(f"\n📈 Metrics:")
        metrics = result['metrics']
        print(f"  Accuracy: {metrics['accuracy']:.3f}")
        print(f"  Precision: {metrics['precision']:.3f}")
        print(f"  Recall: {metrics['recall']:.3f}")
        print(f"  F1 Score: {metrics['f1_score']:.3f}")
        print(f"  AUC-ROC: {metrics['auc_roc']:.3f}")
        
        print(f"\n🎯 Predictions:")
        print(f"  Total: {metrics['total_predictions']}")
        print(f"  Correct: {metrics['correct_predictions']}")
        print(f"  False Positives: {metrics['false_positives']}")
        print(f"  False Negatives: {metrics['false_negatives']}")
        
        return result
        
    finally:
        db.close()


def test_api_endpoints():
    """Test retraining API endpoints."""
    
    print_section("Testing API Endpoints")
    
    base_url = "http://localhost:8000"
    
    # Test status endpoint
    print("\n1. Checking retraining status...")
    try:
        response = requests.get(f"{base_url}/db/retraining/status")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Status: {result['retraining']['is_ready']}")
            print(f"   Total predictions: {result['retraining']['total_predictions']}")
        else:
            print(f"   ⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  API not running: {e}")
    
    # Test export endpoint
    print("\n2. Exporting training data...")
    try:
        response = requests.post(f"{base_url}/db/export_training_data")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Exported to: {result['file_path']}")
        else:
            print(f"   ⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  API not running: {e}")
    
    # Test retrain endpoint
    print("\n3. Triggering retraining...")
    try:
        response = requests.post(
            f"{base_url}/db/retrain",
            params={"min_samples": 10, "min_feedback_ratio": 0.1}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Status: {result['status']}")
            if result['status'] == 'success':
                print(f"   Model version: {result['result']['model_version']}")
                print(f"   Accuracy: {result['result']['metrics']['accuracy']:.3f}")
        else:
            print(f"   ⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  API not running: {e}")


def main():
    """Main test function."""
    
    print_section("Database Retraining Test")
    
    print("\nThis script will:")
    print("  1. Create sample predictions with feedback")
    print("  2. Check retraining status")
    print("  3. Export training data")
    print("  4. Retrain the model")
    print("  5. Test API endpoints")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Create sample data
    create_sample_predictions_with_feedback()
    
    # Step 2: Check status
    is_ready = test_retraining_status()
    
    if not is_ready:
        print("\n⚠️  Not enough data for retraining")
        print("   Create more predictions with feedback first")
        return
    
    # Step 3: Export data
    test_export_training_data()
    
    # Step 4: Retrain model
    test_model_retraining()
    
    # Step 5: Test API endpoints
    print("\n\nTo test API endpoints, start the API first:")
    print("  python run.py")
    print("\nThen run this section:")
    
    response = input("\nTest API endpoints now? (y/n): ")
    if response.lower() == 'y':
        test_api_endpoints()
    
    print_section("Test Complete")
    
    print("\n✅ Database retraining test completed successfully!")
    print("\nNext steps:")
    print("  1. Make predictions and submit feedback")
    print("  2. Check retraining status: GET /db/retraining/status")
    print("  3. Retrain model: POST /db/retrain")
    print("  4. Export data: POST /db/export_training_data")


if __name__ == "__main__":
    main()

"""Test model artifacts and retraining functionality.

Note: This test verifies that model artifacts exist and are valid.
"""
import os
import sys
from pathlib import Path
import pytest
import json

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.mark.unit
def test_model_artifacts_exist():
    """Test that required model artifacts exist in the models directory."""
    models_dir = ROOT / "models"
    
    # Check if models directory exists
    assert models_dir.exists(), "Models directory should exist"
    
    # Check for required files
    required_files = [
        "credit_risk_model.pkl",
        "scaler.pkl",
        "feature_names.json"
    ]
    
    for filename in required_files:
        filepath = models_dir / filename
        assert filepath.exists(), f"Required model file not found: {filename}"


@pytest.mark.unit
def test_feature_names_valid():
    """Test that feature_names.json is valid and contains expected features."""
    feature_names_path = ROOT / "models" / "feature_names.json"
    
    if not feature_names_path.exists():
        pytest.skip("feature_names.json not found")
    
    # Load and validate JSON
    with open(feature_names_path, 'r') as f:
        feature_names = json.load(f)
    
    # Should be a list
    assert isinstance(feature_names, list), "Feature names should be a list"
    
    # Should not be empty
    assert len(feature_names) > 0, "Feature names list should not be empty"
    
    # Should contain expected base features (after one-hot encoding)
    expected_features = [
        "person_age",
        "person_income",
        "person_emp_length",
        "loan_amnt",
        "loan_int_rate",
        "loan_percent_income",
        "cb_person_cred_hist_length"
    ]
    
    for feature in expected_features:
        assert feature in feature_names, f"Expected feature '{feature}' not found in feature names"


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.requires_data
def test_model_can_be_loaded():
    """Test that the saved model can be loaded successfully."""
    import joblib
    
    model_path = ROOT / "models" / "credit_risk_model.pkl"
    scaler_path = ROOT / "models" / "scaler.pkl"
    
    if not model_path.exists() or not scaler_path.exists():
        pytest.skip("Model files not found")
    
    # Try to load model
    model = joblib.load(model_path)
    assert model is not None, "Model should load successfully"
    
    # Try to load scaler
    scaler = joblib.load(scaler_path)
    assert scaler is not None, "Scaler should load successfully"
    
    # Verify model has expected attributes
    assert hasattr(model, 'predict'), "Model should have predict method"
    assert hasattr(model, 'predict_proba'), "Model should have predict_proba method"

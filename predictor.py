import joblib
import pandas as pd
import numpy as np
from typing import Dict, Union, Tuple
import os
from config import MODEL_PKL, SCALER_PKL, FEATURE_NAMES_PKL
import json
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CreditRiskPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.load_error = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the model and supporting files."""
        try:
            # Prefer loading the latest versioned artifacts from models/manifest.json if present
            manifest_path = os.path.join("models", "manifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as mf:
                        manifest = json.load(mf)
                    # manifest is a list of entries, pick the last (most recent)
                    if isinstance(manifest, list) and len(manifest) > 0:
                        latest = manifest[-1]
                        model_path = latest.get("model")
                        scaler_path = latest.get("scaler")
                        features_path = latest.get("features")
                        if model_path and os.path.exists(model_path):
                            self.model = joblib.load(model_path)
                        if scaler_path and os.path.exists(scaler_path):
                            self.scaler = joblib.load(scaler_path)
                        if features_path and os.path.exists(features_path):
                            with open(features_path, "r", encoding="utf-8") as f:
                                self.feature_names = json.load(f)
                except Exception:
                    # Fall back to legacy artifact names if manifest parsing/loading fails
                    pass

            # Fallback to legacy filenames from centralized config if anything missing
            if self.model is None:
                self.model = joblib.load(MODEL_PKL)
            if self.scaler is None:
                self.scaler = joblib.load(SCALER_PKL)
            if self.feature_names is None:
                # feature names may be stored as json or a pickle
                try:
                    with open(FEATURE_NAMES_PKL, "r", encoding="utf-8") as f:
                        self.feature_names = json.load(f)
                except Exception:
                    self.feature_names = joblib.load(FEATURE_NAMES_PKL)
        except Exception as e:
            self.load_error = e
            # Re-raise so callers (API/app) can decide how to handle load failures
            raise e

    def preprocess_features(self, input_dict: Dict[str, Union[float, str]]) -> pd.DataFrame:
        """
        Preprocess the input features for prediction.
        
        Args:
            input_dict: Dictionary containing the raw input features
            
        Returns:
            Preprocessed features as a DataFrame
        """
        # Build full feature dict with one-hot encoded categorical variables
        input_full = {col: input_dict.get(col, 0) for col in self.feature_names}
        df_input = pd.DataFrame([input_full])
        
        # Scale numeric features
        scaled = self.scaler.transform(df_input)
        return scaled

    def predict(self, input_dict: Dict[str, Union[float, str]], flag_threshold: float = 0.6) -> Tuple[str, float, int]:
        """
        Make a prediction and return the risk level, probability, and binary prediction.
        
        Args:
            input_dict: Dictionary containing the input features
            flag_threshold: Threshold for high risk classification
            
        Returns:
            Tuple containing (risk_level, probability, binary_prediction)
        """
        # Preprocess features
        scaled_features = self.preprocess_features(input_dict)
        
        # Make prediction
        pred = self.model.predict(scaled_features)[0]
        
        # Get probability of default (Class 1)
        try:
            # Get the raw probability array for the first sample
            raw_proba = self.model.predict_proba(scaled_features)[0] 
            
            # Check the size of the probability output
            if len(raw_proba) == 2:
                # Standard binary output: [P(Class 0), P(Class 1)]
                prob = raw_proba[1]
            elif len(raw_proba) == 1:
                # Single column output: [P(Class 1)]
                prob = raw_proba[0]
            else:
                # Fallback if prediction fails or is unexpected
                prob = float(pred)  # use raw prediction as probability-like value
            # Ensure native Python float for JSON friendliness
            prob = float(prob)
                
        except Exception as e:
            # fallback if predict_proba itself throws an error
            logger.warning("predict_proba failed; falling back to raw prediction. Error: %s", e)
            prob = float(pred)
        
        # Determine risk level
        if prob > flag_threshold:
            risk_level = "High Risk 🔴"
            risk_class = "risk-high"
        elif prob > 0.4:
            risk_level = "Borderline Risk 🟠"
            risk_class = "risk-borderline"
        else:
            risk_level = "Low Risk 🟢"
            risk_class = "risk-low"
        
        return risk_level, prob, int(pred)

    def get_shap_values(self, input_dict: Dict[str, Union[float, str]]):
        """
        Get SHAP values for the prediction.
        
        Args:
            input_dict: Dictionary containing the input features
            
        Returns:
            Tuple of (shap_values, expected_value, features_df)
        """
        import shap
        
        # Preprocess features
        scaled_features = self.preprocess_features(input_dict)
        df_input = pd.DataFrame([input_dict])
        
        # Calculate SHAP values
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(scaled_features)
        expected_value = explainer.expected_value
        
        return shap_values, expected_value, df_input
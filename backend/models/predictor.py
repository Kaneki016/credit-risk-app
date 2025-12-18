import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd

from backend.core.config import FEATURE_NAMES_PKL, MODEL_PKL, SCALER_PKL

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
            # Get the project root directory
            # This file is in backend/models/, so go up 2 levels to get project root
            from pathlib import Path
            script_dir = Path(__file__).parent
            project_root = script_dir.parent.parent  # backend/models -> backend -> project root
            
            # Prefer loading the latest versioned artifacts from models/manifest.json if present
            manifest_path = project_root / "models" / "manifest.json"
            if manifest_path.exists():
                try:
                    logger.info(f"Loading model from manifest: {manifest_path}")
                    with open(manifest_path, "r", encoding="utf-8") as mf:
                        manifest = json.load(mf)
                    # manifest is a list of entries, pick the last (most recent)
                    if isinstance(manifest, list) and len(manifest) > 0:
                        latest = manifest[-1]
                        model_path = latest.get("model")
                        scaler_path = latest.get("scaler")
                        features_path = latest.get("features")
                        
                        # Normalize paths (handle both forward and backslashes, relative and absolute)
                        if model_path:
                            if not os.path.isabs(model_path):
                                model_path = os.path.normpath(os.path.join(project_root, model_path))
                            else:
                                model_path = os.path.normpath(model_path)
                            if os.path.exists(model_path):
                                logger.info(f"Loading model from: {model_path}")
                                self.model = joblib.load(model_path)
                            else:
                                logger.warning(f"Model path from manifest does not exist: {model_path}")
                        if scaler_path:
                            if not os.path.isabs(scaler_path):
                                scaler_path = os.path.normpath(os.path.join(project_root, scaler_path))
                            else:
                                scaler_path = os.path.normpath(scaler_path)
                            if os.path.exists(scaler_path):
                                logger.info(f"Loading scaler from: {scaler_path}")
                                self.scaler = joblib.load(scaler_path)
                            else:
                                logger.warning(f"Scaler path from manifest does not exist: {scaler_path}")
                        if features_path:
                            if not os.path.isabs(features_path):
                                features_path = os.path.normpath(os.path.join(project_root, features_path))
                            else:
                                features_path = os.path.normpath(features_path)
                            if os.path.exists(features_path):
                                logger.info(f"Loading feature names from: {features_path}")
                                with open(features_path, "r", encoding="utf-8") as f:
                                    self.feature_names = json.load(f)
                            else:
                                logger.warning(f"Features path from manifest does not exist: {features_path}")
                except Exception as e:
                    # Log the error but continue to fallback
                    logger.warning(f"Failed to load from manifest, falling back to legacy paths. Error: {e}")

            # Fallback to legacy filenames from centralized config if anything missing
            if self.model is None:
                model_path = Path(MODEL_PKL)
                logger.info(f"Loading model from fallback path: {model_path}")
                if not model_path.exists():
                    raise FileNotFoundError(f"Model file not found at: {model_path}")
                self.model = joblib.load(str(model_path))
            if self.scaler is None:
                scaler_path = Path(SCALER_PKL)
                logger.info(f"Loading scaler from fallback path: {scaler_path}")
                if not scaler_path.exists():
                    raise FileNotFoundError(f"Scaler file not found at: {scaler_path}")
                self.scaler = joblib.load(str(scaler_path))
            if self.feature_names is None:
                features_path = Path(FEATURE_NAMES_PKL)
                logger.info(f"Loading feature names from fallback path: {features_path}")
                if not features_path.exists():
                    raise FileNotFoundError(f"Feature names file not found at: {features_path}")
                # feature names may be stored as json or a pickle
                try:
                    with open(str(features_path), "r", encoding="utf-8") as f:
                        self.feature_names = json.load(f)
                except Exception:
                    self.feature_names = joblib.load(str(features_path))
            
            # Verify all components loaded successfully
            if self.model is None or self.scaler is None or self.feature_names is None:
                missing = []
                if self.model is None:
                    missing.append("model")
                if self.scaler is None:
                    missing.append("scaler")
                if self.feature_names is None:
                    missing.append("feature_names")
                raise ValueError(f"Failed to load required components: {', '.join(missing)}")
            
            logger.info("Model, scaler, and feature names loaded successfully")
        except Exception as e:
            self.load_error = e
            logger.error(f"Model loading failed: {e}", exc_info=True)
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
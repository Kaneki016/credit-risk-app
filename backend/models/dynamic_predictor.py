# dynamic_predictor.py
"""
Enhanced predictor with dynamic input handling.
Wraps the original CreditRiskPredictor with flexible input processing.
"""

import logging
import os
from typing import Any, Dict, Optional, Tuple

from backend.models.predictor import CreditRiskPredictor
from backend.services.imputation import DynamicFeatureMapper, FeatureImputer

logger = logging.getLogger(__name__)


class DynamicCreditRiskPredictor:
    """
    Wrapper around CreditRiskPredictor that handles dynamic inputs.
    Automatically imputes missing values and adapts to different input formats.
    """
    
    def __init__(self, 
                 stats_path: Optional[str] = None,
                 historical_data_path: Optional[str] = None):
        """
        Initialize the dynamic predictor.
        
        Args:
            stats_path: Path to feature statistics JSON
            historical_data_path: Path to historical data CSV for imputation
        """
        # Initialize the core predictor
        self.predictor = CreditRiskPredictor()
        
        # Set up paths
        if stats_path is None:
            stats_path = os.path.join("models", "feature_statistics.json")
        if historical_data_path is None:
            # Try common locations
            for path in ["data/credit_risk_dataset.csv", "credit_risk_dataset.csv"]:
                if os.path.exists(path):
                    historical_data_path = path
                    break
        
        # Initialize imputer and mapper
        self.imputer = FeatureImputer(stats_path, historical_data_path)
        self.mapper = DynamicFeatureMapper(self.predictor.feature_names)
        
        logger.info("DynamicCreditRiskPredictor initialized successfully")
    
    def predict(self, 
                input_data: Dict[str, Any], 
                flag_threshold: float = 0.6,
                return_imputation_log: bool = False) -> Tuple:
        """
        Make a prediction with dynamic input handling.
        
        Args:
            input_data: Dictionary with partial or complete loan application data
            flag_threshold: Threshold for high risk classification
            return_imputation_log: Whether to return imputation details
            
        Returns:
            Tuple of (risk_level, probability, binary_prediction, [imputation_log])
        """
        # Step 1: Impute missing values
        imputed_data, imputation_log = self.imputer.impute(input_data)
        
        # Step 2: Map to model features (one-hot encoding)
        mapped_features = self.mapper.map_to_model_features(imputed_data)
        
        # Step 3: Ensure all expected features are present
        complete_features = self.mapper.validate_and_fill(mapped_features)
        
        # Step 4: Make prediction using the core predictor
        risk_level, prob, pred = self.predictor.predict(complete_features, flag_threshold)
        
        if return_imputation_log:
            return risk_level, prob, pred, imputation_log, imputed_data
        else:
            return risk_level, prob, pred
    
    def get_shap_values(self, input_data: Dict[str, Any]):
        """
        Get SHAP values with dynamic input handling.
        
        Args:
            input_data: Dictionary with partial or complete loan application data
            
        Returns:
            Tuple of (shap_values, expected_value, features_df, imputed_data)
        """
        # Impute and map features
        imputed_data, _ = self.imputer.impute(input_data)
        mapped_features = self.mapper.map_to_model_features(imputed_data)
        complete_features = self.mapper.validate_and_fill(mapped_features)
        
        # Get SHAP values
        shap_values, expected_value, df_features = self.predictor.get_shap_values(complete_features)
        
        return shap_values, expected_value, df_features, imputed_data
    
    def get_feature_importance(self, input_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Get feature importance scores for the prediction.
        
        Args:
            input_data: Dictionary with loan application data
            
        Returns:
            Dictionary mapping feature names to importance scores
        """
        shap_values, _, df_features, _ = self.get_shap_values(input_data)
        
        # Handle binary classification SHAP values
        if isinstance(shap_values, list):
            shap_data = shap_values[1]  # Positive class
        else:
            shap_data = shap_values
        
        # Extract feature importance
        try:
            row = shap_data.tolist()[0]
        except Exception:
            import numpy as np
            row = np.asarray(shap_data).ravel().tolist()
        
        feature_names = df_features.columns.tolist()
        importance = {k: float(v) for k, v in zip(feature_names, row)}
        
        return importance
    
    def validate_input(self, input_data: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate input data and return validation status and warnings.
        
        Args:
            input_data: Dictionary with loan application data
            
        Returns:
            Tuple of (is_valid, warnings_list)
        """
        warnings = []
        
        # Check for completely empty input
        if not input_data or all(v is None for v in input_data.values()):
            warnings.append("No input data provided - all values will be imputed")
            return False, warnings
        
        # Check for critical missing fields
        critical_fields = ['person_income', 'loan_amnt']
        missing_critical = [f for f in critical_fields if input_data.get(f) is None]
        
        if missing_critical:
            warnings.append(f"Critical fields missing (will be imputed): {', '.join(missing_critical)}")
        
        # Check for invalid ranges
        if input_data.get('person_age') is not None:
            if input_data['person_age'] < 18 or input_data['person_age'] > 100:
                warnings.append(f"person_age ({input_data['person_age']}) outside valid range [18, 100]")
        
        if input_data.get('loan_percent_income') is not None:
            if input_data['loan_percent_income'] > 1:
                warnings.append(f"loan_percent_income ({input_data['loan_percent_income']}) > 1 (should be 0-1)")
        
        # Check for negative values
        numeric_fields = ['person_income', 'person_emp_length', 'loan_amnt', 
                         'loan_int_rate', 'cb_person_cred_hist_length']
        for field in numeric_fields:
            if input_data.get(field) is not None and input_data[field] < 0:
                warnings.append(f"{field} is negative: {input_data[field]}")
        
        is_valid = len(warnings) == 0 or all('will be imputed' in w for w in warnings)
        return is_valid, warnings

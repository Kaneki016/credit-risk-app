# dynamic_schema.py
"""
Dynamic input schema system that adapts to incoming data.
Supports flexible inputs, missing value imputation, and historical data inference.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import json
import os
import logging

logger = logging.getLogger(__name__)


class DynamicLoanApplication(BaseModel):
    """
    Flexible loan application schema that accepts partial or complete data.
    Missing fields will be imputed using defaults, historical data, or inference.
    """

    # Core numeric features (all optional with smart defaults)
    person_age: Optional[int] = Field(None, description="Age of the borrower (years)", ge=18, le=100)
    person_income: Optional[float] = Field(None, description="Annual income in USD", ge=0)
    person_emp_length: Optional[float] = Field(None, description="Employment length in months", ge=0)
    loan_amnt: Optional[float] = Field(None, description="Loan amount requested in USD", ge=0)
    loan_int_rate: Optional[float] = Field(None, description="Loan interest rate as percentage", ge=0, le=100)
    loan_percent_income: Optional[float] = Field(None, description="Loan amount as percentage of income", ge=0, le=1)
    cb_person_cred_hist_length: Optional[float] = Field(None, description="Credit history length in years", ge=0)

    # Categorical fields (optional)
    home_ownership: Optional[str] = Field(None, description="Home ownership status (RENT, OWN, MORTGAGE, OTHER)")
    loan_intent: Optional[str] = Field(None, description="Purpose of the loan")
    loan_grade: Optional[str] = Field(None, description="Loan grade assigned (A-G)")
    default_on_file: Optional[str] = Field(None, description="Previous default on file (Y/N)")

    # Allow extra fields for future extensibility
    model_config = {
        "extra": "allow",
        "json_schema_extra": {
            "examples": [
                {"person_age": 30, "person_income": 50000.0, "loan_amnt": 10000.0, "loan_intent": "PERSONAL"},
                {"person_income": 75000.0, "loan_amnt": 15000.0, "loan_grade": "B"},
            ]
        },
    }

    @field_validator("home_ownership", "loan_intent", "loan_grade", "default_on_file", mode="before")
    @classmethod
    def uppercase_strings(cls, v):
        """Normalize categorical values to uppercase."""
        if v is not None and isinstance(v, str):
            return v.upper()
        return v


class FeatureImputer:
    """
    Intelligent feature imputation using multiple strategies:
    1. Historical data statistics
    2. Derived calculations (e.g., loan_percent_income from loan_amnt and income)
    3. Safe defaults based on domain knowledge
    """

    def __init__(self, stats_path: Optional[str] = None, historical_data_path: Optional[str] = None):
        self.stats = {}
        self.historical_stats = {}
        self.categorical_modes = {}

        # Load feature statistics if available
        if stats_path and os.path.exists(stats_path):
            try:
                with open(stats_path, "r", encoding="utf-8") as f:
                    self.stats = json.load(f)
                logger.info(f"Loaded feature statistics from {stats_path}")
            except Exception as e:
                logger.warning(f"Could not load feature statistics: {e}")

        # Load historical data for more sophisticated imputation
        if historical_data_path and os.path.exists(historical_data_path):
            try:
                df = pd.read_csv(historical_data_path)
                self._compute_historical_stats(df)
                logger.info(f"Loaded historical data from {historical_data_path}")
            except Exception as e:
                logger.warning(f"Could not load historical data: {e}")

    def _compute_historical_stats(self, df: pd.DataFrame):
        """Compute statistics from historical data."""
        # Numeric features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in df.columns:
                self.historical_stats[col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "q25": float(df[col].quantile(0.25)),
                    "q75": float(df[col].quantile(0.75)),
                }

        # Categorical features - find mode
        categorical_cols = df.select_dtypes(include=["object"]).columns
        for col in categorical_cols:
            if col in df.columns:
                mode_val = df[col].mode()
                if len(mode_val) > 0:
                    self.categorical_modes[col] = str(mode_val[0]).upper()

    def impute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Impute missing values using intelligent strategies.

        Strategy priority:
        1. Derive from other fields if possible
        2. Use historical median/mode
        3. Use safe domain-specific defaults
        """
        imputed = data.copy()
        imputation_log = []

        # Derive loan_percent_income if missing but loan_amnt and person_income are present
        if imputed.get("loan_percent_income") is None:
            if imputed.get("loan_amnt") is not None and imputed.get("person_income") is not None:
                if imputed["person_income"] > 0:
                    imputed["loan_percent_income"] = imputed["loan_amnt"] / imputed["person_income"]
                    imputation_log.append("loan_percent_income: derived from loan_amnt/person_income")

        # Impute numeric features
        numeric_defaults = {
            "person_age": 35,  # Median working age
            "person_income": 50000,  # Median income
            "person_emp_length": 24,  # 2 years employment
            "loan_amnt": 10000,  # Typical loan amount
            "loan_int_rate": 10.0,  # Average interest rate
            "loan_percent_income": 0.25,  # Conservative 25%
            "cb_person_cred_hist_length": 5,  # 5 years credit history
        }

        for field, default_val in numeric_defaults.items():
            if imputed.get(field) is None:
                # Try historical median first
                if field in self.historical_stats:
                    imputed[field] = self.historical_stats[field]["median"]
                    imputation_log.append(f"{field}: historical median")
                # Try feature stats median
                elif field in self.stats and "mean" in self.stats[field]:
                    imputed[field] = self.stats[field]["mean"]
                    imputation_log.append(f"{field}: training mean")
                # Use safe default
                else:
                    imputed[field] = default_val
                    imputation_log.append(f"{field}: safe default")

        # Impute categorical features
        categorical_defaults = {
            "home_ownership": "RENT",
            "loan_intent": "PERSONAL",
            "loan_grade": "C",  # Middle grade
            "default_on_file": "N",  # Assume no default
        }

        for field, default_val in categorical_defaults.items():
            if imputed.get(field) is None:
                # Try historical mode first
                if field in self.categorical_modes:
                    imputed[field] = self.categorical_modes[field]
                    imputation_log.append(f"{field}: historical mode")
                else:
                    imputed[field] = default_val
                    imputation_log.append(f"{field}: safe default")

        # Log imputation actions
        if imputation_log:
            logger.info(f"Imputed {len(imputation_log)} fields: {', '.join(imputation_log)}")

        return imputed, imputation_log


class DynamicFeatureMapper:
    """
    Maps dynamic input to model-expected features.
    Handles different feature sets across model versions.
    """

    def __init__(self, expected_features: List[str]):
        self.expected_features = expected_features
        self.numeric_features = [
            "person_age",
            "person_income",
            "person_emp_length",
            "loan_amnt",
            "loan_int_rate",
            "loan_percent_income",
            "cb_person_cred_hist_length",
        ]
        self.categorical_features = {
            "person_home_ownership": ["RENT", "OWN", "MORTGAGE", "OTHER"],
            "loan_intent": ["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"],
            "loan_grade": ["A", "B", "C", "D", "E", "F", "G"],
            "cb_person_default_on_file": ["Y", "N"],
        }

    def map_to_model_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert dynamic input to model-expected one-hot encoded format.
        """
        mapped = {}

        # Add numeric features directly
        for feat in self.numeric_features:
            if feat in data:
                mapped[feat] = data[feat]

        # One-hot encode categorical features
        # home_ownership -> person_home_ownership_RENT, etc.
        if "home_ownership" in data and data["home_ownership"]:
            mapped[f"person_home_ownership_{data['home_ownership']}"] = 1

        if "loan_intent" in data and data["loan_intent"]:
            mapped[f"loan_intent_{data['loan_intent']}"] = 1

        if "loan_grade" in data and data["loan_grade"]:
            mapped[f"loan_grade_{data['loan_grade']}"] = 1

        if "default_on_file" in data and data["default_on_file"]:
            mapped[f"cb_person_default_on_file_{data['default_on_file']}"] = 1

        return mapped

    def validate_and_fill(self, mapped_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure all expected features are present, filling missing ones with 0.
        """
        complete_features = {feat: mapped_features.get(feat, 0) for feat in self.expected_features}
        return complete_features

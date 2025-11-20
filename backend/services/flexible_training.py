"""
Flexible Model Training Service
Allows training with different CSV structures and column mappings.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class FlexibleModelTrainer:
    """
    Train credit risk models with flexible column mappings.
    Supports different CSV structures and feature sets.
    """

    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)

        # Default column mappings (can be customized)
        self.default_mappings = {
            "target": ["loan_status", "default", "target", "label", "outcome"],
            "numeric_features": [
                "person_age",
                "person_income",
                "person_emp_length",
                "loan_amnt",
                "loan_int_rate",
                "loan_percent_income",
                "cb_person_cred_hist_length",
            ],
            "categorical_features": ["person_home_ownership", "loan_intent", "loan_grade", "cb_person_default_on_file"],
        }

    def detect_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Automatically detect column types and target variable.

        Args:
            df: Input dataframe

        Returns:
            Dictionary with detected columns
        """
        columns = df.columns.tolist()

        # Detect target column
        target_col = None
        for possible_target in self.default_mappings["target"]:
            if possible_target in columns:
                target_col = possible_target
                break

        if not target_col:
            # Try to find binary column
            for col in columns:
                if df[col].nunique() == 2:
                    target_col = col
                    logger.info(f"Auto-detected target column: {col}")
                    break

        if not target_col:
            raise ValueError(f"Could not detect target column. Please specify one of: " f"{self.default_mappings['target']}")

        # Separate features from target
        feature_columns = [col for col in columns if col != target_col]

        # Detect numeric vs categorical
        numeric_features = []
        categorical_features = []

        for col in feature_columns:
            if df[col].dtype in ["int64", "float64"]:
                # Check if it's actually categorical (few unique values)
                if df[col].nunique() < 10 and df[col].nunique() / len(df) < 0.05:
                    categorical_features.append(col)
                else:
                    numeric_features.append(col)
            else:
                categorical_features.append(col)

        logger.info(f"Detected {len(numeric_features)} numeric and {len(categorical_features)} categorical features")

        return {
            "target": target_col,
            "numeric_features": numeric_features,
            "categorical_features": categorical_features,
            "all_features": feature_columns,
        }

    def preprocess_data(
        self, df: pd.DataFrame, column_mapping: Optional[Dict[str, Any]] = None
    ) -> Tuple[pd.DataFrame, pd.Series, Dict[str, Any]]:
        """
        Preprocess data with flexible column handling.

        Args:
            df: Input dataframe
            column_mapping: Optional custom column mapping

        Returns:
            Tuple of (features_df, target_series, preprocessing_info)
        """
        # Auto-detect columns if not provided
        if column_mapping is None:
            column_mapping = self.detect_columns(df)

        target_col = column_mapping["target"]
        numeric_features = column_mapping["numeric_features"]
        categorical_features = column_mapping["categorical_features"]

        # Extract target
        y = df[target_col].copy()

        # Convert target to binary if needed
        if y.dtype == "object":
            # Map common values
            mapping = {
                "default": 1,
                "no_default": 0,
                "yes": 1,
                "no": 0,
                "y": 1,
                "n": 0,
                "1": 1,
                "0": 0,
                "true": 1,
                "false": 0,
                "approved": 0,
                "rejected": 1,
                "good": 0,
                "bad": 1,
            }
            y = y.str.lower().map(mapping)

            if y.isna().any():
                logger.warning(f"Some target values could not be mapped. Unique values: {df[target_col].unique()}")
                y = y.fillna(0)

        y = y.astype(int)

        # Process features
        X = pd.DataFrame()

        # Add numeric features
        for col in numeric_features:
            if col in df.columns:
                X[col] = pd.to_numeric(df[col], errors="coerce").fillna(df[col].median())

        # One-hot encode categorical features
        for col in categorical_features:
            if col in df.columns:
                # Convert to string and handle missing
                df[col] = df[col].fillna("UNKNOWN").astype(str)

                # One-hot encode
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=False)
                X = pd.concat([X, dummies], axis=1)

        preprocessing_info = {
            "target_column": target_col,
            "numeric_features": numeric_features,
            "categorical_features": categorical_features,
            "feature_names": X.columns.tolist(),
            "n_features": len(X.columns),
            "n_samples": len(X),
        }

        logger.info(f"Preprocessed data: {len(X)} samples, {len(X.columns)} features")

        return X, y, preprocessing_info

    def train_model(
        self,
        csv_path: str,
        column_mapping: Optional[Dict[str, Any]] = None,
        test_size: float = 0.2,
        random_state: int = 42,
        model_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Train a model from CSV file with flexible column handling.

        Args:
            csv_path: Path to CSV file
            column_mapping: Optional custom column mapping
            test_size: Proportion of data for testing
            random_state: Random seed
            model_params: Optional XGBoost parameters

        Returns:
            Training results and metrics
        """
        logger.info(f"Starting flexible model training from {csv_path}")

        # Load data
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")

        # Preprocess
        X, y, preprocessing_info = self.preprocess_data(df, column_mapping)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model
        if model_params is None:
            model_params = {
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "random_state": random_state,
                "eval_metric": "logloss",
            }

        logger.info("Training XGBoost model...")
        model = XGBClassifier(**model_params)
        model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
            "auc_roc": float(roc_auc_score(y_test, y_pred_proba)),
        }

        logger.info(f"Model trained. Accuracy: {metrics['accuracy']:.4f}, AUC-ROC: {metrics['auc_roc']:.4f}")

        # Save model
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        model_filename = f"credit_risk_model_v{timestamp}.pkl"
        scaler_filename = f"scaler_v{timestamp}.pkl"
        features_filename = f"feature_names_v{timestamp}.json"
        preprocessing_filename = f"preprocessing_info_v{timestamp}.json"

        model_path = self.models_dir / model_filename
        scaler_path = self.models_dir / scaler_filename
        features_path = self.models_dir / features_filename
        preprocessing_path = self.models_dir / preprocessing_filename

        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)

        with open(features_path, "w") as f:
            json.dump(preprocessing_info["feature_names"], f, indent=2)

        with open(preprocessing_path, "w") as f:
            json.dump(preprocessing_info, f, indent=2)

        # Update manifest
        manifest_path = self.models_dir / "manifest.json"
        manifest = {
            "model_path": str(model_path),
            "scaler_path": str(scaler_path),
            "feature_names_path": str(features_path),
            "preprocessing_info_path": str(preprocessing_path),
            "timestamp": timestamp,
            "metrics": metrics,
            "preprocessing_info": preprocessing_info,
            "training_info": {
                "csv_path": csv_path,
                "n_samples": len(df),
                "n_train": len(X_train),
                "n_test": len(X_test),
                "test_size": test_size,
                "model_params": model_params,
            },
        }

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Model saved to {model_path}")
        logger.info(f"Manifest updated at {manifest_path}")

        return {
            "status": "success",
            "model_path": str(model_path),
            "metrics": metrics,
            "preprocessing_info": preprocessing_info,
            "training_info": manifest["training_info"],
        }

    def train_from_dataframe(
        self,
        df: pd.DataFrame,
        column_mapping: Optional[Dict[str, Any]] = None,
        test_size: float = 0.2,
        random_state: int = 42,
        model_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Train a model directly from a DataFrame.

        Args:
            df: Input dataframe
            column_mapping: Optional custom column mapping
            test_size: Proportion of data for testing
            random_state: Random seed
            model_params: Optional XGBoost parameters

        Returns:
            Training results and metrics
        """
        logger.info(f"Starting flexible model training from DataFrame")
        logger.info(f"Data shape: {df.shape}")

        # Save to temporary CSV and use train_model
        temp_csv = self.models_dir / "temp_training_data.csv"
        df.to_csv(temp_csv, index=False)

        result = self.train_model(
            str(temp_csv),
            column_mapping=column_mapping,
            test_size=test_size,
            random_state=random_state,
            model_params=model_params,
        )

        # Clean up temp file
        temp_csv.unlink()

        return result

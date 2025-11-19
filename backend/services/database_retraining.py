# backend/services/database_retraining.py
"""
Model retraining using data from database.
Enables continuous learning from predictions and feedback.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import json
import os

from backend.database import SessionLocal, crud
from backend.database.models import Prediction, ModelMetrics

logger = logging.getLogger(__name__)


class DatabaseRetrainer:
    """
    Retrain model using data from database.
    """
    
    def __init__(self, min_samples: int = 100, min_feedback_ratio: float = 0.1):
        """
        Initialize retrainer.
        
        Args:
            min_samples: Minimum number of samples needed for retraining
            min_feedback_ratio: Minimum ratio of samples with feedback
        """
        self.min_samples = min_samples
        self.min_feedback_ratio = min_feedback_ratio
        self.models_dir = "models"
        self.data_dir = "data"
        
        # Ensure directories exist
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
    
    def check_retraining_readiness(self, db: Session) -> Dict[str, Any]:
        """
        Check if enough data is available for retraining.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with readiness status and statistics
        """
        # Get all predictions
        all_predictions = crud.get_predictions(db, limit=10000)
        total_predictions = len(all_predictions)
        
        # Get predictions with feedback
        predictions_with_feedback = [
            p for p in all_predictions 
            if p.actual_outcome is not None
        ]
        feedback_count = len(predictions_with_feedback)
        
        # Calculate feedback ratio
        feedback_ratio = feedback_count / total_predictions if total_predictions > 0 else 0
        
        # Check readiness
        is_ready = (
            total_predictions >= self.min_samples and
            feedback_ratio >= self.min_feedback_ratio
        )
        
        return {
            "is_ready": is_ready,
            "total_predictions": total_predictions,
            "feedback_count": feedback_count,
            "feedback_ratio": feedback_ratio,
            "min_samples_required": self.min_samples,
            "min_feedback_ratio_required": self.min_feedback_ratio,
            "samples_needed": max(0, self.min_samples - total_predictions),
            "feedback_needed": max(0, int(self.min_samples * self.min_feedback_ratio) - feedback_count)
        }
    
    def extract_training_data(self, db: Session) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Extract training data from database predictions with feedback.
        
        Args:
            db: Database session
            
        Returns:
            Tuple of (features_df, labels_series)
        """
        # Get predictions with feedback
        predictions = crud.get_predictions(db, limit=10000)
        predictions_with_feedback = [
            p for p in predictions 
            if p.actual_outcome is not None and p.input_features
        ]
        
        if not predictions_with_feedback:
            raise ValueError("No predictions with feedback found in database")
        
        logger.info(f"Extracting training data from {len(predictions_with_feedback)} predictions")
        
        # Convert to DataFrame
        data_records = []
        labels = []
        
        for pred in predictions_with_feedback:
            try:
                # Get input features
                features = pred.input_features
                
                # Add to records
                data_records.append(features)
                labels.append(pred.actual_outcome)
                
            except Exception as e:
                logger.warning(f"Failed to process prediction {pred.id}: {e}")
                continue
        
        # Create DataFrame
        df = pd.DataFrame(data_records)
        y = pd.Series(labels, name='loan_status')
        
        logger.info(f"Extracted {len(df)} samples with {len(df.columns)} features")
        logger.info(f"Feature columns: {list(df.columns)}")
        logger.info(f"Data types: {df.dtypes.to_dict()}")
        
        return df, y
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for training (handle categorical variables).
        
        Args:
            df: Raw features DataFrame
            
        Returns:
            Processed features DataFrame
        """
        df_processed = df.copy()
        
        # Map column names to match expected format
        column_mapping = {
            'person_home_ownership': 'home_ownership',
            'cb_person_default_on_file': 'default_on_file'
        }
        
        # Rename columns if needed
        for old_name, new_name in column_mapping.items():
            if old_name in df_processed.columns and new_name not in df_processed.columns:
                df_processed[new_name] = df_processed[old_name]
                df_processed = df_processed.drop(columns=[old_name])
        
        # Handle categorical variables
        categorical_cols = {
            'home_ownership': ['RENT', 'OWN', 'MORTGAGE', 'OTHER'],
            'loan_intent': ['PERSONAL', 'EDUCATION', 'MEDICAL', 'VENTURE', 
                           'HOMEIMPROVEMENT', 'DEBTCONSOLIDATION'],
            'loan_grade': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
            'default_on_file': ['Y', 'N']
        }
        
        # One-hot encode categorical variables
        for col, categories in categorical_cols.items():
            if col in df_processed.columns:
                # Convert to string and uppercase
                df_processed[col] = df_processed[col].astype(str).str.upper()
                
                # Create one-hot encoded columns
                for category in categories:
                    new_col = f"{col}_{category}"
                    df_processed[new_col] = (df_processed[col] == category).astype(int)
                
                # Drop original column
                df_processed = df_processed.drop(columns=[col])
        
        # Ensure all columns are numeric
        for col in df_processed.columns:
            if df_processed[col].dtype == 'object':
                try:
                    df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
                except Exception:
                    logger.warning(f"Could not convert column {col} to numeric, dropping it")
                    df_processed = df_processed.drop(columns=[col])
        
        # Fill any NaN values with 0
        df_processed = df_processed.fillna(0)
        
        return df_processed
    
    def retrain_model(
        self, 
        db: Session,
        test_size: float = 0.2,
        save_model: bool = True
    ) -> Dict[str, Any]:
        """
        Retrain model using database data.
        
        Args:
            db: Database session
            test_size: Proportion of data for testing
            save_model: Whether to save the retrained model
            
        Returns:
            Dictionary with retraining results and metrics
        """
        logger.info("Starting model retraining from database data")
        
        # Check readiness
        readiness = self.check_retraining_readiness(db)
        if not readiness['is_ready']:
            raise ValueError(
                f"Not enough data for retraining. "
                f"Need {readiness['samples_needed']} more samples and "
                f"{readiness['feedback_needed']} more feedback entries."
            )
        
        # Extract training data
        X, y = self.extract_training_data(db)
        
        # Prepare features
        X_processed = self.prepare_features(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y, test_size=test_size, random_state=42, stratify=y
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        # Train model using existing training function
        from xgboost import XGBClassifier
        from sklearn.preprocessing import StandardScaler
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train XGBoost model
        model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss'
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
            'auc_roc': float(roc_auc_score(y_test, y_pred_proba)),
            'total_predictions': len(y_pred),
            'correct_predictions': int((y_pred == y_test).sum()),
            'false_positives': int(((y_pred == 1) & (y_test == 0)).sum()),
            'false_negatives': int(((y_pred == 0) & (y_test == 1)).sum())
        }
        
        logger.info(f"Model metrics: Accuracy={metrics['accuracy']:.3f}, "
                   f"AUC-ROC={metrics['auc_roc']:.3f}")
        
        # Save model if requested
        if save_model:
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
            version = f"v{timestamp}"
            
            model_path = os.path.join(self.models_dir, f"credit_risk_model_{version}.pkl")
            scaler_path = os.path.join(self.models_dir, f"scaler_{version}.pkl")
            features_path = os.path.join(self.models_dir, f"feature_names_{version}.json")
            
            # Save model, scaler, and feature names
            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)
            
            with open(features_path, 'w') as f:
                json.dump(list(X_processed.columns), f)
            
            logger.info(f"Model saved: {model_path}")
            
            # Update manifest
            self._update_manifest(version, model_path, scaler_path, features_path, metrics)
            
            # Save metrics to database
            self._save_metrics_to_db(db, metrics, version)
        
        return {
            'status': 'success',
            'metrics': metrics,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'features_count': len(X_processed.columns),
            'model_version': version if save_model else None,
            'timestamp': datetime.now().isoformat()
        }
    
    def _update_manifest(
        self, 
        version: str, 
        model_path: str, 
        scaler_path: str, 
        features_path: str,
        metrics: Dict[str, Any]
    ):
        """Update model manifest file."""
        manifest_path = os.path.join(self.models_dir, "manifest.json")
        
        # Load existing manifest
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        else:
            manifest = []
        
        # Add new entry
        manifest.append({
            'version': version,
            'model': model_path,
            'scaler': scaler_path,
            'features': features_path,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat(),
            'source': 'database_retraining'
        })
        
        # Save manifest
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Manifest updated with version {version}")
    
    def _save_metrics_to_db(self, db: Session, metrics: Dict[str, Any], version: str):
        """Save model metrics to database."""
        try:
            metrics_data = {
                'model_type': 'xgboost',
                'model_version': version,
                'accuracy': metrics['accuracy'],
                'precision': metrics['precision'],
                'recall': metrics['recall'],
                'f1_score': metrics['f1_score'],
                'auc_roc': metrics['auc_roc'],
                'total_predictions': metrics['total_predictions'],
                'correct_predictions': metrics['correct_predictions'],
                'false_positives': metrics['false_positives'],
                'false_negatives': metrics['false_negatives'],
                'notes': f'Retrained from database data. Source: database_retraining'
            }
            
            crud.create_model_metrics(db, metrics_data)
            logger.info("Metrics saved to database")
            
        except Exception as e:
            logger.error(f"Failed to save metrics to database: {e}")
    
    def export_training_data(self, db: Session, output_path: Optional[str] = None) -> str:
        """
        Export training data from database to CSV file.
        
        Args:
            db: Database session
            output_path: Optional output file path
            
        Returns:
            Path to exported file
        """
        # Extract data
        X, y = self.extract_training_data(db)
        
        # Combine features and labels
        df = X.copy()
        df['loan_status'] = y
        
        # Set output path
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.data_dir, f"training_data_{timestamp}.csv")
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Training data exported to {output_path}")
        
        return output_path


def retrain_from_database(
    min_samples: int = 100,
    min_feedback_ratio: float = 0.1,
    test_size: float = 0.2
) -> Dict[str, Any]:
    """
    Convenience function to retrain model from database.
    
    Args:
        min_samples: Minimum samples required
        min_feedback_ratio: Minimum feedback ratio required
        test_size: Test set proportion
        
    Returns:
        Retraining results
    """
    db = SessionLocal()
    try:
        retrainer = DatabaseRetrainer(min_samples, min_feedback_ratio)
        result = retrainer.retrain_model(db, test_size=test_size)
        return result
    finally:
        db.close()


def check_retraining_status() -> Dict[str, Any]:
    """
    Check if model can be retrained from database.
    
    Returns:
        Status information
    """
    db = SessionLocal()
    try:
        retrainer = DatabaseRetrainer()
        return retrainer.check_retraining_readiness(db)
    finally:
        db.close()

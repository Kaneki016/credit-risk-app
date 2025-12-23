"""
Train XGBoost model for credit risk.

This script trains an XGBoost classifier for credit risk prediction.
It handles data preprocessing, model training, and saves the trained model artifacts.

Fixes applied:
- Split the dataset before fitting the scaler to avoid data leakage.
- Save the scaler fitted on training data and the full feature list.
"""

import json
import os
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

# Get project root (3 levels up from this file: backend/models/training.py -> project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"

# Load dataset
dataset_path = DATA_DIR / "credit_risk_dataset.csv"
if not dataset_path.exists():
    raise FileNotFoundError(f"Dataset not found at {dataset_path}. Please ensure the data file exists.")

df = pd.read_csv(dataset_path)

# Target variable
y = df["loan_status"]
X = df.drop(columns=["loan_status"])

# One-hot encode categorical features
X = pd.get_dummies(X, drop_first=True)

# Split dataset (do this before scaling to avoid data leakage)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale numeric features (fit scaler only on training data)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = model.predict(X_test_scaled)
print(classification_report(y_test, y_pred))
print("AUC:", roc_auc_score(y_test, model.predict_proba(X_test_scaled)[:, 1]))

# Save model and metadata into the canonical `models/` directory
MODELS_DIR.mkdir(exist_ok=True)
joblib.dump(model, MODELS_DIR / "credit_risk_model.pkl")
joblib.dump(scaler, MODELS_DIR / "scaler.pkl")

# Persist the full feature list (from the encoded dataframe) as JSON for consistency
with open(MODELS_DIR / "feature_names.json", "w", encoding="utf-8") as f:
	json.dump(X.columns.tolist(), f)

print(f"\n✅ Model training complete!")
print(f"   Model saved to: {MODELS_DIR / 'credit_risk_model.pkl'}")
print(f"   Scaler saved to: {MODELS_DIR / 'scaler.pkl'}")
print(f"   Features saved to: {MODELS_DIR / 'feature_names.json'}")

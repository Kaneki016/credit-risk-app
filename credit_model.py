# credit_model.py
import os
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score
import joblib

"""
Train XGBoost model for credit risk.

Fixes applied:
- Split the dataset before fitting the scaler to avoid data leakage.
- Save the scaler fitted on training data and the full feature list.
"""

# Load dataset
df = pd.read_csv("credit_risk_dataset.csv")

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
os.makedirs("models", exist_ok=True)
joblib.dump(model, os.path.join("models", "credit_risk_model.pkl"))
joblib.dump(scaler, os.path.join("models", "scaler.pkl"))
# Persist the full feature list (from the encoded dataframe) as JSON for consistency
with open(os.path.join("models", "feature_names.json"), "w", encoding="utf-8") as f:
	json.dump(X.columns.tolist(), f)

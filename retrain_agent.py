# retrain_agent.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score
import joblib
import os
import datetime

THRESHOLD_AUC = 0.75
DATA_PATH = "credit_data.csv"
MODEL_PATH = "credit_risk_model.pkl"

def retrain_if_needed():
    df = pd.read_csv(DATA_PATH)
    y = df["loan_status"]
    X = df.drop(columns=["loan_status"])
    X = pd.get_dummies(X, drop_first=True)

    # Ensure we keep track of columns for future inputs
    feature_names = X.columns.tolist()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X_train, y_train)

    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    print(f"Current AUC: {auc:.4f}")

    if auc < THRESHOLD_AUC:
        print("⚠️ Model underperforming. Retraining and saving new model.")
    else:
        print("✅ Model is healthy. Saving latest version anyway.")

    # Save model and metadata
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, "scaler.pkl")
    joblib.dump(feature_names, "feature_names.pkl")

    # Optional: versioned backup
    backup_dir = "model_versions"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    joblib.dump(model, f"{backup_dir}/model_{timestamp}.pkl")

if __name__ == "__main__":
    retrain_if_needed()

# retrain_agent.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score

THRESHOLD_AUC = 0.75
# Use the dataset included in the repository by default
DATA_PATH = "credit_risk_dataset.csv"
MODEL_PATH = "credit_risk_model.pkl"

def retrain_if_needed():
    df = pd.read_csv(DATA_PATH)
    y = df["loan_status"]
    X = df.drop(columns=["loan_status"])
    X = pd.get_dummies(X, drop_first=True)

    # Ensure we keep track of columns for future inputs
    feature_names = X.columns.tolist()

    # Split before scaling to avoid leakage
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X_train_scaled, y_train)

    auc = roc_auc_score(y_test, model.predict_proba(X_test_scaled)[:, 1])

    if auc < THRESHOLD_AUC:
        status = "⚠️ UNDERPERFORMING: Model Retrained!"
    else:
        status = "✅ HEALTHY: Model Updated."

    # Save model and metadata (joblib.dump calls)

    return {
        "status": status,
        "auc": round(auc, 4),
        "threshold": THRESHOLD_AUC
    }
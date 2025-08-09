# credit_model.py
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

if __name__ == "__main__":
    # === File paths ===
    processed_data_path = "processed_data.pkl"
    model_path = "xgclassifier_model.pkl"

    # === Load processed data ===
    try:
        data = joblib.load(processed_data_path)
        print(f"✅ Loaded processed data from {processed_data_path}")
    except FileNotFoundError:
        print(f"❌ Processed data file not found: {processed_data_path}")
        exit(1)

    X = data["features"]
    y = data["target"]

    # === Train-test split ===
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # === Train model ===
    model = XGBClassifier(eval_metric="logloss")
    model.fit(X_train, y_train)

    print("✅ Model training complete.")

    # === Save model ===
    joblib.dump(model, model_path)
    print(f"💾 Model saved to {model_path}")

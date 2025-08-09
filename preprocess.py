# preprocess.py
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

if __name__ == "__main__":
    # === File paths ===
    dataset_path = "credit_risk_dataset.csv"
    processed_data_path = "processed_data.pkl"
    preprocessor_path = "preprocessor.pkl"

    # === Load dataset ===
    try:
        df = pd.read_csv(dataset_path)
        print(f"✅ Loaded dataset from {dataset_path}")
    except FileNotFoundError:
        print(f"❌ Dataset file not found: {dataset_path}")
        exit(1)

    # === Separate features & target ===
    target_col = "loan_status"
    y = df[target_col]
    X = df.drop(columns=[target_col])

    # === Identify column types ===
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

    print(f"📊 Numeric columns: {numeric_cols}")
    print(f"📊 Categorical columns: {categorical_cols}")

    # === Preprocessor ===
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
        ]
    )

    # === Fit & transform features ===
    X_processed = preprocessor.fit_transform(X)

    print(f"✅ Preprocessing complete. Processed shape: {X_processed.shape}")

    # === Save processed data and preprocessor ===
    joblib.dump({"features": X_processed, "target": y}, processed_data_path)
    print(f"💾 Processed data saved to {processed_data_path}")

    joblib.dump(preprocessor, preprocessor_path)
    print(f"💾 Preprocessor saved to {preprocessor_path}")

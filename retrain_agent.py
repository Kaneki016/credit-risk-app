# retrain_agent.py
import os
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, classification_report
import xgboost as xgb
import numpy as np
import sklearn
from datetime import datetime

THRESHOLD_AUC = 0.75
# Use the dataset included in the repository by default
# Prefer dataset in data/ folder if present, otherwise fall back to repository root
DEFAULT_DATA_PATHS = [os.path.join("data", "credit_risk_dataset.csv"), "credit_risk_dataset.csv"]
DATA_PATH = next((p for p in DEFAULT_DATA_PATHS if os.path.exists(p)), DEFAULT_DATA_PATHS[0])
MODELS_DIR = "models"
MODEL_PATH = os.path.join(MODELS_DIR, "credit_risk_model.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")
FEATURES_PATH = os.path.join(MODELS_DIR, "feature_names.json")
MODEL_CARDS_DIR = "model_cards"


def _write_model_card_markdown(card: str, fname: str):
    os.makedirs(MODEL_CARDS_DIR, exist_ok=True)
    md_path = os.path.join(MODEL_CARDS_DIR, fname + ".md")
    html_path = os.path.join(MODEL_CARDS_DIR, fname + ".html")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(card)

    # Very small HTML wrapper to render markdown in a browser without extra deps
    try:
        import markdown
        html = markdown.markdown(card)
    except Exception:
        # Minimal conversion: wrap markdown in <pre> as fallback
        html = "<pre>" + card.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</pre>"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"<html><head><meta charset=\"utf-8\"><title>Model Card</title></head><body>{html}</body></html>")


def _generate_markdown_card(metadata: dict, report: str, features: list) -> str:
    ts = metadata.get("timestamp")
    lines = [
        f"# Model Card - Credit Risk Model",
        "",
        f"**Generated:** {ts}",
        "",
        "## Summary",
        f"- AUC: **{metadata.get('auc')}** (threshold: {metadata.get('threshold')})",
        f"- Status: {metadata.get('status')}",
        "",
        "## Model Details",
        f"- XGBoost version: {metadata.get('xgboost_version')}",
        f"- scikit-learn version: {metadata.get('sklearn_version')}",
        "",
        "## Features",
        "\n".join([f"- {f}" for f in features]),
        "",
        "## Classification Report",
        "```",
        report,
        "```",
        "",
        "## Notes",
        "- This model card was auto-generated after a retraining run.",
    ]
    return "\n".join(lines)


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

    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)

    auc = roc_auc_score(y_test, y_pred_proba)
    class_report = classification_report(y_test, y_pred, digits=4)

    # Prepare metadata
    metadata = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "auc": round(float(auc), 4),
        "threshold": THRESHOLD_AUC,
        "status": "✅ HEALTHY: Model Updated." if auc >= THRESHOLD_AUC else "⚠️ UNDERPERFORMING: Model Retrained!",
        "xgboost_version": getattr(xgb, "__version__", "unknown"),
        "sklearn_version": getattr(sklearn, "__version__", "unknown"),
        "n_train": int(X_train.shape[0]),
        "n_test": int(X_test.shape[0])
    }

    # Persist model artifacts
    os.makedirs(MODELS_DIR, exist_ok=True)

    # Versioned filenames (use UTC timestamp)
    version_ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    model_versioned = os.path.join(MODELS_DIR, f"credit_risk_model_v{version_ts}.pkl")
    scaler_versioned = os.path.join(MODELS_DIR, f"scaler_v{version_ts}.pkl")
    features_versioned = os.path.join(MODELS_DIR, f"feature_names_v{version_ts}.json")

    joblib.dump(model, model_versioned)
    joblib.dump(scaler, scaler_versioned)
    with open(features_versioned, "w", encoding="utf-8") as f:
        json.dump(feature_names, f)

    # Compute and save numerical feature statistics (min/max/mean/std) from the training set
    try:
        # raw X before one-hot encoding
        raw_X = df.drop(columns=["loan_status"])  # original features
        numeric_cols = raw_X.select_dtypes(include=[np.number]).columns.tolist()
        feature_stats = {}
        if len(numeric_cols) > 0:
            # Use the training split to compute stats
            X_train_raw = X_train.copy()
            # If X_train is one-hot encoded, try to map numeric_cols intersection
            # Prefer computing stats from raw_X using train index
            try:
                # locate rows in raw_X corresponding to X_train by index (works if indices preserved)
                X_train_raw_from_df = raw_X.loc[X_train.index, numeric_cols]
            except Exception:
                # fallback to using raw numeric columns from the whole dataset
                X_train_raw_from_df = raw_X[numeric_cols]

            for col in numeric_cols:
                col_values = X_train_raw_from_df[col].dropna().astype(float)
                if col_values.size == 0:
                    continue
                feature_stats[col] = {
                    "min": float(col_values.min()),
                    "max": float(col_values.max()),
                    "mean": float(col_values.mean()),
                    "std": float(col_values.std(ddof=0))
                }

            stats_path = os.path.join(MODELS_DIR, "feature_statistics.json")
            with open(stats_path, "w", encoding="utf-8") as sf:
                json.dump(feature_stats, sf, indent=2)
    except Exception:
        # Non-fatal: if stats computation fails, continue without blocking saving artifacts
        pass

    # Also update the unversioned paths for compatibility
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    with open(FEATURES_PATH, "w", encoding="utf-8") as f:
        json.dump(feature_names, f)

    # Attempt to use Model Card Toolkit (MCT) if installed; otherwise fallback to simple markdown
    card_name = f"model_card_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
    try:
        import model_card_toolkit as mct

        # Try a minimal MCT flow. If API differs, this may raise and we fallback below.
        toolkit = mct.ModelCardToolkit()
        model_card = toolkit.scaffold_model_card()
        model_card.model_details = {
            "name": "Credit Risk XGBoost",
            "version": metadata["timestamp"],
            "type": "xgboost.XGBClassifier"
        }
        model_card.model_parameters = {"xgboost_version": metadata["xgboost_version"]}
        model_card.model_eval = {"auc": metadata["auc"], "classification_report": class_report}
        # Export using the toolkit
        os.makedirs(MODEL_CARDS_DIR, exist_ok=True)
        out_dir = os.path.join(MODEL_CARDS_DIR, card_name)
        toolkit.write_model_card(model_card, out_dir)
        exported = {"markdown": os.path.join(out_dir, "model_card.md"), "html": os.path.join(out_dir, "index.html")}
    except Exception:
        # Fallback: simple markdown + html files
        md = _generate_markdown_card(metadata, class_report, feature_names)
        _write_model_card_markdown(md, card_name)
        exported = {"markdown": os.path.join(MODEL_CARDS_DIR, card_name + ".md"), "html": os.path.join(MODEL_CARDS_DIR, card_name + ".html")}

    # Update manifest.json with the new version entry
    manifest_path = os.path.join(MODELS_DIR, "manifest.json")
    manifest = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as mf:
                manifest = json.load(mf)
        except Exception:
            manifest = []

    manifest_entry = {
        "timestamp": metadata["timestamp"],
        "auc": metadata["auc"],
        "status": metadata["status"],
        "model": model_versioned,
        "scaler": scaler_versioned,
        "features": features_versioned,
        "card": exported
    }

    manifest.append(manifest_entry)
    # Keep only the most recent 10 entries to limit size
    manifest = sorted(manifest, key=lambda x: x.get("timestamp"))[-10:]
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)

    result = {
        "status": metadata["status"],
        "auc": metadata["auc"],
        "threshold": THRESHOLD_AUC,
        "artifacts": {
            "model": MODEL_PATH,
            "scaler": SCALER_PATH,
            "features": FEATURES_PATH
        },
        "model_card": exported
    }

    return result
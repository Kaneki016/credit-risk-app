# api.py
import joblib
import pandas as pd
import numpy as np
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from predictor import CreditRiskPredictor
# Use the single canonical Pydantic model from model_schema.py
from model_schema import LoanApplication
from retrain_agent import retrain_if_needed, MODEL_CARDS_DIR
import math
import logging
import httpx
import requests
import os  # REQUIRED for os.getenv()
from dotenv import load_dotenv  # REQUIRED to load the .env file
from logging_setup import configure_logging
 

# --- Setup Logging ---
# Use centralized logging setup
configure_logging()
logger = logging.getLogger(__name__)

# --- Gemini API ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"


# --- 1. Initialize the Core Predictor Class ---
# This loads the model and preprocessors once when the API starts.
try:
    predictor = CreditRiskPredictor()
    logger.info("CreditRiskPredictor loaded successfully.")
except Exception as e:
    # If loading fails, log the error and let the API start with an error state
    logger.error(f"FATAL: Model loading failed. Prediction API will be disabled. Error: {e}")
    predictor = None
    
# --- Load feature statistics for drift detection if available ---
FEATURE_STATS = {}
try:
    stats_path = os.path.join("models", "feature_statistics.json")
    if os.path.exists(stats_path):
        with open(stats_path, "r", encoding="utf-8") as sf:
            FEATURE_STATS = json.load(sf)
except Exception:
    FEATURE_STATS = {}
    
# --- 2. Input schema ---
# `LoanApplication` is defined in `model_schema.py` and imported above.

# --- 3. Initialize FastAPI Application ---
app = FastAPI(
    title="Agentic Credit Risk Prediction API for n8n",
    version="1.0.0",
    description="Serves the XGBoost credit risk model for automated workflows (n8n)."
)

# --- NEW: Async Function to Call LLM for Explanation ---
async def generate_llm_explanation(
    input_data: Dict[str, Any],
    shap_explanation: Dict[str, float],
    risk_level: str,
) -> str:
    """Asynchronously sends SHAP results and application data to Gemini for a natural language explanation.

    Uses httpx.AsyncClient for non-blocking I/O.
    """
    shap_series = pd.Series(shap_explanation).sort_values(key=abs, ascending=False).head(5)

    prompt = f"""
    You are an expert Credit Risk Analyst. Explain the decision for this loan application
    in a concise, single paragraph suitable for a bank client.

    The predicted outcome is: {risk_level}.

    The top 5 most impactful features (SHAP values) contributing to this decision are:
    {shap_series.to_dict()}

    The raw applicant data is: {input_data}

    Focus on summarizing *why* the loan was approved or rejected based on these factors.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {
            "parts": [{"text": "You are a friendly, expert financial analyst explaining complex risk to a non-expert."}]
        }
    }

    headers = {"Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "LLM explanation unavailable.")
            return text
    except Exception as e:
        logger.error("Gemini API async call failed: %s", e)
        return f"Could not generate LLM explanation due to API error: {str(e)}"

# --- 4. Health Check Endpoint ---
@app.get("/")
@app.get("/health")
def health_check():
    """Check if the API is running and the model is loaded."""
    if predictor is None:
        raise HTTPException(
            status_code=503, 
            detail={"status": "error", "message": "Model not loaded. Service unavailable.", "load_error": str(predictor.load_error) if predictor else "Unknown"}
        )
    return {"status": "ok", "message": "API is running and model is ready."}

# --- 5. Prediction Endpoint (The main target for n8n) ---
@app.post("/predict_risk", response_model=Dict[str, Any])
async def predict_risk(application: LoanApplication):
    """
    Accepts loan application data and returns a credit risk prediction, probability,
    and SHAP explanation data.
    """
    if predictor is None:
        raise HTTPException(
            status_code=503, 
            detail={"status": "error", "message": "Model not loaded. Cannot process prediction."}
        )

    # Convert Pydantic model to a raw dictionary
    raw_input_dict = application.model_dump()

    # --- Data drift check: compare numeric fields against training statistics ---
    drift_warnings = []
    try:
        for feat, stats in FEATURE_STATS.items():
            if feat in raw_input_dict:
                try:
                    val = float(raw_input_dict[feat])
                except Exception:
                    continue
                mn = stats.get("min")
                mx = stats.get("max")
                mean = stats.get("mean")
                std = stats.get("std")
                flagged = False
                if mn is not None and mx is not None and (val < mn or val > mx):
                    drift_warnings.append(f"{feat}: value {val} outside training min/max [{mn}, {mx}]")
                    logger.warning("Data drift detected: %s outside min/max [%s, %s]", feat, mn, mx)
                    flagged = True
                if not flagged and mean is not None and std is not None and std >= 0:
                    # check ±3 sigma
                    lower = mean - 3 * std
                    upper = mean + 3 * std
                    if val < lower or val > upper:
                        drift_warnings.append(f"{feat}: value {val} outside 3-sigma range [{lower}, {upper}]")
                        logger.warning("Data drift detected: %s outside 3-sigma [%s, %s]", feat, lower, upper)
    except Exception as e:
        logger.debug("Error during drift check: %s", e)

    # --- Prepare Input Dictionary (Matching app.py's structure) ---
    
    # The predictor expects the one-hot-encoded columns (e.g., 'person_home_ownership_RENT': 1)
    # Re-map the raw inputs into the one-hot format for the predictor.
    input_dict_for_predictor = {
        "person_age": raw_input_dict["person_age"],
        "person_income": raw_input_dict["person_income"],
        "person_emp_length": raw_input_dict["person_emp_length"],
        "loan_amnt": raw_input_dict["loan_amnt"],
        "loan_int_rate": raw_input_dict["loan_int_rate"],
        "loan_percent_income": raw_input_dict["loan_percent_income"],
        "cb_person_cred_hist_length": raw_input_dict["cb_person_cred_hist_length"],
        
        # One-hot encoded versions are constructed here:
        f"person_home_ownership_{raw_input_dict['home_ownership']}": 1,
        f"loan_intent_{raw_input_dict['loan_intent']}": 1,
        f"loan_grade_{raw_input_dict['loan_grade']}": 1,
        f"cb_person_default_on_file_{raw_input_dict['default_on_file']}": 1
    }

    try:
        # Get prediction
        risk_level, prob, pred = predictor.predict(input_dict_for_predictor, flag_threshold=0.6)
        
        # Get SHAP values
        shap_values, expected_value, df_features = predictor.get_shap_values(input_dict_for_predictor)
        
        # Format SHAP data for JSON output
        feature_names = df_features.columns.tolist()
        
        # Handle SHAP values for binary classification
        if isinstance(shap_values, list):
            # For binary classification, TreeExplainer returns list of arrays where index 1 
            # corresponds to the probability of default (positive class)
            logger.debug("Using SHAP values for positive class (default probability)")
            shap_data = shap_values[1]
        else:
            # For single-output cases (shouldn't occur with binary classification)
            logger.warning("Unexpected single SHAP array - model may not be binary classification")
            shap_data = shap_values

        # Try to extract the first row of SHAP values in a robust way
        try:
            row = shap_data.tolist()[0]
        except Exception:
            # shap_data may already be 1-D or not have a nested list structure
            row = np.asarray(shap_data).ravel().tolist()

        # If lengths mismatch, zip will truncate to the shorter; log for diagnostics
        if len(feature_names) != len(row):
            logger.warning("SHAP feature count (%s) != feature_names count (%s). Truncating to min length.", len(row), len(feature_names))

        # Ensure all SHAP values are native Python floats for JSON serialization
        shap_explanation = {k: float(v) for k, v in zip(feature_names, row)}

    except Exception as e:
        logger.error(f"Prediction or SHAP calculation failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail={"status": "error", "message": f"Internal prediction error: {str(e)}"}
        )

    # --- 6. Generate LLM Explanation ---
    # Call the LLM explanation asynchronously and await the result
    llm_explanation = await generate_llm_explanation(
        input_data=raw_input_dict,
        shap_explanation=shap_explanation,
        risk_level=risk_level,
    )
    # Prepare a human-friendly operational notes section from drift warnings
    if drift_warnings:
        operational_notes = "Data drift warnings detected: " + "; ".join(drift_warnings) + ". Please review input data and consider retraining or investigating data pipelines."
    else:
        operational_notes = ""
    
    # --- 7. Prepare final response object for n8n ---
    return {
        "status": "success",
        "timestamp": pd.Timestamp.now().isoformat(),
        "risk_level": risk_level,
        "probability_default_percent": round(prob * 100, 2),
        "binary_prediction": pred,
        "model_confidence_threshold": 0.6,
        "input_features": raw_input_dict,
        "shap_explanation": shap_explanation,
        "llm_explanation": llm_explanation,
        "data_drift_warnings": drift_warnings,
        "operational_notes": operational_notes
    }

@app.post("/trigger_retrain")
def trigger_retrain_cycle():
    """Triggers the model retraining and returns the outcome."""
    try:
        # Execute the core retraining function, capturing the result
        retrain_result = retrain_if_needed()
        return {"status": "success", "result": retrain_result}
    except Exception as e:
        logger.error(f"Retraining failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": f"Retraining failed: {str(e)}"}
        )
    
@app.get("/model_card/latest")
def get_latest_model_card():
    """Return paths and small previews for the most recent generated model card."""
    try:
        if not os.path.isdir(MODEL_CARDS_DIR):
            raise HTTPException(status_code=404, detail={"message": "No model cards found"})

        entries = [os.path.join(MODEL_CARDS_DIR, f) for f in os.listdir(MODEL_CARDS_DIR) if os.path.isfile(os.path.join(MODEL_CARDS_DIR, f))]
        if not entries:
            raise HTTPException(status_code=404, detail={"message": "No model cards found"})

        # Pick the most recently modified file and then gather its pair (.md/.html)
        latest = max(entries, key=os.path.getmtime)
        base = os.path.splitext(latest)[0]
        md = base + ".md"
        html = base + ".html"

        preview_md = None
        try:
            with open(md, "r", encoding="utf-8") as f:
                preview_md = f.read()[:2000]
        except Exception:
            preview_md = None

        return {"markdown_path": md, "html_path": html, "preview_markdown": preview_md}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve latest model card: %s", e)
        raise HTTPException(status_code=500, detail={"message": "Internal error retrieving model card"})


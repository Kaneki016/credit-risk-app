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
) -> Dict[str, Any]:
    """Asynchronously sends SHAP results and application data to Gemini for a natural language explanation.

    Uses httpx.AsyncClient for non-blocking I/O.
    """
    shap_series = pd.Series(shap_explanation).sort_values(key=abs, ascending=False).head(5)

    # Request a structured JSON response so callers can programmatically use remediation suggestions
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

    # Quick sanity check: ensure API key is present
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set; skipping LLM call and returning placeholder explanation.")
        return {"text": "LLM explanation disabled (no API key).", "raw": "", "remediation_suggestion": None, "error": "no_api_key"}

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
            response = await client.post(url, headers=headers, json=payload)
            # Log status for diagnostics
            logger.debug("Gemini request status: %s; url: %s", response.status_code, url)
            text = None
            try:
                result = response.json()
            except Exception:
                result = None

            # Try several common response shapes (generative API variants)
            if result:
                # shape: {candidates:[{content:{parts:[{text:...}]}}]}
                try:
                    text = result.get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text")
                except Exception:
                    text = None
                # shape: {output:[{content:[{text:...}]}]}
                if not text:
                    try:
                        text = result.get("output", [])[0].get("content", [])[0].get("text")
                    except Exception:
                        text = None
            # Fallback: use raw response text
            if not text:
                text = response.text[:10000] if response.text else ""

            # Now attempt to extract structured JSON from the returned text
            remediation = None
            explanation_text = text
            try:
                import re
                m = re.search(r"\{[\s\S]*\}", text)
                if m:
                    json_text = m.group(0)
                    parsed = json.loads(json_text)
                    remediation = parsed.get("remediation_suggestion") or parsed.get("remediation")
                    explanation_text = parsed.get("explanation") or parsed.get("explanation_text") or explanation_text
            except Exception as parse_err:
                logger.debug("Could not parse JSON from LLM text: %s", parse_err)

            # If the LLM didn't provide a remediation suggestion, build a simple rule-based fallback
            if not remediation:
                try:
                    def build_rule_based_remediation(input_data, shap_expl, risk_level):
                        try:
                            top_feats = sorted(shap_expl.items(), key=lambda x: abs(x[1]), reverse=True)
                        except Exception:
                            top_feats = []

                        def n(key, default=None):
                            try:
                                return float(input_data.get(key, default)) if input_data.get(key) is not None else default
                            except Exception:
                                return default

                        income = n("person_income", None)
                        loan_amnt = n("loan_amnt", None)
                        loan_pct = n("loan_percent_income", None)
                        loan_rate = n("loan_int_rate", None)
                        cred_hist = n("cb_person_cred_hist_length", None)
                        emp_length = n("person_emp_length", None)

                        suggestions = []

                        prev_default = str(input_data.get("default_on_file", "")).upper()
                        if prev_default in ("Y", "YES", "TRUE"):
                            suggestions.append("Applicant has a previous default on file — require a co-signer, collateral, or significantly reduce the requested amount.")

                        if loan_pct is not None and loan_pct > 0.35:
                            if income:
                                suggested = int(max(0, income * 0.30))
                                suggestions.append(f"Requested loan equals {loan_pct*100:.0f}% of income — consider reducing the loan to ~${suggested:,} (≈30% of income) or offering a longer term.")
                            else:
                                suggestions.append("Requested loan is a large share of income — consider reducing the amount or verifying income documentation.")

                        if loan_amnt is not None and income is not None and loan_amnt > income * 0.5:
                            suggestions.append(f"Loan amount (${int(loan_amnt):,}) is >50% of annual income; consider reducing amount or requiring collateral/co-signer.")

                        if loan_rate is not None and loan_rate >= 15:
                            suggestions.append("Loan interest rate is high; consider offering a lower rate, longer term, or requiring additional assurances (collateral/co-signer).")

                        if cred_hist is not None and cred_hist < 2:
                            suggestions.append("Short credit history — consider requiring a guarantor or additional documentation, or offer a smaller secured loan.")
                        if emp_length is not None and emp_length < 6:
                            suggestions.append("Limited recent employment duration — consider verifying employment stability or requiring a co-signer.")

                        if not suggestions and top_feats:
                            top_name, top_val = top_feats[0]
                            if "loan_amnt" in top_name or "loan_percent_income" in top_name:
                                suggestions.append("Top risk factor is loan size — reduce requested amount or increase downpayment.")
                            elif "person_income" in top_name:
                                suggestions.append("Top risk factor is low income — require income verification or lower the loan amount.")
                            elif "loan_int_rate" in top_name:
                                suggestions.append("Top risk factor is interest rate — consider presenting refinancing or longer term options.")
                            else:
                                suggestions.append("Top contributing factors indicate elevated risk; consider reducing exposure (smaller loan), requiring collateral/co-signer, or additional underwriting checks.")

                        final = " ".join(suggestions)
                        if len(final) > 400:
                            final = final[:400].rsplit('.', 1)[0] + '.'
                        return final or None

                    remediation = build_rule_based_remediation(input_data, shap_explanation, risk_level)
                except Exception as fallback_err:
                    logger.debug("Fallback remediation builder failed: %s", fallback_err)

            return {"text": explanation_text, "raw": text, "remediation_suggestion": remediation}
    except httpx.HTTPStatusError as e:
        logger.error("Gemini API returned HTTP error %s: %s", e.response.status_code if e.response is not None else "?", e)
        body = ""
        try:
            body = e.response.text
        except Exception:
            body = str(e)
        return {"text": f"LLM API error: {e}", "raw": body, "remediation_suggestion": None, "error": "http_status"}
    except Exception as e:
        logger.error("Gemini API async call failed: %s", e)
        return {"text": f"Could not generate LLM explanation due to API error: {str(e)}", "raw": "", "remediation_suggestion": None, "error": "exception"}

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
    llm_result = await generate_llm_explanation(
        input_data=raw_input_dict,
        shap_explanation=shap_explanation,
        risk_level=risk_level,
    )
    # llm_result is a dict: {"text": ..., "raw": ..., "remediation_suggestion": ...}
    llm_explanation = llm_result.get("text") if isinstance(llm_result, dict) else str(llm_result)
    remediation_suggestion = None
    if isinstance(llm_result, dict):
        remediation_suggestion = llm_result.get("remediation_suggestion")
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
        "remediation_suggestion": remediation_suggestion,
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


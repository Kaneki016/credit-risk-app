# backend/api/main.py
import joblib
import pandas as pd
import numpy as np
import json
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import math
import logging
import httpx
import requests
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Internal imports
from backend.models.predictor import CreditRiskPredictor
from backend.models.dynamic_predictor import DynamicCreditRiskPredictor
from backend.database import get_db, init_db, check_connection, crud
from backend.utils.ai_client import get_ai_client
from backend.database.models import Prediction as DBPrediction
from sqlalchemy.orm import Session
from backend.services.database_retraining import DatabaseRetrainer, check_retraining_status
from backend.api.clear_database_endpoint import router as clear_db_router
from backend.core.schemas import LoanApplication
from backend.services.imputation import DynamicLoanApplication
from backend.services.retraining import retrain_if_needed, MODEL_CARDS_DIR
from backend.core.logging_setup import configure_logging
 

# --- Setup Logging ---
# Use centralized logging setup
configure_logging()
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# AI API configuration - OpenRouter (preferred) or Gemini (legacy)
# OpenRouter provides unified access to multiple AI models

# Check for OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
USE_OPENROUTER = bool(OPENROUTER_API_KEY)

# Legacy Gemini configuration (fallback)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

# Determine which AI provider to use
if USE_OPENROUTER:
    AI_PROVIDER = "OpenRouter"
    AI_API_KEY = OPENROUTER_API_KEY
    logger.info(f"Using OpenRouter with model: {OPENROUTER_MODEL}")
else:
    AI_PROVIDER = "Gemini"
    AI_API_KEY = GEMINI_API_KEY
    logger.info("Using Gemini API (legacy mode)")

# Feature toggles
ENABLE_SHAP_EXPLANATIONS = os.getenv("ENABLE_SHAP_EXPLANATIONS", "true").lower() == "true"

# Log configuration
logger.info(f"AI Provider: {AI_PROVIDER}")
logger.info(f"SHAP Explanations: {'Enabled' if ENABLE_SHAP_EXPLANATIONS else 'Disabled'}")
if AI_API_KEY:
    logger.info(f"{AI_PROVIDER} API key configured")
else:
    logger.warning("No AI API key configured - explanations will use fallback logic")


# --- 1. Initialize the Core Predictor Class ---
# This loads the model and preprocessors once when the API starts.
try:
    predictor = CreditRiskPredictor()
    logger.info("CreditRiskPredictor loaded successfully.")
except Exception as e:
    # If loading fails, log the error and let the API start with an error state
    logger.error(f"FATAL: Model loading failed. Prediction API will be disabled. Error: {e}")
    predictor = None

# --- Initialize Dynamic Predictor ---
dynamic_predictor = None
try:
    dynamic_predictor = DynamicCreditRiskPredictor()
    logger.info("DynamicCreditRiskPredictor loaded successfully.")
except Exception as e:
    logger.warning(f"Dynamic predictor initialization failed: {e}")
    dynamic_predictor = None

# Gemini AI is used only for generating natural language explanations
# No separate predictor needed - integrated into the main prediction flow
    
# --- Load feature statistics for drift detection if available ---
FEATURE_STATS = {}
try:
    # Use absolute path to ensure it works regardless of working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = script_dir  # api.py is in the project root
    stats_path = os.path.join(project_root, "models", "feature_statistics.json")
    if os.path.exists(stats_path):
        with open(stats_path, "r", encoding="utf-8") as sf:
            FEATURE_STATS = json.load(sf)
        logger.info(f"Loaded feature statistics from: {stats_path}")
except Exception as e:
    logger.warning(f"Could not load feature statistics: {e}")
    FEATURE_STATS = {}
    
# --- 2. Input schema ---
# `LoanApplication` is defined in `model_schema.py` and imported above.

# --- 3. Initialize FastAPI Application ---
app = FastAPI(
    title="Credit Risk Prediction API",
    version="2.0.0",
    description="AI-powered credit risk prediction with XGBoost ML model, SHAP explainability, and AI-generated insights."
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and check connection on startup."""
    try:
        if check_connection():
            init_db()
            logger.info("Database initialized successfully")
        else:
            logger.warning("Database connection failed - running without database")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        logger.warning("API will run without database functionality")

# Allow cross-origin requests from local frontend (development)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(clear_db_router, tags=["database"])

# --- NEW: Async Function to Call LLM for Explanation ---
async def generate_llm_explanation(
    input_data: Dict[str, Any],
    shap_explanation: Dict[str, float],
    risk_level: str,
) -> Dict[str, Any]:
    """Asynchronously sends SHAP results and application data to AI for a natural language explanation.

    Uses the AI client with automatic retry logic and request counting.
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

    system_prompt = "You are a friendly, expert financial analyst explaining complex risk to a non-expert."

    # Check if SHAP explanations are enabled
    if not ENABLE_SHAP_EXPLANATIONS:
        logger.info("SHAP explanations disabled via configuration")
        return {"text": "AI explanations disabled (feature toggle off).", "raw": "", "remediation_suggestion": None, "error": "disabled"}
    
    # Use AI client with retry logic and request counting
    ai_client = get_ai_client()
    
    if not ai_client.is_available():
        logger.warning("No AI API key set; skipping LLM call and returning placeholder explanation.")
        return {"text": "LLM explanation disabled (no API key).", "raw": "", "remediation_suggestion": None, "error": "no_api_key"}

    try:
        # Use the AIClientWithRetry for proper error handling and retry logic
        result = await ai_client.generate_with_retry(prompt, system_prompt)
        
        if result.get("error"):
            logger.warning(f"AI client returned error: {result.get('error')} - Using fallback explanation")
            # Generate comprehensive fallback explanation
            fallback_explanation = _generate_fallback_explanation(input_data, shap_explanation, risk_level)
            remediation = _build_rule_based_remediation(input_data, shap_explanation, risk_level)
            return {
                "text": fallback_explanation,
                "raw": result.get("raw", ""),
                "remediation_suggestion": remediation,
                "error": result.get("error"),
                "fallback_used": True
            }
        
        # Parse the AI response
        text = result.get("text", "")
        
        # Try to extract structured JSON from the response
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

        # If no remediation from AI, use rule-based fallback
        if not remediation:
            remediation = _build_rule_based_remediation(input_data, shap_explanation, risk_level)

        return {
            "text": explanation_text,
            "raw": result.get("raw", ""),
            "remediation_suggestion": remediation
        }
        
    except Exception as e:
        logger.error("Unexpected error in generate_llm_explanation: %s", e)
        # Generate comprehensive fallback explanation
        fallback_explanation = _generate_fallback_explanation(input_data, shap_explanation, risk_level)
        remediation = _build_rule_based_remediation(input_data, shap_explanation, risk_level)
        return {
            "text": fallback_explanation,
            "raw": "",
            "remediation_suggestion": remediation,
            "error": "exception",
            "fallback_used": True
        }


def _generate_fallback_explanation(input_data: Dict[str, Any], shap_expl: Dict[str, float], risk_level: str) -> str:
    """Generate a comprehensive human-readable explanation when AI is unavailable."""
    try:
        # Get top contributing factors
        top_feats = sorted(shap_expl.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        
        # Helper to safely get numeric values
        def n(key, default=None):
            try:
                return float(input_data.get(key, default)) if input_data.get(key) is not None else default
            except Exception:
                return default
        
        # Extract key metrics
        income = n("person_income")
        loan_amnt = n("loan_amnt")
        loan_pct = n("loan_percent_income")
        loan_rate = n("loan_int_rate")
        cred_hist = n("cb_person_cred_hist_length")
        emp_length = n("person_emp_length")
        age = n("person_age")
        
        # Build explanation based on risk level
        if "HIGH" in risk_level.upper() or "REJECT" in risk_level.upper():
            explanation = "This loan application has been flagged as **high risk** based on our credit risk assessment model. "
            
            # Identify primary concerns
            concerns = []
            if loan_pct and loan_pct > 0.4:
                concerns.append(f"the requested loan amount represents {loan_pct*100:.0f}% of annual income, which is significantly high")
            if loan_rate and loan_rate >= 15:
                concerns.append(f"the interest rate of {loan_rate:.1f}% indicates elevated risk")
            if cred_hist and cred_hist < 2:
                concerns.append("limited credit history (less than 2 years)")
            if emp_length and emp_length < 1:
                concerns.append("very short employment duration")
            
            prev_default = str(input_data.get("default_on_file", "")).upper()
            if prev_default in ("Y", "YES", "TRUE"):
                concerns.append("previous default on file")
            
            if concerns:
                explanation += "Key concerns include: " + ", ".join(concerns) + ". "
            
            # Add top SHAP factors
            if top_feats:
                top_factor_names = []
                for feat_name, feat_val in top_feats[:3]:
                    # Clean up feature names for readability
                    clean_name = feat_name.replace("_", " ").replace("person ", "").replace("loan ", "").replace("cb ", "")
                    if feat_val > 0:
                        top_factor_names.append(clean_name)
                
                if top_factor_names:
                    explanation += f"The most significant factors contributing to this decision are: {', '.join(top_factor_names)}. "
            
            explanation += "We recommend reviewing the application details and considering risk mitigation measures before approval."
            
        elif "MEDIUM" in risk_level.upper() or "MODERATE" in risk_level.upper():
            explanation = "This loan application presents **moderate risk** according to our assessment. "
            
            # Identify mixed signals
            positives = []
            concerns = []
            
            if income and income >= 50000:
                positives.append("stable income level")
            if cred_hist and cred_hist >= 5:
                positives.append("established credit history")
            if emp_length and emp_length >= 5:
                positives.append("long-term employment")
            
            if loan_pct and loan_pct > 0.3:
                concerns.append(f"loan-to-income ratio of {loan_pct*100:.0f}%")
            if loan_rate and loan_rate >= 12:
                concerns.append("elevated interest rate")
            
            if positives and concerns:
                explanation += f"While the applicant shows {' and '.join(positives)}, there are concerns regarding {' and '.join(concerns)}. "
            elif positives:
                explanation += f"The applicant demonstrates {' and '.join(positives)}, though some risk factors remain. "
            elif concerns:
                explanation += f"Key concerns include {' and '.join(concerns)}. "
            
            explanation += "Additional verification or adjusted loan terms may help mitigate the identified risks."
            
        else:  # LOW RISK / APPROVE
            explanation = "This loan application has been assessed as **low risk** and is recommended for approval. "
            
            # Identify strengths
            strengths = []
            if income and income >= 60000:
                strengths.append(f"strong annual income of ${income:,.0f}")
            if loan_pct and loan_pct <= 0.25:
                strengths.append(f"conservative loan-to-income ratio of {loan_pct*100:.0f}%")
            if cred_hist and cred_hist >= 5:
                strengths.append(f"solid credit history of {cred_hist:.0f} years")
            if emp_length and emp_length >= 5:
                strengths.append(f"stable employment for {emp_length:.0f} years")
            
            prev_default = str(input_data.get("default_on_file", "")).upper()
            if prev_default not in ("Y", "YES", "TRUE"):
                strengths.append("no previous defaults")
            
            if strengths:
                explanation += "Key positive factors include: " + ", ".join(strengths) + ". "
            
            if loan_amnt:
                explanation += f"The requested loan amount of ${loan_amnt:,.0f} appears manageable based on the applicant's financial profile. "
            
            explanation += "This application meets our standard approval criteria."
        
        # Add note about AI unavailability
        explanation += "\n\n*Note: This explanation was generated using rule-based analysis as AI-powered insights are temporarily unavailable.*"
        
        return explanation
        
    except Exception as e:
        logger.error(f"Error generating fallback explanation: {e}")
        return (
            f"Based on our credit risk model, this application has been classified as **{risk_level}**. "
            "The decision was made by analyzing multiple factors including income, loan amount, credit history, "
            "and employment stability. Please review the SHAP values above for detailed feature importance. "
            "\n\n*Note: Detailed explanation temporarily unavailable.*"
        )


def _build_rule_based_remediation(input_data: Dict[str, Any], shap_expl: Dict[str, float], risk_level: str) -> str:
    """Build rule-based remediation suggestions when AI is unavailable."""
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

# --- 4. Health Check Endpoint ---
@app.get("/")
@app.get("/health")
def health_check():
    """Check if the API is running and the model is loaded."""
    if predictor is None:
        error_msg = "Model not loaded. Service unavailable."
        return {
            "status": "error",
            "message": error_msg,
            "load_error": "Model failed to load during startup. Check logs for details."
        }
    return {"status": "ok", "message": "API is running and model is ready."}

# --- 4.5. Model Reload Endpoint ---
@app.post("/reload_model")
def reload_model():
    """Reload the model from disk. Useful after retraining or fixing model files."""
    global predictor, dynamic_predictor
    try:
        logger.info("Reloading model...")
        predictor = CreditRiskPredictor()
        dynamic_predictor = DynamicCreditRiskPredictor()
        logger.info("Model reloaded successfully.")
        return {
            "status": "success",
            "message": "Model reloaded successfully."
        }
    except Exception as e:
        logger.error(f"Model reload failed: {e}", exc_info=True)
        predictor = None
        dynamic_predictor = None
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Model reload failed: {str(e)}"
            }
        )

# --- 5. Single Prediction Endpoint (Legacy - kept for backward compatibility) ---
@app.post("/predict_risk", response_model=Dict[str, Any])
async def predict_risk(application: LoanApplication):
    """
    Accepts complete loan application data and returns a credit risk prediction, probability,
    SHAP explanation, and AI-generated advice.
    
    Note: For CSV uploads and partial data, use /predict_risk_dynamic or /predict_risk_batch instead.
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
    
    # --- 7. Prepare final response object ---
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

# --- 6. Dynamic Prediction Endpoint (Flexible Input) ---
@app.post("/predict_risk_dynamic", response_model=Dict[str, Any])
async def predict_risk_dynamic(application: DynamicLoanApplication):
    """
    Primary prediction endpoint for CSV uploads and flexible data input.
    
    Accepts partial or complete loan application data with intelligent imputation.
    Missing fields are automatically filled using historical data, derived calculations, or safe defaults.
    
    Features:
    - Accepts partial data (missing fields will be imputed)
    - SHAP explainability showing feature importance
    - AI-generated natural language explanations and advice
    - Data drift detection
    
    This is the recommended endpoint for all predictions.
    """
    if dynamic_predictor is None:
        raise HTTPException(
            status_code=503,
            detail={"status": "error", "message": "Dynamic predictor not loaded. Cannot process prediction."}
        )
    
    # Convert Pydantic model to dictionary, excluding None values initially
    raw_input_dict = application.model_dump(exclude_none=False)
    
    # Validate input
    is_valid, validation_warnings = dynamic_predictor.validate_input(raw_input_dict)
    
    # Get prediction with imputation
    try:
        risk_level, prob, pred, imputation_log, imputed_data = dynamic_predictor.predict(
            raw_input_dict, 
            flag_threshold=0.6,
            return_imputation_log=True
        )
        
        # Get SHAP values
        shap_values, expected_value, df_features, _ = dynamic_predictor.get_shap_values(raw_input_dict)
        
        # Format SHAP data
        feature_names = df_features.columns.tolist()
        
        if isinstance(shap_values, list):
            shap_data = shap_values[1]
        else:
            shap_data = shap_values
        
        try:
            row = shap_data.tolist()[0]
        except Exception:
            row = np.asarray(shap_data).ravel().tolist()
        
        shap_explanation = {k: float(v) for k, v in zip(feature_names, row)}
        
    except Exception as e:
        logger.error(f"Dynamic prediction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": f"Prediction error: {str(e)}"}
        )
    
    # Data drift check on imputed data
    drift_warnings = []
    try:
        for feat, stats in FEATURE_STATS.items():
            if feat in imputed_data:
                try:
                    val = float(imputed_data[feat])
                except Exception:
                    continue
                mn = stats.get("min")
                mx = stats.get("max")
                mean = stats.get("mean")
                std = stats.get("std")
                
                if mn is not None and mx is not None and (val < mn or val > mx):
                    drift_warnings.append(f"{feat}: value {val} outside training min/max [{mn}, {mx}]")
                elif mean is not None and std is not None and std >= 0:
                    lower = mean - 3 * std
                    upper = mean + 3 * std
                    if val < lower or val > upper:
                        drift_warnings.append(f"{feat}: value {val} outside 3-sigma range [{lower:.2f}, {upper:.2f}]")
    except Exception as e:
        logger.debug(f"Error during drift check: {e}")
    
    # Generate LLM explanation
    llm_result = await generate_llm_explanation(
        input_data=imputed_data,
        shap_explanation=shap_explanation,
        risk_level=risk_level,
    )
    
    llm_explanation = llm_result.get("text") if isinstance(llm_result, dict) else str(llm_result)
    remediation_suggestion = llm_result.get("remediation_suggestion") if isinstance(llm_result, dict) else None
    
    # Prepare operational notes
    operational_notes_parts = []
    if imputation_log:
        operational_notes_parts.append(f"Imputed {len(imputation_log)} fields: {', '.join(imputation_log[:5])}")
    if validation_warnings:
        operational_notes_parts.append(f"Validation warnings: {'; '.join(validation_warnings)}")
    if drift_warnings:
        operational_notes_parts.append(f"Data drift detected: {'; '.join(drift_warnings[:3])}")
    
    operational_notes = " | ".join(operational_notes_parts) if operational_notes_parts else ""
    
    return {
        "status": "success",
        "timestamp": pd.Timestamp.now().isoformat(),
        "risk_level": risk_level,
        "probability_default_percent": round(prob * 100, 2),
        "binary_prediction": pred,
        "model_confidence_threshold": 0.6,
        "input_features_original": raw_input_dict,
        "input_features_imputed": imputed_data,
        "imputation_log": imputation_log,
        "validation_warnings": validation_warnings,
        "shap_explanation": shap_explanation,
        "llm_explanation": llm_explanation,
        "remediation_suggestion": remediation_suggestion,
        "data_drift_warnings": drift_warnings,
        "operational_notes": operational_notes
    }

# Gemini-specific endpoints removed - AI is now integrated into main prediction flow
# for generating explanations and advice based on SHAP values

@app.post("/predict_risk_batch", response_model=Dict[str, Any])
async def predict_risk_batch(applications: List[DynamicLoanApplication], include_explanations: bool = False):
    """
    Batch prediction endpoint for CSV uploads.
    
    Accepts a list of loan applications and returns predictions for all.
    
    Args:
        applications: List of loan applications (partial data accepted)
        include_explanations: If True, includes SHAP explanations and AI advice (slower)
    
    Returns:
        Batch prediction results with optional explanations
    """
    if dynamic_predictor is None:
        raise HTTPException(
            status_code=503,
            detail={"status": "error", "message": "Dynamic predictor not loaded."}
        )
    
    results = []
    errors = []
    
    for idx, application in enumerate(applications):
        try:
            raw_input_dict = application.model_dump(exclude_none=False)
            
            # Get prediction
            risk_level, prob, pred, imputation_log, imputed_data = dynamic_predictor.predict(
                raw_input_dict,
                flag_threshold=0.6,
                return_imputation_log=True
            )
            
            result = {
                "index": idx,
                "status": "success",
                "risk_level": risk_level,
                "probability_default_percent": round(prob * 100, 2),
                "binary_prediction": pred,
                "input_features": imputed_data,
                "imputation_log": imputation_log
            }
            
            # Add SHAP explanations and AI advice if requested
            if include_explanations:
                try:
                    # Get SHAP values
                    mapped_features = dynamic_predictor.mapper.map_to_model_features(imputed_data)
                    complete_features = dynamic_predictor.mapper.validate_and_fill(mapped_features)
                    shap_values, expected_value, df_features = predictor.get_shap_values(complete_features)
                    
                    # Format SHAP data
                    feature_names = df_features.columns.tolist()
                    if isinstance(shap_values, list):
                        shap_data = shap_values[1]
                    else:
                        shap_data = shap_values
                    
                    try:
                        row = shap_data.tolist()[0]
                    except Exception:
                        row = np.asarray(shap_data).ravel().tolist()
                    
                    shap_explanation = {k: float(v) for k, v in zip(feature_names, row)}
                    
                    # Generate AI explanation
                    llm_result = await generate_llm_explanation(
                        input_data=imputed_data,
                        shap_explanation=shap_explanation,
                        risk_level=risk_level,
                    )
                    
                    result["shap_explanation"] = shap_explanation
                    result["llm_explanation"] = llm_result.get("text") if isinstance(llm_result, dict) else str(llm_result)
                    result["remediation_suggestion"] = llm_result.get("remediation_suggestion") if isinstance(llm_result, dict) else None
                    
                except Exception as e:
                    logger.warning(f"Failed to generate explanation for row {idx}: {e}")
                    result["explanation_error"] = str(e)
            
            results.append(result)
            
        except Exception as e:
            logger.error(f"Batch prediction failed for row {idx}: {e}")
            errors.append({
                "index": idx,
                "status": "error",
                "message": str(e)
            })
    
    return {
        "status": "success",
        "timestamp": pd.Timestamp.now().isoformat(),
        "total_processed": len(applications),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

# Feature engineering endpoints removed - focus is on CSV upload and prediction

@app.get("/db/retraining/status")
def get_retraining_status(db: Session = Depends(get_db)):
    """
    Check if model can be retrained from database data.
    
    Returns readiness status and statistics.
    """
    try:
        retrainer = DatabaseRetrainer()
        status = retrainer.check_retraining_readiness(db)
        
        return {
            "status": "success",
            "retraining": status,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to check retraining status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train/flexible")
async def train_flexible_model(file: UploadFile = File(...)):
    """
    Train a new model from uploaded CSV with flexible column detection.
    
    Automatically detects:
    - Target column (loan_status, default, target, etc.)
    - Numeric features
    - Categorical features
    
    Supports any CSV structure with credit risk data.
    """
    try:
        logger.info(f"Flexible training requested with file: {file.filename}")
        
        # Save uploaded file
        temp_path = Path("data") / f"temp_training_{file.filename}"
        temp_path.parent.mkdir(exist_ok=True)
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Train model
        from backend.services.flexible_training import FlexibleModelTrainer
        trainer = FlexibleModelTrainer()
        result = trainer.train_model(str(temp_path))
        
        # Clean up temp file
        temp_path.unlink()
        
        logger.info(f"Flexible training completed successfully")
        
        return {
            "status": "success",
            "message": "Model trained successfully with flexible column detection",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Flexible training failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Training failed: {str(e)}"
        )


@app.post("/db/retrain")
async def retrain_from_database(
    min_samples: int = 100,
    min_feedback_ratio: float = 0.1,
    test_size: float = 0.2,
    db: Session = Depends(get_db)
):
    """
    Retrain model using data from database.
    
    Requires predictions with actual outcomes (feedback).
    """
    try:
        logger.info("Starting database retraining...")
        
        retrainer = DatabaseRetrainer(min_samples, min_feedback_ratio)
        
        # Check readiness
        readiness = retrainer.check_retraining_readiness(db)
        if not readiness['is_ready']:
            return {
                "status": "not_ready",
                "message": "Not enough data for retraining",
                "readiness": readiness,
                "timestamp": pd.Timestamp.now().isoformat()
            }
        
        # Retrain model
        result = retrainer.retrain_model(db, test_size=test_size, save_model=True)
        
        return {
            "status": "success",
            "message": "Model retrained successfully",
            "result": result,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database retraining failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": f"Retraining failed: {str(e)}"}
        )

@app.post("/db/export_training_data")
def export_training_data(db: Session = Depends(get_db)):
    """
    Export training data from database to CSV file.
    
    Useful for manual model training or analysis.
    """
    try:
        retrainer = DatabaseRetrainer()
        output_path = retrainer.export_training_data(db)
        
        return {
            "status": "success",
            "message": "Training data exported successfully",
            "file_path": output_path,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to export training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/db/import_csv")
async def import_csv_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import CSV data into database.
    
    Accepts CSV file with loan data and actual outcomes.
    """
    try:
        from io import BytesIO
        
        # Read file content
        content = await file.read()
        
        # Read CSV from bytes
        df = pd.read_csv(BytesIO(content))
        
        logger.info(f"Received CSV with {len(df)} rows, {len(df.columns)} columns")
        
        # Import data
        imported_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                # Extract input features
                input_features = {}
                for col in df.columns:
                    if col != 'loan_status' and pd.notna(row[col]):
                        input_features[col] = row[col]
                
                # Get actual outcome
                actual_outcome = int(row['loan_status']) if 'loan_status' in df.columns and pd.notna(row['loan_status']) else None
                
                # Create prediction record
                prediction = DBPrediction(
                    input_features=input_features,
                    risk_level="Unknown",
                    probability_default=0.5,
                    binary_prediction=actual_outcome if actual_outcome is not None else 0,
                    model_type="imported_data",
                    actual_outcome=actual_outcome,
                    created_at=pd.Timestamp.now()
                )
                
                db.add(prediction)
                imported_count += 1
                
                # Commit in batches
                if imported_count % 100 == 0:
                    db.commit()
            
            except Exception as e:
                error_count += 1
                logger.warning(f"Error importing row {idx}: {e}")
        
        # Final commit
        db.commit()
        
        return {
            "status": "success",
            "message": f"Successfully imported {imported_count} rows",
            "imported": imported_count,
            "errors": error_count,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"CSV import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    
# ==================== Database Endpoints ====================

@app.get("/db/health")
def check_database_health():
    """Check database connection status."""
    is_connected = check_connection()
    return {
        "status": "connected" if is_connected else "disconnected",
        "database": "postgresql",
        "message": "Database is operational" if is_connected else "Database connection failed"
    }

@app.get("/db/statistics")
def get_database_statistics(db: Session = Depends(get_db)):
    """Get overall database statistics."""
    try:
        pred_stats = crud.get_prediction_statistics(db)
        app_stats = crud.get_application_statistics(db)
        
        return {
            "status": "success",
            "predictions": pred_stats,
            "applications": app_stats,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/predictions")
def get_predictions_history(
    skip: int = 0,
    limit: int = 100,
    model_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get prediction history from database."""
    try:
        predictions = crud.get_predictions(db, skip=skip, limit=limit, model_type=model_type)
        return {
            "status": "success",
            "count": len(predictions),
            "predictions": [
                {
                    "id": p.id,
                    "risk_level": p.risk_level,
                    "probability_default": p.probability_default,
                    "model_type": p.model_type,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in predictions
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/predictions/{prediction_id}")
def get_prediction_detail(prediction_id: int, db: Session = Depends(get_db)):
    """Get detailed prediction by ID."""
    try:
        prediction = crud.get_prediction(db, prediction_id)
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        return {
            "status": "success",
            "prediction": {
                "id": prediction.id,
                "risk_level": prediction.risk_level,
                "probability_default": prediction.probability_default,
                "binary_prediction": prediction.binary_prediction,
                "model_type": prediction.model_type,
                "input_features": prediction.input_features,
                "explanation": prediction.explanation,
                "key_factors": prediction.key_factors,
                "created_at": prediction.created_at.isoformat() if prediction.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/db/predictions/{prediction_id}/feedback")
def submit_prediction_feedback(
    prediction_id: int,
    actual_outcome: int,
    db: Session = Depends(get_db)
):
    """Submit actual outcome for a prediction (for model improvement)."""
    try:
        prediction = crud.update_prediction_feedback(db, prediction_id, actual_outcome)
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        return {
            "status": "success",
            "message": "Feedback recorded successfully",
            "prediction_id": prediction_id,
            "actual_outcome": actual_outcome
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

# ==================== API Configuration Endpoint ====================

@app.get("/api/config")
def get_api_config():
    """
    Get API configuration status.
    Shows which features are enabled and API key status.
    """
    return {
        "status": "success",
        "shap_explanations": {
            "enabled": ENABLE_SHAP_EXPLANATIONS,
            "has_api_key": bool(GEMINI_API_KEY_PREDICTIONS),
            "operational": ENABLE_SHAP_EXPLANATIONS and bool(GEMINI_API_KEY_PREDICTIONS)
        },
        "chatbot": {
            "enabled": ENABLE_CHATBOT,
            "has_api_key": bool(GEMINI_API_KEY_CHATBOT),
            "operational": ENABLE_CHATBOT and bool(GEMINI_API_KEY_CHATBOT)
        },
        "using_separate_keys": GEMINI_API_KEY_PREDICTIONS != GEMINI_API_KEY_CHATBOT if (GEMINI_API_KEY_PREDICTIONS and GEMINI_API_KEY_CHATBOT) else False,
        "message": "API configuration loaded successfully"
    }

# ==================== API Monitoring Endpoints ====================

@app.get("/api/stats")
def get_api_stats():
    """
    Get API request statistics.
    Shows how many LLM API calls have been made.
    """
    try:
        from backend.utils.api_counter import get_api_counter
        counter = get_api_counter()
        stats = counter.get_stats()
        recent = counter.get_recent_requests(limit=10)
        
        return {
            "status": "success",
            "stats": stats,
            "recent_requests": recent,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get API stats: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/api/stats/reset")
def reset_api_stats():
    """
    Reset API request counters.
    Useful for testing or starting fresh.
    """
    try:
        from backend.utils.api_counter import get_api_counter
        counter = get_api_counter()
        counter.reset()
        
        return {
            "status": "success",
            "message": "API request counters reset",
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to reset API stats: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# ==================== Chatbot Endpoint ====================

@app.post("/chatbot/query")
async def chatbot_query(query_data: Dict[str, str], db: Session = Depends(get_db)):
    """
    Chatbot endpoint to answer questions about the database and system.
    Uses separate API key (GEMINI_API_KEY_CHATBOT) to track usage independently.
    """
    # Check if chatbot is enabled
    if not ENABLE_CHATBOT:
        return {
            "response": "Chatbot is currently disabled. Please contact your administrator.",
            "data": None
        }
    
    try:
        query = query_data.get("query", "").lower()
        logger.info(f"Chatbot query: {query[:50]}...")
        
        # Database statistics
        if any(word in query for word in ["database", "stats", "statistics", "how many"]):
            try:
                pred_stats = crud.get_prediction_statistics(db)
                app_stats = crud.get_application_statistics(db)
                
                response = f"""📊 **Database Statistics**

**Predictions:**
• Total: {pred_stats.get('total', 0):,}
• High Risk: {pred_stats.get('high_risk', 0):,}
• Low Risk: {pred_stats.get('low_risk', 0):,}
• With Feedback: {pred_stats.get('with_feedback', 0):,}

**Applications:**
• Total: {app_stats.get('total', 0):,}
• Pending: {app_stats.get('pending', 0):,}
• Approved: {app_stats.get('approved', 0):,}
• Rejected: {app_stats.get('rejected', 0):,}"""
                
                return {
                    "response": response,
                    "data": {
                        "predictions": pred_stats,
                        "applications": app_stats
                    }
                }
            except Exception as e:
                return {
                    "response": f"I couldn't fetch database statistics. Error: {str(e)}",
                    "data": None
                }
        
        # Recent predictions
        elif any(word in query for word in ["recent", "latest", "last", "predictions"]):
            try:
                predictions = crud.get_predictions(db, limit=5)
                
                if not predictions:
                    return {
                        "response": "No predictions found in the database yet.",
                        "data": None
                    }
                
                response = "🔍 **Recent Predictions:**\n\n"
                for i, pred in enumerate(predictions, 1):
                    response += f"{i}. {pred.risk_level} - {pred.probability_default:.1%}\n"
                    response += f"   Created: {pred.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                
                return {
                    "response": response,
                    "data": {
                        "count": len(predictions),
                        "predictions": [
                            {
                                "id": p.id,
                                "risk_level": p.risk_level,
                                "probability": p.probability_default,
                                "created_at": p.created_at.isoformat() if p.created_at else None
                            }
                            for p in predictions
                        ]
                    }
                }
            except Exception as e:
                return {
                    "response": f"I couldn't fetch recent predictions. Error: {str(e)}",
                    "data": None
                }
        
        # API usage statistics
        elif any(word in query for word in ["api usage", "api calls", "requests", "llm usage", "api stats"]):
            try:
                from backend.utils.api_counter import get_api_counter
                counter = get_api_counter()
                stats = counter.get_stats()
                recent = counter.get_recent_requests(limit=5)
                
                response = f"""🔔 **LLM API Usage Statistics**

**Session Stats:**
• Total Requests: {stats['total_requests']}
• Session Duration: {stats['session_duration_seconds']:.0f} seconds
• Requests/Minute: {stats['requests_per_minute']:.2f}

**By Provider:**"""
                
                for provider_model, count in stats['requests_by_provider'].items():
                    response += f"\n• {provider_model}: {count} requests"
                
                if recent:
                    response += "\n\n**Recent Requests:**"
                    for req in recent[-5:]:
                        status_icon = "✅" if req['success'] else "❌"
                        response += f"\n{status_icon} {req['provider']} - {req['endpoint']}"
                
                response += "\n\nNote: Counter resets when backend restarts."
                
                return {
                    "response": response,
                    "data": stats
                }
            except Exception as e:
                return {
                    "response": f"I couldn't fetch API usage stats. Error: {str(e)}",
                    "data": None
                }
        
        # Model performance
        elif any(word in query for word in ["model", "performance", "accuracy", "metrics"]):
            try:
                # Get retraining status
                retrainer = DatabaseRetrainer()
                status = retrainer.check_retraining_readiness(db)
                
                response = f"""📈 **Model Performance**

**Training Data:**
• Total Predictions: {status['total_predictions']:,}
• With Feedback: {status['feedback_count']:,}
• Feedback Ratio: {status['feedback_ratio']:.1%}

**Retraining Status:**
• Ready: {'✅ Yes' if status['is_ready'] else '❌ No'}
• Min Samples Required: {status['min_samples_required']}
• Samples Needed: {status['samples_needed']}

The model is {'ready' if status['is_ready'] else 'not ready'} for retraining."""
                
                return {
                    "response": response,
                    "data": status
                }
            except Exception as e:
                return {
                    "response": f"I couldn't fetch model performance. Error: {str(e)}",
                    "data": None
                }
        
        # Help / How to use
        elif any(word in query for word in ["help", "how", "use", "guide", "tutorial"]):
            response = """❓ **How to Use the System**

**CSV Upload:**
1. Click "Predictions" view
2. Upload your CSV file
3. Navigate through rows or batch process
4. Download results

**Admin Panel:**
1. Click "Admin" button
2. Import Data: Upload CSV with loan_status column
3. Retrain Model: Click when ready (100+ samples)
4. Reload Model: Activate new model

**Chatbot (Me!):**
• Ask about database statistics
• Check recent predictions
• View model performance
• Get help and guidance

**Quick Commands:**
• "show database statistics"
• "show recent predictions"
• "show model performance"
• "how do I import data?"
• "how do I retrain the model?"

What would you like to know more about?"""
            
            return {
                "response": response,
                "data": None
            }
        
        # Import data help
        elif any(word in query for word in ["import", "upload", "csv"]):
            response = """📥 **How to Import Data**

**Via Admin Panel:**
1. Click "🔧 Admin" button
2. Go to "Import Data" tab
3. Click upload area or drag & drop CSV
4. Click "Import Data" button
5. Wait for completion

**CSV Requirements:**
• Must have `loan_status` column (0 or 1)
• Other columns: person_age, person_income, loan_amnt, etc.
• Missing values are OK (will be imputed)

**After Import:**
• Data is stored in database
• Can be used for retraining
• Check "Status" tab to verify

Need help with retraining? Just ask!"""
            
            return {
                "response": response,
                "data": None
            }
        
        # Retrain help
        elif any(word in query for word in ["retrain", "training", "train model"]):
            response = """🔄 **How to Retrain the Model**

**Requirements:**
• At least 100 predictions in database
• At least 1% with actual outcomes (feedback)

**Steps:**
1. Go to Admin Panel → "Retrain Model" tab
2. Check readiness status
3. Click "Start Retraining" button
4. Wait 30-60 seconds
5. Click "Reload Model in API"

**What Happens:**
• Model trains on database data
• Uses 80/20 train/test split
• Calculates accuracy and AUC
• Saves new model version
• Updates manifest

**After Retraining:**
• New model is ready to use
• Check metrics (accuracy, AUC)
• Test with predictions

Want to check if you're ready to retrain? Ask me "show model performance"!"""
            
            return {
                "response": response,
                "data": None
            }
        
        # Default response
        else:
            response = """I can help you with:

• 📊 **Database statistics** - "show database statistics"
• 🔍 **Recent predictions** - "show recent predictions"
• 📈 **Model performance** - "show model performance"
• 📥 **Import data** - "how do I import data?"
• 🔄 **Retrain model** - "how do I retrain the model?"
• ❓ **General help** - "help"

What would you like to know?"""
            
            return {
                "response": response,
                "data": None
            }
    
    except Exception as e:
        logger.error(f"Chatbot query failed: {e}")
        return {
            "response": f"Sorry, I encountered an error: {str(e)}",
            "data": None
        }


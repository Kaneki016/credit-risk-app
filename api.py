# api.py
import joblib
import pandas as pd
import numpy as np
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from predictor import CreditRiskPredictor
from retrain_agent import retrain_if_needed
import logging
import requests
import os  # REQUIRED for os.getenv()
from dotenv import load_dotenv  # REQUIRED to load the .env file
 

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
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
    
# --- 2. Define the Pydantic Input Schema ---
# This Pydantic model ensures incoming JSON data from n8n is correct.
# It MUST match the features expected by your Streamlit/Predictor input dictionary.
class LoanApplication(BaseModel):
    # Core numerical features
    person_age: int = Field(..., description="Age of the borrower (years).", example=30)
    person_income: float = Field(..., description="Annual Income.", example=75000.0)
    person_emp_length: float = Field(..., description="Employment length (months).", example=60.0)
    loan_amnt: float = Field(..., description="Loan amount requested.", example=12000.0)
    loan_int_rate: float = Field(..., description="Loan interest rate (%).", example=11.99)
    loan_percent_income: float = Field(..., description="Loan amount as % of income.", example=0.25)
    cb_person_cred_hist_length: int = Field(..., description="Credit history length (years).", example=5)
    
    # Raw categorical inputs (these will be one-hot encoded by the predictor)
    home_ownership: str = Field(..., description="Home Ownership (RENT, OWN, MORTGAGE, OTHER).", example="RENT")
    loan_intent: str = Field(..., description="Purpose of the loan.", example="DEBTCONSOLIDATION")
    loan_grade: str = Field(..., description="Loan Grade (A-G).", example="B")
    default_on_file: str = Field(..., description="Previous Default on File (Y/N).", example="N")

# --- 3. Initialize FastAPI Application ---
app = FastAPI(
    title="Agentic Credit Risk Prediction API for n8n",
    version="1.0.0",
    description="Serves the XGBoost credit risk model for automated workflows (n8n)."
)

# --- NEW: Function to Call LLM for Explanation ---
def generate_llm_explanation(
    input_data: Dict[str, Any], 
    shap_explanation: Dict[str, float], 
    risk_level: str
) -> str:
    """Sends SHAP results and application data to Gemini for natural language explanation."""
    
    # 1. Prepare the prompt with the most impactful features
    # Convert SHAP dict to a DataFrame, sort by absolute value, and take the top 5
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
    
    # 2. Build the API Payload
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {
            "parts": [{"text": "You are a friendly, expert financial analyst explaining complex risk to a non-expert."}]
        }
    }
    
    # 3. Make the API Call (using synchronous requests for simplicity)
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", 
            headers=headers, 
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        
        # 4. Extract Text
        result = response.json()
        text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'LLM explanation unavailable.')
        return text

    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
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
def predict_risk(application: LoanApplication):
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
        
        # Handle different SHAP value formats
        if isinstance(shap_values, list):
            # For multi-class output (returns list of arrays)
            shap_data = shap_values[0] if len(shap_values) == 1 else shap_values[1]
        else:
            # For single-class output (returns single array)
            shap_data = shap_values
            
        shap_explanation = dict(zip(feature_names, shap_data.tolist()[0]))

    except Exception as e:
        logger.error(f"Prediction or SHAP calculation failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail={"status": "error", "message": f"Internal prediction error: {str(e)}"}
        )

    # --- 6. Generate LLM Explanation ---
    llm_explanation = generate_llm_explanation(
        input_data=raw_input_dict,
        shap_explanation=shap_explanation,
        risk_level=risk_level
    )
    
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
        "llm_explanation": llm_explanation
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
    

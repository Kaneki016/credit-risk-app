# app.py


import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import requests
from streamlit_lottie import st_lottie
from config import N8N_WEBHOOK_URL, LOG_PATH, FLAG_THRESHOLD

# Configure logging early so libraries can use logging
from logging_setup import configure_logging
configure_logging()

# Initialize predictor
from predictor import CreditRiskPredictor

predictor = None
load_error = None
try:
    predictor = CreditRiskPredictor()
except Exception as e:
    # Save the exception and continue so the Streamlit app can show a helpful message
    load_error = e

LOG_PATH = "prediction_logs.csv"
FLAG_THRESHOLD = 0.6  # Flag if probability of default > 60%

st.set_page_config(page_title="Credit Risk Agentic AI", layout="wide")


# Sidebar with Lottie animation and info
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

lottie_url = "https://assets2.lottiefiles.com/packages/lf20_4kx2q32n.json"  # finance animation
lottie_json = load_lottieurl(lottie_url)

with st.sidebar:
    if lottie_json is not None:
        try:
            st_lottie(lottie_json, height=120, key="credit-lottie")
        except Exception:
            # fallback: simple header if lottie fails
            st.header("Credit Risk App")
    else:
        st.header("Credit Risk App")
    st.markdown("# 💼 Credit Risk App")
    st.markdown(
        "<span style='color:#43a047;font-weight:bold;'>AI-powered credit risk prediction with SHAP explainability.</span>",
        unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Created by Kaneki016**")


# Flashy CSS: gradient background, custom font, animated result box
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
html, body, [class*="css"]  {
    font-family: 'Montserrat', sans-serif !important;
}
.main {
    background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%) !important;
}
.block-container {
    padding-top: 2rem;
}
.result-box {
    background: linear-gradient(90deg, #f0f2f6 60%, #e0eafc 100%);
    border-radius: 0.7rem;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    border: 2px solid #e0e0e0;
    box-shadow: 0 4px 24px 0 rgba(60,60,60,0.08);
    animation: fadeIn 1.2s cubic-bezier(.4,0,.2,1);
}
.risk-high {background: linear-gradient(90deg, #ffeaea 60%, #ffdde1 100%); border-left: 8px solid #e53935; animation: pulse 1.2s infinite alternate;}
.risk-borderline {background: linear-gradient(90deg, #fff8e1 60%, #fffde4 100%); border-left: 8px solid #ffb300;}
.risk-low {background: linear-gradient(90deg, #e8f5e9 60%, #e0f7fa 100%); border-left: 8px solid #43a047;}
@keyframes fadeIn {from {opacity:0;transform:translateY(30px);} to {opacity:1;transform:translateY(0);}}
@keyframes pulse {0% {box-shadow:0 0 0 0 #e5393533;} 100% {box-shadow:0 0 16px 8px #e5393533;}}
.stButton>button {background: linear-gradient(90deg,#43a047,#1976d2); color:white; font-weight:bold; border-radius:8px; border:none;}
.stButton>button:hover {background: linear-gradient(90deg,#1976d2,#43a047);}
.st-expanderHeader {font-size:1.1rem; color:#1976d2;}
</style>
""", unsafe_allow_html=True)


st.markdown("<h1>💼 <span style='color:#1976d2;'>Credit Risk Prediction</span></h1>", unsafe_allow_html=True)
st.markdown(
    "<span style='color: #888; font-size:1.1rem;'>Agentic AI with <b>SHAP Explainability</b></span>", unsafe_allow_html=True
)
st.markdown("<hr style='margin-top:0.5rem;margin-bottom:1.5rem;border:0;border-top:2px solid #1976d2;'>", unsafe_allow_html=True)



# Group input fields in columns and expanders, with emoji and color
with st.expander("📝 Enter Applicant Information", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("👤 Person Age", min_value=18, max_value=100, value=30)
        emp_length = st.number_input("💼 Employment Length (months)", value=12.0)
        cred_hist = st.number_input("📅 Credit History Length (years)", value=5)
    with col2:
        income = st.number_input("💰 Annual Income", value=50000)
        percent_income = st.number_input("📊 Loan % of Income", value=0.25)
        loan_amnt = st.number_input("💵 Loan Amount", value=10000)
    with col3:
        home = st.selectbox("🏠 Home Ownership", ["RENT", "OWN", "MORTGAGE", "OTHER"])
        intent = st.selectbox("🎯 Loan Intent", ["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"])
        grade = st.selectbox("🏅 Loan Grade", ["A", "B", "C", "D", "E", "F", "G"])
        loan_rate = st.number_input("📈 Loan Interest Rate (%)", value=10.0)
        default_on_file = st.selectbox("⚠️ Previous Default on File", ["Y", "N"])


st.markdown("<hr style='margin-top:1.5rem;margin-bottom:1.5rem;border:0;border-top:2px dashed #43a047;'>", unsafe_allow_html=True)

# Predict button
if st.button("✨ Predict Credit Risk! ✨", use_container_width=True):
    # ----------------------------------------------------
    # 1. BUILD RAW INPUT PAYLOAD (MUST MATCH N8N WEBHOOK)
    # ----------------------------------------------------
    # The payload MUST match the Pydantic/Webhook structure exactly
    # Ensure correct data types before sending to API
    input_payload = {
        "person_age": int(age),  # Ensure integer
        "person_income": float(income),
        "person_emp_length": float(emp_length),
        "loan_amnt": float(loan_amnt),
        "loan_int_rate": float(loan_rate),
        "loan_percent_income": float(percent_income),
        "cb_person_cred_hist_length": int(cred_hist),  # Ensure integer
        "home_ownership": str(home).upper(),  # Ensure uppercase string
        "loan_intent": str(intent).upper(),
        "loan_grade": str(grade).upper(),
        "default_on_file": str(default_on_file).upper()
    }

    st.markdown("<h3>🚀 Sending Data to Agentic Workflow...</h3>", unsafe_allow_html=True)

    try:
        # ----------------------------------------------------
        # 2. CALL THE N8N WEBHOOK (HTTP POST)
        # ----------------------------------------------------
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=input_payload,
            timeout=30 # Increased timeout for the full workflow execution
        )
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # The n8n Webhook should be configured to return a response after the 
        # HTTP Request to FastAPI finishes.
        # The response structure we expect is the output of the FastAPI API.
        webhook_response = response.json()
        
        # Normalize common n8n / webhook wrappers
        def normalize_webhook_response(resp):
            """Unwrap common n8n wrappers so the Streamlit app can handle different webhook outputs.

            - n8n may wrap the real payload inside arrays or inside keys like 'body' or 'data'.
            - This helper tries common unwrap patterns and returns a dict-like payload.
            """
            # If it's a list with one element, unwrap it
            if isinstance(resp, list) and len(resp) == 1:
                resp = resp[0]

            # If n8n returns something like { "body": {...} } or { "data": {...} }, prefer the nested dict
            for key in ("body", "data", "json", "payload"):
                if isinstance(resp, dict) and key in resp and isinstance(resp[key], (dict, list)):
                    # If nested is a list of length 1, unwrap that too
                    nested = resp[key]
                    if isinstance(nested, list) and len(nested) == 1:
                        nested = nested[0]
                    if isinstance(nested, dict):
                        return nested

            # Otherwise return as-is if it's already a dict
            return resp

        webhook_response = normalize_webhook_response(webhook_response)

        # Validate response structure
        required_fields = ['risk_level', 'probability_default_percent', 'binary_prediction', 'shap_explanation']
        if not isinstance(webhook_response, dict) or not all(field in webhook_response for field in required_fields):
            missing_fields = []
            if isinstance(webhook_response, dict):
                missing_fields = [field for field in required_fields if field not in webhook_response]
            # Provide diagnostics: show raw response and help on common shapes
            st.error("Incomplete response from API. See raw response for debugging.")
            st.markdown("**Raw webhook response:**")
            try:
                st.json(webhook_response)
            except Exception:
                st.write(str(webhook_response))

            # Also log to console for deeper inspection
            print("[DEBUG] Raw webhook response:", repr(webhook_response))
            raise ValueError(f"Incomplete response from API. Missing fields: {missing_fields}")

        # Extract results from the response
        risk_level = webhook_response['risk_level']
        prob = webhook_response['probability_default_percent'] / 100  # Convert back to 0-1 range for display
        pred = webhook_response['binary_prediction']
        
        # Extract the NEW LLM field
        llm_explanation = webhook_response.get('llm_explanation', 'LLM explanation not returned.')

        # Validate probability range
        if not 0 <= webhook_response['probability_default_percent'] <= 100:
            raise ValueError(f"Invalid probability value: {webhook_response['probability_default_percent']}%")
        
        # The SHAP explanation data is nested in the response
        shap_explanation_data = webhook_response['shap_explanation']
        
        # Validate SHAP data
        if not isinstance(shap_explanation_data, dict) or not shap_explanation_data:
            raise ValueError("Invalid or empty SHAP explanation data received")
        
        # ----------------------------------------------------
        # 3. DISPLAY RESULTS & SHAP (Using data from n8n)
        # ----------------------------------------------------

        # Determine CSS class for display
        risk_class = risk_level.split()[0].lower() + "-" + risk_level.split()[1].lower()

        st.markdown("<h4 style='color:#1976d2;'>🎉 Prediction Result</h4>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='result-box {risk_class}'>"
            f"<span style='font-size:1.3rem;'><b>Risk Level:</b> {risk_level}</span><br>"
            f"<span style='font-size:1.1rem;'><b>Probability of Default:</b> <span style='color:#1976d2;'>{round(prob * 100, 2)}%</span></span>"
            f"</div>", unsafe_allow_html=True
        )
        st.balloons()
        st.success("✅ Agentic Workflow Completed: Logging, Decision, and Action Performed.")

        # SHAP Explanation (Reconstruct force plot using the SHAP data received)
        st.markdown("<hr style='margin-top:1.5rem;margin-bottom:1.5rem;border:0;border-top:2px dashed #1976d2;'>", unsafe_allow_html=True)
        st.markdown("<h3>🔎 <span style='color:#1976d2;'>Why This Prediction?</span></h3>", unsafe_allow_html=True)
        
        # --- NEW: Display LLM Explanation First ---
        st.subheader("Natural Language Explanation:")
        st.info(llm_explanation) # Use st.info for a prominent box

        # --- Display SHAP Dataframe (for visual inspection/audit) ---
        st.markdown("<h4>Top Feature Contributions (SHAP Audit Data):</h4>", unsafe_allow_html=True)
        st.dataframe(pd.Series(shap_explanation_data).sort_values(ascending=False).head(5).rename("SHAP Value").to_frame().style.format("{:.4f}"))
        st.info("The Agentic System performed all logging and decision logic successfully.")

    except requests.exceptions.RequestException as e:
        st.error("Error communicating with the Agentic AI Backend (n8n/FastAPI).")
        if isinstance(e, requests.exceptions.Timeout):
            st.error("Request timed out. The n8n workflow may be taking too long.")
        elif isinstance(e, requests.exceptions.ConnectionError):
            st.error("Could not connect to the n8n server. Please check if n8n is running.")
        else:
            st.error(f"API request failed: {str(e)}")
        st.exception(e)
    except ValueError as e:
        st.error("Invalid data received from the API")
        st.exception(e)
    except KeyError as e:
        st.error("Unexpected API response structure")
        st.exception(e)
    except Exception as e:
        st.error("An unexpected error occurred while processing the response.")
        st.exception(e)
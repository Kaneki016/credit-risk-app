# app.py


import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import shap
import matplotlib.pyplot as plt
import requests
from streamlit_lottie import st_lottie

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
    if load_error is not None or predictor is None:
        st.error(
            "Model artifacts failed to load. See details below and retrain the model before using the app."
        )
        st.exception(load_error)
        st.info("To retrain the model run: `python credit_model.py` or `python retrain_agent.py` in this project root.")
        st.stop()
    # Build feature dict for model
    input_dict = {
        "person_age": age,
        "person_income": income,
        "person_emp_length": emp_length,
        "loan_amnt": loan_amnt,
        "loan_int_rate": loan_rate,
        "loan_percent_income": percent_income,
        "cb_person_cred_hist_length": cred_hist,
        f"person_home_ownership_{home}": 1,
        f"loan_intent_{intent}": 1,
        f"loan_grade_{grade}": 1,
        f"cb_person_default_on_file_{default_on_file}": 1
    }

    # Make prediction using the predictor
    risk_level, prob, pred = predictor.predict(input_dict, FLAG_THRESHOLD)
    risk_class = risk_level.split()[0].lower() + "-" + risk_level.split()[1].lower()


    # Display result with animated colored box
    st.markdown("<h4 style='color:#1976d2;'>🎉 Prediction Result</h4>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='result-box {risk_class}'>"
        f"<span style='font-size:1.3rem;'><b>Risk Level:</b> {risk_level}</span><br>"
        f"<span style='font-size:1.1rem;'><b>Probability of Default:</b> <span style='color:#1976d2;'>{round(prob * 100, 2)}%</span></span>"
        f"</div>", unsafe_allow_html=True
    )
    st.balloons()


    # SHAP Explanation (guarded)
    st.markdown("<hr style='margin-top:1.5rem;margin-bottom:1.5rem;border:0;border-top:2px dashed #1976d2;'>", unsafe_allow_html=True)
    st.markdown("<h3>🔎 <span style='color:#1976d2;'>Why This Prediction?</span></h3>", unsafe_allow_html=True)
    
    # Get SHAP values from predictor
    shap_values, expected_value, df_input = predictor.get_shap_values(input_dict)

    shap.initjs()
    plt.figure(figsize=(10, 4))
    shap.force_plot(expected_value, shap_values[0], df_input, matplotlib=True, show=False)
    st.pyplot(plt.gcf())

    # Log prediction
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "prediction": int(pred),
        "probability": prob,
        "risk_level": risk_level,
        "input_data": str(input_dict)
    }

    log_df = pd.DataFrame([log_data])
    if not os.path.exists(LOG_PATH):
        log_df.to_csv(LOG_PATH, index=False)
    else:
        log_df.to_csv(LOG_PATH, mode="a", index=False, header=False)

    st.success("✅ Prediction logged successfully.")

# app.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import shap
import matplotlib.pyplot as plt

# Load model and supporting files
model = joblib.load("credit_risk_model.pkl")
scaler = joblib.load("scaler.pkl")
feature_names = joblib.load("feature_names.pkl")

LOG_PATH = "prediction_logs.csv"
FLAG_THRESHOLD = 0.6  # Flag if probability of default > 60%

st.set_page_config(page_title="Credit Risk Agentic AI", layout="wide")
st.title("💼 Credit Risk Prediction (Agentic AI with SHAP Explainability)")

# Input fields
age = st.number_input("Person Age", min_value=18, max_value=100, value=30)
income = st.number_input("Annual Income", value=50000)
home = st.selectbox("Home Ownership", ["RENT", "OWN", "MORTGAGE", "OTHER"])
emp_length = st.number_input("Employment Length (in months)", value=12.0)
intent = st.selectbox("Loan Intent", ["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"])
grade = st.selectbox("Loan Grade", ["A", "B", "C", "D", "E", "F", "G"])
loan_amnt = st.number_input("Loan Amount", value=10000)
loan_rate = st.number_input("Loan Interest Rate (%)", value=10.0)
percent_income = st.number_input("Loan % of Income", value=0.25)
default_on_file = st.selectbox("Previous Default on File", ["Y", "N"])
cred_hist = st.number_input("Credit History Length (years)", value=5)

# Predict button
if st.button("🔍 Predict Credit Risk"):
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

    # Fill all model columns (missing = 0)
    input_full = {col: input_dict.get(col, 0) for col in feature_names}
    df_input = pd.DataFrame([input_full])

    # Scale numeric input
    scaled = scaler.transform(df_input)

    # Make prediction
    pred = model.predict(scaled)[0]
    prob = model.predict_proba(scaled)[0][1]

    # Categorize risk
    if prob > FLAG_THRESHOLD:
        risk_level = "High Risk 🔴"
    elif prob > 0.4:
        risk_level = "Borderline Risk 🟠"
    else:
        risk_level = "Low Risk 🟢"

    # Display result
    st.subheader("Prediction Result")
    st.write(f"**Risk Level:** {risk_level}")
    st.write(f"**Probability of Default:** {round(prob * 100, 2)}%")

    # SHAP Explanation
    st.subheader("🔎 Why This Prediction?")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(scaled)
    expected_value = explainer.expected_value

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

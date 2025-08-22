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
from prophet import Prophet
import plotly.express as px

# ===============================
# Load models and config
# ===============================
model = joblib.load("xgclassifier_model.pkl")
scaler = joblib.load("scaler.pkl")
feature_names = joblib.load("feature_names.pkl")

LOG_PATH = "prediction_logs.csv"
FORECAST_MODEL_PATH = "applicant_forecast_model.pkl"
FLAG_THRESHOLD = 0.6  # Flag if probability of default > 60%

st.set_page_config(page_title="Loan Credit Risk Agentic AI", layout="wide")

# ===============================
# Sidebar with Lottie animation
# ===============================
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_url = "https://assets2.lottiefiles.com/packages/lf20_4kx2q32n.json"
lottie_json = load_lottieurl(lottie_url)

with st.sidebar:
    st_lottie(lottie_json, height=120, key="credit-lottie")
    st.markdown("# 💼 Credit Risk App")
    st.markdown(
        "<span style='color:#43a047;font-weight:bold;'>AI-powered credit risk prediction with SHAP explainability.</span>",
        unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Created by Kaneki016**")

# ===============================
# Tabs: Prediction | Forecasting
# ===============================
tab1, tab2 = st.tabs(["📊 Credit Risk Prediction", "🔮 Applicant Forecasting"])

# ===============================
# TAB 1: Credit Risk Prediction
# ===============================
with tab1:
    st.markdown("<h1>💼 <span style='color:#1976d2;'>Credit Risk Prediction</span></h1>", unsafe_allow_html=True)

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

    if st.button("✨ Predict Credit Risk! ✨", use_container_width=True):
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

        # Fill missing columns with 0
        input_full = {col: input_dict.get(col, 0) for col in feature_names}
        df_input = pd.DataFrame([input_full])

        # Scale and predict
        scaled = scaler.transform(df_input)
        pred = model.predict(scaled)[0]
        prob = model.predict_proba(scaled)[0][1]

        # Risk categorization
        if prob > FLAG_THRESHOLD:
            risk_level = "High Risk 🔴"
            risk_class = "risk-high"
        elif prob > 0.4:
            risk_level = "Borderline Risk 🟠"
            risk_class = "risk-borderline"
        else:
            risk_level = "Low Risk 🟢"
            risk_class = "risk-low"

        st.markdown("<h4 style='color:#1976d2;'>🎉 Prediction Result</h4>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='result-box {risk_class}'>"
            f"<span style='font-size:1.3rem;'><b>Risk Level:</b> {risk_level}</span><br>"
            f"<span style='font-size:1.1rem;'><b>Probability of Default:</b> <span style='color:#1976d2;'>{round(prob * 100, 2)}%</span></span>"
            f"</div>", unsafe_allow_html=True
        )
        st.balloons()

        # SHAP explanation
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(scaled)
        expected_value = explainer.expected_value
        shap.initjs()
        plt.figure(figsize=(10, 4))
        shap.force_plot(expected_value, shap_values[0], df_input, matplotlib=True, show=False)
        st.pyplot(plt.gcf())

        # Logging
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

# ===============================
# TAB 2: Applicant Forecasting
# ===============================
with tab2:
    st.markdown("<h1>🔮 <span style='color:#1976d2;'>Applicant Forecasting</span></h1>", unsafe_allow_html=True)

    # Load and prepare applicant count data
    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Count monthly applicants (live aggregation)
        monthly_counts = df.groupby(df["timestamp"].dt.to_period("M")).size().to_timestamp()
        df_counts = monthly_counts.reset_index()
        df_counts.columns = ["ds", "y"]

        # Train or update forecast model every time data changes
        forecast_model = Prophet()
        forecast_model.fit(df_counts)

        # Forecast next 3 months
        future = forecast_model.make_future_dataframe(periods=3, freq="M")
        forecast = forecast_model.predict(future)

        # Rename columns for non-professional users
        forecast_result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(3)
        forecast_result = forecast_result.rename(columns={
            "ds": "Date",
            "yhat": "Predicted Applicants",
            "yhat_lower": "Min Expected",
            "yhat_upper": "Max Expected"
        })
        forecast_result["Predicted Applicants"] = forecast_result["Predicted Applicants"].round().astype(int)
        forecast_result["Min Expected"] = forecast_result["Min Expected"].round().astype(int)
        forecast_result["Max Expected"] = forecast_result["Max Expected"].round().astype(int)

        # Show history
        st.markdown("### 📊 Applicant History")
        st.line_chart(df_counts.set_index("ds")["y"])

        # Show forecast
        st.markdown("### 🔮 Forecast (Next 3 Months)")
        st.dataframe(forecast_result)

        # Plot forecast with plotly
        fig = px.line(forecast_result, x="Date", y="Predicted Applicants", title="Applicant Forecast")
        fig.add_scatter(x=forecast_result["Date"], y=forecast_result["Max Expected"], mode="lines", line=dict(dash="dot"), name="Max Expected")
        fig.add_scatter(x=forecast_result["Date"], y=forecast_result["Min Expected"], mode="lines", line=dict(dash="dot"), name="Min Expected")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠️ No applicant data found. Please make some predictions first to generate logs.")
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
import openai
openai.api_key = st.secrets["openai_key"]

# Load model and supporting files

model = joblib.load("credit_risk_model.pkl")
scaler = joblib.load("scaler.pkl")
feature_names = joblib.load("feature_names.pkl")

LOG_PATH = "prediction_logs.csv"
FLAG_THRESHOLD = 0.6  # Flag if probability of default > 60%

st.set_page_config(page_title="Credit Risk Agentic AI", layout="wide")

# Sidebar with Lottie animation and info
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_url = "https://assets2.lottiefiles.com/packages/lf20_4kx2q32n.json"  # finance animation
lottie_json = load_lottieurl(lottie_url)

with st.sidebar:
    st_lottie(lottie_json, height=120, key="credit-lottie")
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
        risk_class = "risk-high"
    elif prob > 0.4:
        risk_level = "Borderline Risk 🟠"
        risk_class = "risk-borderline"
    else:
        risk_level = "Low Risk 🟢"
        risk_class = "risk-low"


    # Display result with animated colored box
    st.markdown("<h4 style='color:#1976d2;'>🎉 Prediction Result</h4>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='result-box {risk_class}'>"
        f"<span style='font-size:1.3rem;'><b>Risk Level:</b> {risk_level}</span><br>"
        f"<span style='font-size:1.1rem;'><b>Probability of Default:</b> <span style='color:#1976d2;'>{round(prob * 100, 2)}%</span></span>"
        f"</div>", unsafe_allow_html=True
    )
    st.balloons()


    # SHAP Explanation
    st.markdown("<hr style='margin-top:1.5rem;margin-bottom:1.5rem;border:0;border-top:2px dashed #1976d2;'>", unsafe_allow_html=True)
    st.markdown("<h3>🔎 <span style='color:#1976d2;'>Why This Prediction?</span></h3>", unsafe_allow_html=True)
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
    
    # Business explanation using OpenAI
    st.markdown("<hr style='margin-top:1.5rem;margin-bottom:1rem;border:0;border-top:2px dashed #43a047;'>", unsafe_allow_html=True)
    st.markdown("<h3>📄 <span style='color:#1976d2;'>Business Explanation Report</span></h3>", unsafe_allow_html=True)
    
    # Top SHAP features
    top_features = sorted(zip(df_input.columns, shap_values[0]), key=lambda x: abs(x[1]), reverse=True)[:5]
    top_factors_text = "\n".join([f"- {f}: SHAP impact {round(v, 3)}" for f, v in top_features])
    
    # Construct input summary
    input_summary = "\n".join([f"{k}: {v}" for k, v in input_dict.items()])
    
    # Prompt to GPT
    prompt = f"""
    You are a business analyst writing a structured credit risk analysis report for a loan applicant.
    
    Structure the report into the following sections:
    1. Summary of Risk Level
    2. Key Contributing Factors
    3. Applicant Profile Insights
    4. Recommendations or Next Steps
    
    Avoid technical terms like SHAP or model weights. Focus on explaining how applicant characteristics contribute to the credit risk using business language in point form and start with -.
    
    **Prediction Summary:**
    - Risk Level: {risk_level}
    - Probability of Default: {round(prob * 100, 2)}%
    
    **Top Factors Influencing Risk:**
    {top_factors_text}
    
    **Applicant Information:**
    {input_summary}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional business analyst explaining credit risk to executives."},
                {"role": "user", "content": prompt}
            ]
        )
        business_explanation = response['choices'][0]['message']['content']
        st.markdown("#### 📝 Business Report:")

        # Reformat GPT-generated response
        def style_report_sections(text):
            styled_lines = []
            lines = text.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("- "):
                    styled_lines.append(f"🔸 {line}")
                elif line == "":
                    styled_lines.append("")
                else:
                    styled_lines.append(line)
            return "\n\n".join(styled_lines)
    
        formatted_report = style_report_sections(business_explanation)
        st.markdown(formatted_report, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Failed to generate business report: {e}")
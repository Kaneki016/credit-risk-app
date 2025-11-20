import json
import logging
import os
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from backend.utils.ai_client import get_ai_client

logger = logging.getLogger(__name__)

# Feature toggles
ENABLE_SHAP_EXPLANATIONS = os.getenv("ENABLE_SHAP_EXPLANATIONS", "true").lower() == "true"


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
        return {
            "text": "AI explanations disabled (feature toggle off).",
            "raw": "",
            "remediation_suggestion": None,
            "error": "disabled",
        }

    # Use AI client with retry logic and request counting
    ai_client = get_ai_client()

    if not ai_client.is_available():
        logger.warning("No AI API key set; skipping LLM call and returning placeholder explanation.")
        return {
            "text": "LLM explanation disabled (no API key).",
            "raw": "",
            "remediation_suggestion": None,
            "error": "no_api_key",
        }

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
                "fallback_used": True,
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

        return {"text": explanation_text, "raw": result.get("raw", ""), "remediation_suggestion": remediation}

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
            "fallback_used": True,
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
                concerns.append(
                    f"the requested loan amount represents {loan_pct*100:.0f}% of annual income, which is significantly high"
                )
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
                    explanation += (
                        f"The most significant factors contributing to this decision are: {', '.join(top_factor_names)}. "
                    )

            explanation += (
                "We recommend reviewing the application details and considering risk mitigation measures before approval."
            )

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
        suggestions.append(
            "Applicant has a previous default on file — require a co-signer, collateral, or significantly reduce the requested amount."
        )

    if loan_pct is not None and loan_pct > 0.35:
        if income:
            suggested = int(max(0, income * 0.30))
            suggestions.append(
                f"Requested loan equals {loan_pct*100:.0f}% of income — consider reducing the loan to ~${suggested:,} (≈30% of income) or offering a longer term."
            )
        else:
            suggestions.append(
                "Requested loan is a large share of income — consider reducing the amount or verifying income documentation."
            )

    if loan_amnt is not None and income is not None and loan_amnt > income * 0.5:
        suggestions.append(
            f"Loan amount (${int(loan_amnt):,}) is >50% of annual income; consider reducing amount or requiring collateral/co-signer."
        )

    if loan_rate is not None and loan_rate >= 15:
        suggestions.append(
            "Loan interest rate is high; consider offering a lower rate, longer term, or requiring additional assurances (collateral/co-signer)."
        )

    if cred_hist is not None and cred_hist < 2:
        suggestions.append(
            "Short credit history — consider requiring a guarantor or additional documentation, or offer a smaller secured loan."
        )
    if emp_length is not None and emp_length < 6:
        suggestions.append(
            "Limited recent employment duration — consider verifying employment stability or requiring a co-signer."
        )

    if not suggestions and top_feats:
        top_name, top_val = top_feats[0]
        if "loan_amnt" in top_name or "loan_percent_income" in top_name:
            suggestions.append("Top risk factor is loan size — reduce requested amount or increase downpayment.")
        elif "person_income" in top_name:
            suggestions.append("Top risk factor is low income — require income verification or lower the loan amount.")
        elif "loan_int_rate" in top_name:
            suggestions.append("Top risk factor is interest rate — consider presenting refinancing or longer term options.")
        else:
            suggestions.append(
                "Top contributing factors indicate elevated risk; consider reducing exposure (smaller loan), requiring collateral/co-signer, or additional underwriting checks."
            )

    final = " ".join(suggestions)
    if len(final) > 400:
        final = final[:400].rsplit(".", 1)[0] + "."
    return final or None

import json
import logging
import os
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from backend.api.routes.model import ModelManager
from backend.core.schemas import LoanApplication
from backend.services.imputation import DynamicLoanApplication
from backend.utils.ai_client import get_ai_client

router = APIRouter()
logger = logging.getLogger(__name__)


# Helper function for generating LLM explanations
async def generate_llm_explanation(
    input_data: Dict[str, Any],
    shap_explanation: Dict[str, float],
    risk_level: str,
) -> Dict[str, Any]:
    """Generate AI-powered explanation for credit risk decision."""
    try:
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
        
        system_prompt = "You are a friendly, expert financial analyst explaining complex risk to a non-expert."
        
        ai_client = get_ai_client()
        
        if not ai_client.is_available():
            return {
                "text": "AI explanation unavailable. Decision based on credit risk model analysis.",
                "remediation_suggestion": None,
                "error": "no_api_key"
            }
        
        result = await ai_client.generate_with_retry(prompt, system_prompt)
        
        if result.get("error"):
            return {
                "text": "AI explanation temporarily unavailable. Decision based on credit risk model analysis.",
                "remediation_suggestion": None,
                "error": result.get("error")
            }
        
        return {
            "text": result.get("text", ""),
            "remediation_suggestion": None,  # Can be enhanced later
            "raw": result.get("raw", "")
        }
        
    except Exception as e:
        logger.error(f"Error generating LLM explanation: {e}")
        return {
            "text": "AI explanation unavailable due to error. Decision based on credit risk model analysis.",
            "remediation_suggestion": None,
            "error": str(e)
        }

# Load feature statistics for drift detection
FEATURE_STATS = {}
try:
    from pathlib import Path
    from backend.core.config import PROJECT_ROOT
    
    stats_path = PROJECT_ROOT / "models" / "feature_statistics.json"
    if stats_path.exists():
        with open(stats_path, "r", encoding="utf-8") as sf:
            FEATURE_STATS = json.load(sf)
        logger.info(f"Loaded feature statistics from: {stats_path}")
except Exception as e:
    logger.warning(f"Could not load feature statistics: {e}")
    FEATURE_STATS = {}


@router.post("/predict_risk", response_model=Dict[str, Any])
async def predict_risk(application: LoanApplication):
    """
    Accepts complete loan application data and returns a credit risk prediction, probability,
    SHAP explanation, and AI-generated advice.

    Note: For CSV uploads and partial data, use /predict_risk_dynamic or /predict_risk_batch instead.
    """
    predictor = ModelManager.get_predictor()
    if predictor is None:
        raise HTTPException(
            status_code=503, detail={"status": "error", "message": "Model not loaded. Cannot process prediction."}
        )

    # Convert Pydantic model to a raw dictionary
    raw_input_dict = application.model_dump()

    # --- Data drift check ---
    drift_warnings = _check_drift(raw_input_dict)

    # --- Prepare Input Dictionary ---
    input_dict_for_predictor = {
        "person_age": raw_input_dict["person_age"],
        "person_income": raw_input_dict["person_income"],
        "person_emp_length": raw_input_dict["person_emp_length"],
        "loan_amnt": raw_input_dict["loan_amnt"],
        "loan_int_rate": raw_input_dict["loan_int_rate"],
        "loan_percent_income": raw_input_dict["loan_percent_income"],
        "cb_person_cred_hist_length": raw_input_dict["cb_person_cred_hist_length"],
        f"person_home_ownership_{raw_input_dict['home_ownership']}": 1,
        f"loan_intent_{raw_input_dict['loan_intent']}": 1,
        f"loan_grade_{raw_input_dict['loan_grade']}": 1,
        f"cb_person_default_on_file_{raw_input_dict['default_on_file']}": 1,
    }

    try:
        # Get prediction
        risk_level, prob, pred = predictor.predict(input_dict_for_predictor, flag_threshold=0.6)

        # Get SHAP values
        shap_values, expected_value, df_features = predictor.get_shap_values(input_dict_for_predictor)

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

        if len(feature_names) != len(row):
            logger.warning(
                "SHAP feature count (%s) != feature_names count (%s). Truncating to min length.", len(row), len(feature_names)
            )

        shap_explanation = {k: float(v) for k, v in zip(feature_names, row)}

    except Exception as e:
        logger.error(f"Prediction or SHAP calculation failed: {e}")
        raise HTTPException(status_code=500, detail={"status": "error", "message": f"Internal prediction error: {str(e)}"})

    # --- Generate LLM Explanation ---
    llm_result = await generate_llm_explanation(
        input_data=raw_input_dict,
        shap_explanation=shap_explanation,
        risk_level=risk_level,
    )
    llm_explanation = llm_result.get("text") if isinstance(llm_result, dict) else str(llm_result)
    remediation_suggestion = None
    if isinstance(llm_result, dict):
        remediation_suggestion = llm_result.get("remediation_suggestion")

    # Prepare operational notes
    operational_notes = ""
    if drift_warnings:
        operational_notes = "Data drift warnings detected: " + "; ".join(drift_warnings) + ". Please review input data."

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
        "operational_notes": operational_notes,
    }


@router.post("/predict_risk_dynamic", response_model=Dict[str, Any])
async def predict_risk_dynamic(application: DynamicLoanApplication):
    """
    Primary prediction endpoint for CSV uploads and flexible data input.
    """
    dynamic_predictor = ModelManager.get_dynamic_predictor()
    if dynamic_predictor is None:
        raise HTTPException(
            status_code=503, detail={"status": "error", "message": "Dynamic predictor not loaded. Cannot process prediction."}
        )

    raw_input_dict = application.model_dump(exclude_none=False)

    is_valid, validation_warnings = dynamic_predictor.validate_input(raw_input_dict)

    try:
        risk_level, prob, pred, imputation_log, imputed_data = dynamic_predictor.predict(
            raw_input_dict, flag_threshold=0.6, return_imputation_log=True
        )

        shap_values, expected_value, df_features, _ = dynamic_predictor.get_shap_values(raw_input_dict)

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
        raise HTTPException(status_code=500, detail={"status": "error", "message": f"Prediction error: {str(e)}"})

    # Data drift check on imputed data
    drift_warnings = _check_drift(imputed_data)

    llm_result = await generate_llm_explanation(
        input_data=imputed_data,
        shap_explanation=shap_explanation,
        risk_level=risk_level,
    )

    llm_explanation = llm_result.get("text") if isinstance(llm_result, dict) else str(llm_result)
    remediation_suggestion = llm_result.get("remediation_suggestion") if isinstance(llm_result, dict) else None

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
        "operational_notes": operational_notes,
    }


@router.post("/predict_risk_batch", response_model=Dict[str, Any])
async def predict_risk_batch(applications: List[DynamicLoanApplication], include_explanations: bool = False):
    """
    Batch prediction endpoint for CSV uploads.
    """
    dynamic_predictor = ModelManager.get_dynamic_predictor()
    if dynamic_predictor is None:
        raise HTTPException(status_code=503, detail={"status": "error", "message": "Dynamic predictor not loaded."})

    results = []

    for idx, application in enumerate(applications):
        try:
            raw_input_dict = application.model_dump(exclude_none=False)

            risk_level, prob, pred, imputation_log, imputed_data = dynamic_predictor.predict(
                raw_input_dict, flag_threshold=0.6, return_imputation_log=True
            )

            result = {
                "index": idx,
                "status": "success",
                "risk_level": risk_level,
                "probability_default_percent": round(prob * 100, 2),
                "binary_prediction": pred,
                "input_features": imputed_data,
                "imputation_log": imputation_log,
            }

            if include_explanations:
                try:
                    shap_values, _, df_features, _ = dynamic_predictor.get_shap_values(raw_input_dict)
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

                    llm_result = await generate_llm_explanation(
                        input_data=imputed_data,
                        shap_explanation=shap_explanation,
                        risk_level=risk_level,
                    )

                    result["shap_explanation"] = shap_explanation
                    result["llm_explanation"] = llm_result.get("text") if isinstance(llm_result, dict) else str(llm_result)
                    result["remediation_suggestion"] = (
                        llm_result.get("remediation_suggestion") if isinstance(llm_result, dict) else None
                    )

                except Exception as e:
                    logger.warning(f"Explanation generation failed for item {idx}: {e}")
                    result["explanation_error"] = str(e)

            results.append(result)

        except Exception as e:
            logger.error(f"Batch item {idx} failed: {e}")
            results.append({"index": idx, "status": "error", "error": str(e)})

    return {"results": results, "count": len(results)}


def _check_drift(data: Dict[str, Any]) -> List[str]:
    warnings = []
    try:
        for feat, stats in FEATURE_STATS.items():
            if feat in data:
                try:
                    val = float(data[feat])
                except Exception:
                    continue
                mn = stats.get("min")
                mx = stats.get("max")
                mean = stats.get("mean")
                std = stats.get("std")

                if mn is not None and mx is not None and (val < mn or val > mx):
                    warnings.append(f"{feat}: value {val} outside training min/max [{mn}, {mx}]")
                elif mean is not None and std is not None and std >= 0:
                    lower = mean - 3 * std
                    upper = mean + 3 * std
                    if val < lower or val > upper:
                        warnings.append(f"{feat}: value {val} outside 3-sigma range [{lower:.2f}, {upper:.2f}]")
    except Exception as e:
        logger.debug(f"Error during drift check: {e}")
    return warnings

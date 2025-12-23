import json
import logging
import os
import time
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.routes.model import ModelManager
from backend.core.schemas import LoanApplication
from backend.database import crud
from backend.database.config import get_db
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
            logger.warning("AI client not available - no API key configured")
            return {
                "text": "AI explanation unavailable. Decision based on credit risk model analysis.",
                "remediation_suggestion": None,
                "error": "no_api_key"
            }
        
        logger.info("Generating LLM explanation...")
        
        result = await ai_client.generate_with_retry(prompt, system_prompt)
        
        if result.get("error"):
            error_type = result.get("error")
            logger.warning(f"LLM generation failed with error: {error_type}")
            return {
                "text": "AI explanation temporarily unavailable. Decision based on credit risk model analysis.",
                "remediation_suggestion": None,
                "error": error_type
            }
        
        # Ensure we always return text, even if empty
        text = result.get("text", "").strip()
        if not text:
            # If text is empty, use fallback
            logger.warning("LLM returned empty text, using fallback explanation")
            return {
                "text": "AI explanation temporarily unavailable. Decision based on credit risk model analysis. Please refer to the SHAP values for detailed feature contributions.",
                "remediation_suggestion": None,
                "error": "empty_response",
                "raw": result.get("raw", "")
            }
        
        logger.info(f"LLM explanation generated successfully ({len(text)} characters)")
        return {
            "text": text,
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


def _get_model_version() -> str:
    """Get the current model version from manifest."""
    try:
        from pathlib import Path
        from backend.core.config import PROJECT_ROOT
        
        manifest_path = PROJECT_ROOT / "models" / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                if isinstance(manifest, list) and len(manifest) > 0:
                    # Get the latest version
                    latest = manifest[-1]
                    return latest.get("version") or latest.get("model_version") or "unknown"
                elif isinstance(manifest, dict):
                    return manifest.get("version") or manifest.get("model_version") or "unknown"
    except Exception as e:
        logger.warning(f"Could not get model version: {e}")
    return "unknown"


def _store_prediction_to_db(
    db: Session,
    input_features: Dict[str, Any],
    risk_level: str,
    probability_default: float,
    binary_prediction: int,
    model_type: str = "dynamic",
    shap_explanation: Dict[str, float] = None,
    llm_explanation: str = None,
    remediation_suggestion: str = None,
    prediction_time_ms: float = None,
) -> None:
    """
    Store prediction to database for future retraining.
    
    Args:
        db: Database session
        input_features: Input features (target columns already excluded)
        risk_level: Predicted risk level
        probability_default: Probability of default
        binary_prediction: Binary prediction (0 or 1)
        model_type: Type of model used
        shap_explanation: SHAP values (optional)
        llm_explanation: LLM explanation (optional)
        remediation_suggestion: Remediation suggestion (optional)
        prediction_time_ms: Prediction time in milliseconds (optional)
    """
    try:
        # Exclude target columns from input_features (they should not be used as features)
        target_columns = {"loan_status", "loan_status_num", "default", "target", "label", "outcome"}
        clean_features = {k: v for k, v in input_features.items() if k not in target_columns}
        
        model_version = _get_model_version()
        
        prediction_data = {
            "input_features": clean_features,
            "risk_level": risk_level,
            "probability_default": probability_default,
            "binary_prediction": binary_prediction,
            "model_type": model_type,
            "model_version": model_version,
            "shap_values": shap_explanation,
            "explanation": llm_explanation,
            "remediation_suggestion": remediation_suggestion,
            "prediction_time_ms": prediction_time_ms,
        }
        
        crud.create_prediction(db, prediction_data)
        logger.debug(f"Prediction stored to database: risk_level={risk_level}, probability={probability_default}")
    except Exception as e:
        # Don't fail the prediction if database storage fails
        logger.warning(f"Failed to store prediction to database: {e}")


@router.post("/predict_risk", response_model=Dict[str, Any])
async def predict_risk(application: LoanApplication, db: Session = Depends(get_db)):
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

    # Store prediction to database for future retraining
    try:
        _store_prediction_to_db(
            db=db,
            input_features=raw_input_dict,
            risk_level=risk_level,
            probability_default=prob,
            binary_prediction=pred,
            model_type="traditional",
            shap_explanation=shap_explanation,
            llm_explanation=llm_explanation,
            remediation_suggestion=remediation_suggestion,
        )
    except Exception as e:
        logger.warning(f"Failed to store prediction to database: {e}")

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
async def predict_risk_dynamic(
    application: DynamicLoanApplication, 
    include_llm: bool = True,
    db: Session = Depends(get_db)
):
    """
    Primary prediction endpoint for CSV uploads and flexible data input.
    
    Args:
        application: Loan application data
        include_llm: Whether to generate LLM explanation (default: True). Set to False for batch processing to save tokens.
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

    # Generate LLM explanation only if requested (skip for batch processing to save tokens)
    llm_explanation = None
    remediation_suggestion = None
    if include_llm:
        llm_result = await generate_llm_explanation(
            input_data=imputed_data,
            shap_explanation=shap_explanation,
            risk_level=risk_level,
        )
        llm_explanation = llm_result.get("text") if isinstance(llm_result, dict) else str(llm_result)
        remediation_suggestion = llm_result.get("remediation_suggestion") if isinstance(llm_result, dict) else None
    else:
        logger.info("Skipping LLM explanation generation (batch processing mode)")

    operational_notes_parts = []
    if imputation_log:
        operational_notes_parts.append(f"Imputed {len(imputation_log)} fields: {', '.join(imputation_log[:5])}")
    if validation_warnings:
        operational_notes_parts.append(f"Validation warnings: {'; '.join(validation_warnings)}")
    if drift_warnings:
        operational_notes_parts.append(f"Data drift detected: {'; '.join(drift_warnings[:3])}")

    operational_notes = " | ".join(operational_notes_parts) if operational_notes_parts else ""

    # Store prediction to database for future retraining
    # Use imputed_data (not raw_input_dict) as it has the actual features used for prediction
    try:
        _store_prediction_to_db(
            db=db,
            input_features=imputed_data,
            risk_level=risk_level,
            probability_default=prob,
            binary_prediction=pred,
            model_type="dynamic",
            shap_explanation=shap_explanation,
            llm_explanation=llm_explanation,
            remediation_suggestion=remediation_suggestion,
        )
    except Exception as e:
        logger.warning(f"Failed to store prediction to database: {e}")

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

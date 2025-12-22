import json
import logging

from fastapi import APIRouter, HTTPException

from backend.models.dynamic_predictor import DynamicCreditRiskPredictor
from backend.models.predictor import CreditRiskPredictor

router = APIRouter()
logger = logging.getLogger(__name__)

"""
Model management and health check endpoints.

This module provides a singleton ModelManager class to manage model instances
and API endpoints for model health checks and reloading.
"""


class ModelManager:
    """
    Singleton manager for credit risk prediction models.
    
    Manages the lifecycle of CreditRiskPredictor and DynamicCreditRiskPredictor
    instances, providing a centralized way to load, access, and reload models.
    """
    _predictor = None
    _dynamic_predictor = None

    @classmethod
    def get_predictor(cls):
        return cls._predictor

    @classmethod
    def get_dynamic_predictor(cls):
        return cls._dynamic_predictor

    @classmethod
    def load_models(cls):
        try:
            cls._predictor = CreditRiskPredictor()
            logger.info("CreditRiskPredictor loaded successfully.")
        except Exception as e:
            logger.error(f"FATAL: Model loading failed. Prediction API will be disabled. Error: {e}")
            cls._predictor = None

        try:
            cls._dynamic_predictor = DynamicCreditRiskPredictor()
            logger.info("DynamicCreditRiskPredictor loaded successfully.")
        except Exception as e:
            logger.warning(f"Dynamic predictor initialization failed: {e}")
            cls._dynamic_predictor = None

    @classmethod
    def reload_models(cls):
        logger.info("Reloading models...")
        cls.load_models()
        return True




@router.get("/health")
def health_check():
    """Check if the API is running and the model is loaded."""
    predictor = ModelManager.get_predictor()
    if predictor is None:
        error_msg = "Model not loaded. Service unavailable."
        return {
            "status": "error",
            "message": error_msg,
            "load_error": "Model failed to load during startup. Check logs for details.",
        }
    return {"status": "ok", "message": "API is running and model is ready."}


@router.get("/model/health")
def model_health():
    """
    Alias endpoint for model health used by the admin panel.

    This keeps backwards compatibility with /health while exposing
    a namespaced /model/health endpoint under /api/v1.
    """
    return health_check()


@router.get("/state")
def get_model_state():
    """Get detailed model state information."""
    import os
    from backend.core.config import MODELS_DIR
    
    predictor = ModelManager.get_predictor()
    dynamic_predictor = ModelManager.get_dynamic_predictor()
    
    state = {
        "predictor_loaded": predictor is not None,
        "dynamic_predictor_loaded": dynamic_predictor is not None,
        "model_files": {},
        "manifest": None
    }
    
    # Check model files in the configured models directory
    model_path = MODELS_DIR / "credit_risk_model.pkl"
    scaler_path = MODELS_DIR / "scaler.pkl"
    features_path = MODELS_DIR / "feature_names.json"
    manifest_path = MODELS_DIR / "manifest.json"
    
    if model_path.exists():
        state["model_files"]["model"] = {
            "exists": True,
            "size": os.path.getsize(model_path),
            "modified": os.path.getmtime(model_path)
        }
    else:
        state["model_files"]["model"] = {"exists": False}
    
    if scaler_path.exists():
        state["model_files"]["scaler"] = {
            "exists": True,
            "size": os.path.getsize(scaler_path),
            "modified": os.path.getmtime(scaler_path)
        }
    else:
        state["model_files"]["scaler"] = {"exists": False}
    
    if features_path.exists():
        state["model_files"]["features"] = {
            "exists": True,
            "size": os.path.getsize(features_path),
            "modified": os.path.getmtime(features_path)
        }
    else:
        state["model_files"]["features"] = {"exists": False}
    
    # Load manifest if exists
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                if isinstance(manifest, list) and len(manifest) > 0:
                    state["manifest"] = manifest[-1]  # Latest entry
        except Exception as e:
            logger.warning(f"Failed to load manifest: {e}")
    
    # Add predictor info if loaded
    if predictor:
        state["predictor_info"] = {
            "has_model": predictor.model is not None,
            "has_scaler": predictor.scaler is not None,
            "has_features": predictor.feature_names is not None,
            "feature_count": len(predictor.feature_names) if predictor.feature_names else 0,
            "load_error": predictor.load_error
        }
    
    return state


@router.get("/model/state")
def get_model_state_alias():
    """
    Alias endpoint for model state used by the admin panel.

    Exposes /api/v1/model/state while reusing the core implementation.
    """
    return get_model_state()


@router.post("/reload_model")
def reload_model():
    """Reload the model from disk. Useful after retraining or fixing model files."""
    try:
        ModelManager.reload_models()
        return {"status": "success", "message": "Model reloaded successfully."}
    except Exception as e:
        logger.error(f"Model reload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"status": "error", "message": f"Model reload failed: {str(e)}"})


@router.post("/model/reload")
def reload_model_alias():
    """
    Alias endpoint for model reload used by the admin panel.

    Exposes /api/v1/model/reload while reusing the core implementation.
    """
    return reload_model()

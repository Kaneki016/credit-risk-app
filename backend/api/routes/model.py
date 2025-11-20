from fastapi import APIRouter, HTTPException
import logging
from backend.models.predictor import CreditRiskPredictor
from backend.models.dynamic_predictor import DynamicCreditRiskPredictor

router = APIRouter()
logger = logging.getLogger(__name__)

# Global instances (will be managed by main app state or dependency injection in a cleaner architecture,
# but for now we keep the pattern to minimize disruption, but we need to access them)
# In this refactor, we'll rely on the fact that these are loaded in main.py and we might need a way to access them.
# However, to avoid circular imports, we might need to initialize them here or have a singleton service.
# For this step, let's assume we can re-instantiate or better yet, use a dependency.
# BUT, `reload_model` updates the global state.
# To properly share state without circular imports, we should probably have a `backend.core.state` module.
# For now, let's define a simple state container in a new file or just keep them here if they are only used here?
# No, they are used in prediction routes too.


# Let's create a simple state manager to hold the predictors.
class ModelManager:
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


# Initialize on import (or we can call it explicitly in main)
# ModelManager.load_models()


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


@router.post("/reload_model")
def reload_model():
    """Reload the model from disk. Useful after retraining or fixing model files."""
    try:
        ModelManager.reload_models()
        return {"status": "success", "message": "Model reloaded successfully."}
    except Exception as e:
        logger.error(f"Model reload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"status": "error", "message": f"Model reload failed: {str(e)}"})

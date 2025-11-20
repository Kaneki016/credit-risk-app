import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile

from backend.services.database_retraining import check_retraining_status, retrain_from_database
from backend.services.flexible_training import FlexibleModelTrainer

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/db/retraining/status")
def get_retraining_status():
    """
    Check if the model is ready for retraining from the database.
    """
    try:
        return check_retraining_status()
    except Exception as e:
        logger.error(f"Error checking retraining status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/db/retraining/start")
@router.post("/db/retrain")  # Alias for frontend compatibility
def start_retraining(
    background_tasks: BackgroundTasks, min_samples: int = 100, min_feedback_ratio: float = 0.1, test_size: float = 0.2
):
    """
    Start the model retraining process in the background.
    """
    try:
        # Check status first
        status = check_retraining_status()
        if not status["is_ready"]:
            raise HTTPException(status_code=400, detail=f"Not enough data. Need {status['samples_needed']} more samples.")

        # Run in background
        background_tasks.add_task(
            retrain_from_database, min_samples=min_samples, min_feedback_ratio=min_feedback_ratio, test_size=test_size
        )

        return {"message": "Retraining started in background", "status": status}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting retraining: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train/flexible")
async def train_flexible_model(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Train a model from a CSV file with flexible column detection.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Save file temporarily
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / f"train_{file.filename}"

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Initialize trainer
        trainer = FlexibleModelTrainer()

        # Run training in background (or synchronously if fast enough, but better background)
        # For now, we'll run it synchronously to return immediate results as the frontend expects
        # If it's large, we should use background tasks, but the frontend seems to wait for result.

        result = trainer.train_model(str(temp_path))

        # Cleanup
        os.remove(temp_path)

        return {"status": "success", "result": result}

    except Exception as e:
        logger.error(f"Flexible training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

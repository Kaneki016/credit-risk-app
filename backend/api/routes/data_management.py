from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import pandas as pd
import io
import logging
from typing import Dict, Any, List
import json

from backend.database import get_db, crud, models

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/db/import_csv")
async def import_csv_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import historical data from CSV.
    Creates LoanApplication and Prediction records (with actual outcomes) for retraining.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        logger.info(f"Importing {len(df)} rows from {file.filename}")

        # Standardize column names
        df.columns = [c.lower().replace(" ", "_").replace("-", "_") for c in df.columns]

        imported_count = 0

        # Column mapping (CSV -> Model)
        # We try to match common names

        for _, row in df.iterrows():
            try:
                # 1. Create Loan Application
                app_data = {
                    "person_age": row.get("person_age") or row.get("age"),
                    "person_income": row.get("person_income") or row.get("income") or row.get("annual_income"),
                    "person_emp_length": row.get("person_emp_length") or row.get("emp_length"),
                    "home_ownership": row.get("person_home_ownership") or row.get("home_ownership") or row.get("home"),
                    "loan_amnt": row.get("loan_amnt") or row.get("loan_amount") or row.get("amount"),
                    "loan_int_rate": row.get("loan_int_rate") or row.get("interest_rate") or row.get("rate"),
                    "loan_percent_income": row.get("loan_percent_income") or row.get("percent_income"),
                    "loan_intent": row.get("loan_intent") or row.get("intent") or row.get("purpose"),
                    "loan_grade": row.get("loan_grade") or row.get("grade"),
                    "cb_person_cred_hist_length": row.get("cb_person_cred_hist_length") or row.get("cred_hist_length"),
                    "default_on_file": row.get("cb_person_default_on_file")
                    or row.get("default_on_file")
                    or row.get("default_history"),
                    "application_status": "approved",  # Assume historical data is processed
                }

                # Clean data (handle NaNs)
                app_data = {k: (v if pd.notna(v) else None) for k, v in app_data.items()}

                # Skip if essential fields are missing
                if not app_data["person_income"] or not app_data["loan_amnt"]:
                    continue

                application = crud.create_loan_application(db, app_data)

                # 2. Create Prediction record (for retraining)
                # We treat historical data as "predictions" with known outcomes
                loan_status = row.get("loan_status")
                if loan_status is None:
                    loan_status = row.get("loan_status_num")  # Try numeric

                if loan_status is not None:
                    actual_outcome = int(loan_status)

                    # Create dummy prediction record linked to application
                    pred_data = {
                        "application_id": application.id,
                        "input_features": app_data,  # Store features for retraining
                        "risk_level": "Historical",
                        "probability_default": 0.0,  # Unknown
                        "binary_prediction": actual_outcome,  # Assume perfect prediction for history? Or just store actual.
                        "model_type": "historical_import",
                        "actual_outcome": actual_outcome,
                        "feedback_date": pd.Timestamp.now(),
                    }
                    crud.create_prediction(db, pred_data)

                imported_count += 1

            except Exception as e:
                logger.warning(f"Failed to import row: {e}")
                continue

        return {
            "status": "success",
            "message": f"Successfully imported {imported_count} records",
            "total_rows": len(df),
            "imported": imported_count,
        }

    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import io
import json
import logging
from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session

from backend.database import crud, models
from backend.database.config import get_db, engine

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/db/schema/{table_name}")
def get_table_schema(table_name: str, db: Session = Depends(get_db)):
    """
    Get column names for a specific table.
    """
    from sqlalchemy import inspect
    
    try:
        inspector = inspect(engine)
        if not inspector.has_table(table_name):
            raise HTTPException(status_code=404, detail=f"Table {table_name} not found")
            
        columns = [c["name"] for c in inspector.get_columns(table_name)]
        return {"table": table_name, "columns": columns}
    except Exception as e:
        logger.error(f"Failed to get schema for {table_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/db/import_csv")
async def import_csv_data(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    replace_schema: bool = False,
    column_mapping: str = Form(None), # JSON string
    db: Session = Depends(get_db)
):
    """
    Import historical data from CSV.
    Creates LoanApplication and Prediction records (with actual outcomes) for retraining.
    Dynamically updates schema for new columns.
    
    Args:
        replace_schema: If True, drops existing table and recreates it based on CSV columns.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        logger.info(f"Starting CSV import for {file.filename}")
        
        # Determine mapping
        mapping = {}
        if column_mapping:
            try:
                mapping = json.loads(column_mapping)
                logger.info(f"Using provided column mapping: {mapping}")
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in column_mapping, falling back to default")
        
        if not mapping:
            # Known mappings (CSV -> Model)
            mapping = {
                "age": "person_age",
                "income": "person_income",
                "annual_income": "person_income",
                "emp_length": "person_emp_length",
                "person_home_ownership": "home_ownership",
                "home": "home_ownership",
                "loan_amount": "loan_amnt",
                "amount": "loan_amnt",
                "interest_rate": "loan_int_rate",
                "rate": "loan_int_rate",
                "percent_income": "loan_percent_income",
                "intent": "loan_intent",
                "purpose": "loan_intent",
                "grade": "loan_grade",
                "cred_hist_length": "cb_person_cred_hist_length",
                "default_history": "default_on_file",
                "cb_person_default_on_file": "default_on_file",
            }

        imported_count = 0
        chunk_size = 1000
        
        # Process in chunks
        # file.file is a SpooledTemporaryFile which works with pd.read_csv
        csv_iterator = pd.read_csv(file.file, chunksize=chunk_size)
        
        from sqlalchemy import MetaData, Table, Float, String, inspect
        
        first_chunk = True
        
        for i, df in enumerate(csv_iterator):
            # Standardize column names
            df.columns = [c.lower().replace(" ", "_").replace("-", "_").replace(".", "_") for c in df.columns]
            
            # Rename columns
            df = df.rename(columns=mapping)
            
            # Handle Schema (only on first chunk)
            if first_chunk:
                inspector = inspect(engine)
                if not inspector.has_table("loan_applications"):
                    logger.info("Table loan_applications does not exist. Creating...")
                    
                    csv_columns = {}
                    for col in df.columns:
                        dtype = df[col].dtype
                        if pd.api.types.is_numeric_dtype(dtype):
                            csv_columns[col] = Float
                        else:
                            csv_columns[col] = String(255)
                    
                    crud.create_loan_application_table(db, csv_columns)
                    db.commit()
                else:
                    # Append mode: Ensure columns exist
                    # We check all columns in the first chunk against DB
                    existing_columns = {c["name"] for c in inspector.get_columns("loan_applications")}
                    
                    for col in df.columns:
                        if col not in existing_columns:
                            # Infer type
                            dtype = df[col].dtype
                            col_type = "FLOAT" if pd.api.types.is_numeric_dtype(dtype) else "VARCHAR(255)"
                            crud.add_column_if_not_exists(db, "loan_applications", col, col_type)
                
                first_chunk = False

            # Prepare data for bulk insert
            app_data_list = []
            
            # Pre-process dataframe to dicts
            # Replace NaNs with None
            # We convert to object first to ensure None is accepted in numeric columns
            df_dict = df.astype(object).where(pd.notnull(df), None).to_dict(orient='records')
            
            for row in df_dict:
                # Ensure essential fields exist (if they are missing, we might skip or allow partial)
                if not row:
                    continue
                
                # Set default status
                row["application_status"] = "approved"
                app_data_list.append(row)
            
            if not app_data_list:
                continue

            # Bulk Insert LoanApplications
            # We use Core Insert to handle dynamic columns and RETURNING to get IDs
            metadata = MetaData()
            table = Table('loan_applications', metadata, autoload_with=db.get_bind())
            
            try:
                # Try using RETURNING clause (Postgres, SQLite 3.35+)
                stmt = table.insert().values(app_data_list).returning(table.c.id)
                result = db.execute(stmt)
                new_ids = result.scalars().all()
                
                # If we got IDs, create Predictions
                if new_ids and len(new_ids) == len(app_data_list):
                    pred_data_list = []
                    
                    for idx, app_data in enumerate(app_data_list):
                        app_id = new_ids[idx]
                        
                        # Determine actual outcome
                        loan_status = app_data.get("loan_status")
                        if loan_status is None:
                            loan_status = app_data.get("loan_status_num")
                        if loan_status is None:
                            loan_status = app_data.get("default") or app_data.get("target")
                            
                        actual_outcome = 0
                        if loan_status is not None:
                            try:
                                actual_outcome = int(loan_status)
                            except:
                                actual_outcome = 1 if str(loan_status).lower() in ['y', 'yes', '1', 'true'] else 0
                        
                        # Exclude target columns from input_features (they should not be used as features)
                        # Target columns: loan_status, loan_status_num, default, target, label, outcome
                        target_columns = {"loan_status", "loan_status_num", "default", "target", "label", "outcome"}
                        input_features = {k: v for k, v in app_data.items() if k not in target_columns}
                        
                        pred_data = {
                            "application_id": app_id,
                            "input_features": input_features,
                            "risk_level": "Historical",
                            "probability_default": 0.0,
                            "binary_prediction": actual_outcome,
                            "model_type": "historical_import",
                            "actual_outcome": actual_outcome,
                            "feedback_date": pd.Timestamp.now(),
                        }
                        pred_data_list.append(pred_data)
                    
                    if pred_data_list:
                        db.execute(models.Prediction.__table__.insert(), pred_data_list)
                
                db.commit()
                imported_count += len(app_data_list)
                logger.info(f"Imported chunk of {len(app_data_list)} rows. Total: {imported_count}")

            except Exception as e:
                db.rollback()
                logger.error(f"Failed to import chunk: {e}")
                # If RETURNING fails, we might fall back to row-by-row for this chunk?
                # Or just fail. For now, let's log and continue (skipping chunk) or raise.
                # Raising is safer to alert user.
                raise HTTPException(status_code=500, detail=f"Bulk import failed: {str(e)}")

        # Note: Auto-retraining removed. Users should manually trigger retraining
        # after importing data to have better control over when retraining happens.

        return {
            "status": "success",
            "message": f"Successfully imported {imported_count} records",
            "total_rows": imported_count, # Approximation since we don't know total upfront without reading all
            "imported": imported_count,
        }

    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

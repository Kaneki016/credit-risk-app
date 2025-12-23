"""
Database Clear Endpoint
Provides functionality to clear all data from the database.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db, models

logger = logging.getLogger(__name__)

router = APIRouter()


@router.delete("/db/clear")
def clear_database(confirm: bool = False, drop_tables: bool = False, db: Session = Depends(get_db)):
    """
    Clear all data from the database.

    WARNING: This will delete ALL data including:
    - Predictions
    - Loan Applications
    - Model Metrics

    Args:
        confirm: Must be True to proceed with deletion
        drop_tables: If True, will drop and recreate all tables (schema reset)

    Returns:
        Summary of deleted records
    """
    if not confirm:
        raise HTTPException(status_code=400, detail="Must set confirm=true to clear database")

    try:
        if drop_tables:
            logger.warning("⚠️  DROPPING ALL TABLES - This is a destructive operation!")
            
            # Use CRUD function to drop tables
            from backend.database import crud
            crud.drop_loan_application_table(db)
            
            logger.info("✅ All tables dropped.")
            return {
                "status": "success",
                "message": "All tables dropped successfully",
                "action": "schema_reset"
            }

        logger.warning("⚠️  DATABASE CLEAR REQUESTED - Deleting all data...")

        from sqlalchemy import func

        # Count records before deletion
        # Use func.count(id) to avoid selecting columns that might not exist in the dynamic schema
        counts_before = {
            "predictions": db.query(func.count(models.Prediction.id)).scalar(),
            "loan_applications": db.query(func.count(models.LoanApplication.id)).scalar(),
            "model_metrics": db.query(func.count(models.ModelMetrics.id)).scalar(),
        }

        # Delete all records (order matters due to foreign keys)
        db.query(models.Prediction).delete()
        db.query(models.LoanApplication).delete()
        db.query(models.ModelMetrics).delete()

        db.commit()

        logger.info(f"✅ Database cleared successfully. Deleted: {counts_before}")

        return {
            "status": "success",
            "message": "Database cleared successfully",
            "deleted": counts_before,
            "total_deleted": sum(counts_before.values()),
        }

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to clear database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear database: {str(e)}")

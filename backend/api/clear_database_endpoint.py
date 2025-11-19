"""
Database Clear Endpoint
Provides functionality to clear all data from the database.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db, models
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.delete("/db/clear")
def clear_database(
    confirm: bool = False,
    db: Session = Depends(get_db)
):
    """
    Clear all data from the database.
    
    WARNING: This will delete ALL data including:
    - Predictions
    - Loan Applications
    - Feature Engineering records
    - Mitigation Plans
    - Audit Logs
    - Model Metrics
    
    Args:
        confirm: Must be True to proceed with deletion
        
    Returns:
        Summary of deleted records
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must set confirm=true to clear database"
        )
    
    try:
        logger.warning("⚠️  DATABASE CLEAR REQUESTED - Deleting all data...")
        
        # Count records before deletion
        counts_before = {
            "predictions": db.query(models.Prediction).count(),
            "loan_applications": db.query(models.LoanApplication).count(),
            "feature_engineering": db.query(models.FeatureEngineering).count(),
            "mitigation_plans": db.query(models.MitigationPlan).count(),
            "audit_logs": db.query(models.AuditLog).count(),
            "model_metrics": db.query(models.ModelMetrics).count()
        }
        
        # Delete all records (order matters due to foreign keys)
        db.query(models.MitigationPlan).delete()
        db.query(models.FeatureEngineering).delete()
        db.query(models.Prediction).delete()
        db.query(models.LoanApplication).delete()
        db.query(models.AuditLog).delete()
        db.query(models.ModelMetrics).delete()
        
        db.commit()
        
        logger.info(f"✅ Database cleared successfully. Deleted: {counts_before}")
        
        return {
            "status": "success",
            "message": "Database cleared successfully",
            "deleted": counts_before,
            "total_deleted": sum(counts_before.values())
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to clear database: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear database: {str(e)}"
        )

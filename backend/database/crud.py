# backend/database/crud.py
"""
CRUD operations for database models.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
import re

from backend.database import models

logger = logging.getLogger(__name__)


# ==================== Loan Applications ====================


def add_column_if_not_exists(db: Session, table_name: str, column_name: str, column_type: str = "FLOAT"):
    """Add a column to a table if it doesn't exist."""
    # Sanitize column name to prevent SQL injection
    if not re.match(r"^[a-zA-Z0-9_]+$", column_name):
        raise ValueError(f"Invalid column name: {column_name}")

    inspector = inspect(db.get_bind())
    columns = [c["name"] for c in inspector.get_columns(table_name)]

    if column_name not in columns:
        try:
            # Use text() for raw SQL
            # Quote column name to handle reserved keywords
            db.execute(text(f'ALTER TABLE {table_name} ADD COLUMN "{column_name}" {column_type}'))
            db.commit()
            logger.info(f"Added column {column_name} to {table_name}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to add column {column_name}: {e}")
            raise


def drop_loan_application_table(db: Session):
    """
    Drop the loan_applications table and its dependencies.
    """
    from backend.database.config import engine
    
    logger.warning("⚠️  Dropping loan_applications and dependent tables...")
    
    # 1. Drop dependent tables first to avoid FK violations
    try:
        models.Prediction.__table__.drop(bind=engine, checkfirst=True)
        logger.info("Dropped dependent tables (predictions)")
    except Exception as e:
        logger.warning(f"Error dropping dependent tables: {e}")

    # 2. Drop loan_applications
    try:
        models.LoanApplication.__table__.drop(bind=engine, checkfirst=True)
        logger.info("Dropped loan_applications table")
    except Exception as e:
        logger.error(f"Error dropping loan_applications table: {e}")
        raise


def create_loan_application_table(db: Session, csv_columns: Dict[str, Any]):
    """
    Create the loan_applications table with columns from CSV.
    """
    from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, Text, func
    from backend.database.config import engine
    
    logger.info("Creating new loan_applications table with dynamic schema...")
    
    # Define new table structure
    metadata = MetaData()
    
    # Start with standard/metadata columns
    columns = [
        Column("id", Integer, primary_key=True, index=True),
        Column("created_at", DateTime(timezone=True), server_default=func.now()),
        Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
        Column("application_status", String(50), default="pending"),
        Column("notes", Text, nullable=True),
    ]
    
    # Track added column names
    added_col_names = {"id", "created_at", "updated_at", "application_status", "notes"}
    
    # Add CSV columns
    for col_name, col_type in csv_columns.items():
        if col_name not in added_col_names:
            # Use provided type if it's a SQLAlchemy type class, otherwise default
            sql_type = col_type if hasattr(col_type, "__visit_name__") else String(255)
            
            columns.append(Column(col_name, sql_type, nullable=True))
            added_col_names.add(col_name)

    # Create the table
    new_table = Table("loan_applications", metadata, *columns)
    new_table.create(bind=engine)
    logger.info(f"Created new loan_applications table with {len(columns)} columns")
    
    # Recreate dependent tables (Predictions)
    # We use the original model definitions
    models.Prediction.__table__.create(bind=engine)
    logger.info("Recreated dependent tables")


def create_loan_application(db: Session, application_data: Dict[str, Any]) -> models.LoanApplication:
    """Create a new loan application, handling dynamic columns."""
    # 1. Identify columns defined in the ORM model
    model_columns = {c.name for c in models.LoanApplication.__table__.columns}
    
    # 2. Identify keys in input data that are NOT in the ORM model
    # These are dynamic columns (either new or existing in DB but not in model)
    dynamic_keys = [k for k in application_data.keys() if k not in model_columns]
    
    # 3. Ensure dynamic columns exist in the database
    if dynamic_keys:
        inspector = inspect(db.get_bind())
        existing_db_columns = {c["name"] for c in inspector.get_columns("loan_applications")}
        
        for col in dynamic_keys:
            if col not in existing_db_columns:
                # Infer type
                val = application_data[col]
                col_type = "FLOAT"
                if isinstance(val, str):
                    col_type = "VARCHAR(255)"
                
                add_column_if_not_exists(db, "loan_applications", col, col_type)

    # 4. Insert data
    # If we have dynamic keys, we MUST use Core Insert because the ORM model class doesn't accept them
    if dynamic_keys:
        from sqlalchemy import MetaData, Table
        metadata = MetaData()
        table = Table('loan_applications', metadata, autoload_with=db.get_bind())
        
        stmt = table.insert().values(**application_data)
        result = db.execute(stmt)
        db.commit()
        
        # Return the created object (re-queried)
        # Note: This object will ONLY have the static model attributes populated.
        return db.query(models.LoanApplication).filter(models.LoanApplication.id == result.inserted_primary_key[0]).first()
    else:
        # Standard ORM insert
        db_application = models.LoanApplication(**application_data)
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        return db_application


def get_loan_application(db: Session, application_id: int) -> Optional[models.LoanApplication]:
    """Get a loan application by ID."""
    return db.query(models.LoanApplication).filter(models.LoanApplication.id == application_id).first()


def get_loan_applications(
    db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None
) -> List[models.LoanApplication]:
    """Get list of loan applications."""
    query = db.query(models.LoanApplication)
    if status:
        query = query.filter(models.LoanApplication.application_status == status)
    return query.offset(skip).limit(limit).all()


def update_loan_application(db: Session, application_id: int, update_data: Dict[str, Any]) -> Optional[models.LoanApplication]:
    """Update a loan application."""
    db_application = get_loan_application(db, application_id)
    if db_application:
        for key, value in update_data.items():
            setattr(db_application, key, value)
        db.commit()
        db.refresh(db_application)
    return db_application


# ==================== Predictions ====================


def create_prediction(db: Session, prediction_data: Dict[str, Any]) -> models.Prediction:
    """Create a new prediction record."""
    db_prediction = models.Prediction(**prediction_data)
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction


def get_prediction(db: Session, prediction_id: int) -> Optional[models.Prediction]:
    """Get a prediction by ID."""
    return db.query(models.Prediction).filter(models.Prediction.id == prediction_id).first()


def get_predictions(
    db: Session, skip: int = 0, limit: int = 100, model_type: Optional[str] = None, application_id: Optional[int] = None
) -> List[models.Prediction]:
    """Get list of predictions."""
    query = db.query(models.Prediction)
    if model_type:
        query = query.filter(models.Prediction.model_type == model_type)
    if application_id:
        query = query.filter(models.Prediction.application_id == application_id)
    return query.order_by(models.Prediction.created_at.desc()).offset(skip).limit(limit).all()


def update_prediction_feedback(db: Session, prediction_id: int, actual_outcome: int) -> Optional[models.Prediction]:
    """Update prediction with actual outcome for model improvement."""
    db_prediction = get_prediction(db, prediction_id)
    if db_prediction:
        db_prediction.actual_outcome = actual_outcome
        db_prediction.feedback_date = datetime.utcnow()
        db.commit()
        db.refresh(db_prediction)
    return db_prediction


# Removed unused CRUD functions for FeatureEngineering, MitigationPlan, and AuditLog
# These tables were never used in the application


# ==================== Model Metrics ====================


def create_model_metrics(db: Session, metrics_data: Dict[str, Any]) -> models.ModelMetrics:
    """Create model metrics record."""
    db_metrics = models.ModelMetrics(**metrics_data)
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics


def get_model_metrics(db: Session, model_type: Optional[str] = None, limit: int = 10) -> List[models.ModelMetrics]:
    """Get model metrics history."""
    query = db.query(models.ModelMetrics)
    if model_type:
        query = query.filter(models.ModelMetrics.model_type == model_type)
    return query.order_by(models.ModelMetrics.evaluation_date.desc()).limit(limit).all()


def get_latest_model_metrics(db: Session, model_type: str) -> Optional[models.ModelMetrics]:
    """Get latest metrics for a specific model type."""
    return (
        db.query(models.ModelMetrics)
        .filter(models.ModelMetrics.model_type == model_type)
        .order_by(models.ModelMetrics.evaluation_date.desc())
        .first()
    )


# ==================== Statistics ====================


def get_prediction_statistics(db: Session) -> Dict[str, Any]:
    """Get overall prediction statistics."""
    total = db.query(models.Prediction).count()
    high_risk = db.query(models.Prediction).filter(models.Prediction.risk_level.like("%High Risk%")).count()
    low_risk = db.query(models.Prediction).filter(models.Prediction.risk_level.like("%Low Risk%")).count()

    return {
        "total_predictions": total,
        "high_risk_count": high_risk,
        "low_risk_count": low_risk,
        "high_risk_percentage": (high_risk / total * 100) if total > 0 else 0,
    }


def get_application_statistics(db: Session) -> Dict[str, Any]:
    """Get loan application statistics."""
    total = db.query(models.LoanApplication).count()
    pending = db.query(models.LoanApplication).filter(models.LoanApplication.application_status == "pending").count()
    approved = db.query(models.LoanApplication).filter(models.LoanApplication.application_status == "approved").count()
    rejected = db.query(models.LoanApplication).filter(models.LoanApplication.application_status == "rejected").count()

    return {"total_applications": total, "pending": pending, "approved": approved, "rejected": rejected}

# backend/database/crud.py
"""
CRUD operations for database models.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.database import models

logger = logging.getLogger(__name__)


# ==================== Loan Applications ====================


def create_loan_application(db: Session, application_data: Dict[str, Any]) -> models.LoanApplication:
    """Create a new loan application."""
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


# ==================== Feature Engineering ====================


def create_feature_engineering(db: Session, fe_data: Dict[str, Any]) -> models.FeatureEngineering:
    """Create a feature engineering record."""
    db_fe = models.FeatureEngineering(**fe_data)
    db.add(db_fe)
    db.commit()
    db.refresh(db_fe)
    return db_fe


def get_feature_engineering(db: Session, fe_id: int) -> Optional[models.FeatureEngineering]:
    """Get feature engineering record by ID."""
    return db.query(models.FeatureEngineering).filter(models.FeatureEngineering.id == fe_id).first()


def get_feature_engineering_history(db: Session, skip: int = 0, limit: int = 50) -> List[models.FeatureEngineering]:
    """Get feature engineering history."""
    return (
        db.query(models.FeatureEngineering)
        .order_by(models.FeatureEngineering.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ==================== Mitigation Plans ====================


def create_mitigation_plan(db: Session, plan_data: Dict[str, Any]) -> models.MitigationPlan:
    """Create a mitigation plan."""
    db_plan = models.MitigationPlan(**plan_data)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def get_mitigation_plan(db: Session, plan_id: int) -> Optional[models.MitigationPlan]:
    """Get mitigation plan by ID."""
    return db.query(models.MitigationPlan).filter(models.MitigationPlan.id == plan_id).first()


def get_mitigation_plans(
    db: Session, skip: int = 0, limit: int = 100, prediction_id: Optional[int] = None
) -> List[models.MitigationPlan]:
    """Get list of mitigation plans."""
    query = db.query(models.MitigationPlan)
    if prediction_id:
        query = query.filter(models.MitigationPlan.prediction_id == prediction_id)
    return query.order_by(models.MitigationPlan.created_at.desc()).offset(skip).limit(limit).all()


def update_mitigation_plan_status(
    db: Session, plan_id: int, implemented: bool, effectiveness_score: Optional[float] = None
) -> Optional[models.MitigationPlan]:
    """Update mitigation plan implementation status."""
    db_plan = get_mitigation_plan(db, plan_id)
    if db_plan:
        db_plan.implemented = implemented
        if implemented:
            db_plan.implementation_date = datetime.utcnow()
        if effectiveness_score is not None:
            db_plan.effectiveness_score = effectiveness_score
        db.commit()
        db.refresh(db_plan)
    return db_plan


# ==================== Audit Logs ====================


def create_audit_log(db: Session, log_data: Dict[str, Any]) -> models.AuditLog:
    """Create an audit log entry."""
    db_log = models.AuditLog(**log_data)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_audit_logs(
    db: Session, skip: int = 0, limit: int = 100, event_type: Optional[str] = None, status: Optional[str] = None
) -> List[models.AuditLog]:
    """Get audit logs."""
    query = db.query(models.AuditLog)
    if event_type:
        query = query.filter(models.AuditLog.event_type == event_type)
    if status:
        query = query.filter(models.AuditLog.status == status)
    return query.order_by(models.AuditLog.created_at.desc()).offset(skip).limit(limit).all()


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

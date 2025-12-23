# backend/database/models.py
"""
Database models for credit risk application.
"""

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from backend.database.config import Base


class LoanApplication(Base):
    """Model for storing loan applications."""

    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)

    # Applicant information
    person_age = Column(Integer)
    person_income = Column(Float)
    person_emp_length = Column(Integer)
    home_ownership = Column(String(50))

    # Loan information
    loan_amnt = Column(Float)
    loan_int_rate = Column(Float)
    loan_percent_income = Column(Float)
    loan_intent = Column(String(50))
    loan_grade = Column(String(10))

    # Credit information
    cb_person_cred_hist_length = Column(Integer)
    default_on_file = Column(String(1))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Additional fields
    application_status = Column(String(50), default="pending")  # pending, approved, rejected
    notes = Column(Text, nullable=True)


class Prediction(Base):
    """Model for storing prediction results."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    # Link to application (optional)
    application_id = Column(Integer, nullable=True)

    # Input features (stored as JSON)
    input_features = Column(JSON)

    # Prediction results
    risk_level = Column(String(50))
    probability_default = Column(Float)
    binary_prediction = Column(Integer)

    # Model information
    model_type = Column(String(50))  # traditional, gemini, comparison
    model_version = Column(String(50), nullable=True)

    # Additional results
    shap_values = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    key_factors = Column(JSON, nullable=True)
    remediation_suggestion = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    prediction_time_ms = Column(Float, nullable=True)

    # Feedback (for model improvement)
    actual_outcome = Column(Integer, nullable=True)  # Actual default status
    feedback_date = Column(DateTime(timezone=True), nullable=True)


# Removed unused tables: FeatureEngineering, MitigationPlan, AuditLog
# These tables were defined but never used in the application


class ModelMetrics(Base):
    """Model for storing model performance metrics."""

    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Model information
    model_type = Column(String(50))
    model_version = Column(String(50))

    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_roc = Column(Float)

    # Additional metrics
    total_predictions = Column(Integer)
    correct_predictions = Column(Integer)
    false_positives = Column(Integer)
    false_negatives = Column(Integer)

    # Metadata
    evaluation_date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)

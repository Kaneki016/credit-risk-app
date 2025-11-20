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


class FeatureEngineering(Base):
    """Model for storing feature engineering results."""

    __tablename__ = "feature_engineering"

    id = Column(Integer, primary_key=True, index=True)

    # Original data
    original_features = Column(JSON)

    # Engineered data
    engineered_features = Column(JSON)
    new_features = Column(JSON)  # List of new feature names

    # Analysis results
    data_quality_score = Column(Float)
    analysis_results = Column(JSON)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_time_ms = Column(Float, nullable=True)


class MitigationPlan(Base):
    """Model for storing mitigation plans."""

    __tablename__ = "mitigation_plans"

    id = Column(Integer, primary_key=True, index=True)

    # Link to prediction
    prediction_id = Column(Integer, nullable=True)

    # Risk assessment
    risk_level = Column(String(50))
    probability_default = Column(Float)

    # Mitigation plan
    overall_strategy = Column(Text)
    immediate_actions = Column(JSON)
    short_term_goals = Column(JSON)
    long_term_improvements = Column(JSON)
    alternative_options = Column(JSON)
    estimated_risk_reduction = Column(String(100))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Follow-up
    implemented = Column(Boolean, default=False)
    implementation_date = Column(DateTime(timezone=True), nullable=True)
    effectiveness_score = Column(Float, nullable=True)


class AuditLog(Base):
    """Model for audit logging."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Event information
    event_type = Column(String(100))  # prediction, feature_engineering, etc.
    event_action = Column(String(100))  # create, update, delete

    # User/session information
    user_id = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)

    # Event details
    details = Column(JSON)

    # Status
    status = Column(String(50))  # success, error
    error_message = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


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

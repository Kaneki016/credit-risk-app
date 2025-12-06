import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from backend.database import models, crud
from backend.database.config import Base

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_dynamic_schema_update(db_session):
    # 1. Verify initial schema
    inspector = inspect(db_session.get_bind())
    columns = [c["name"] for c in inspector.get_columns("loan_applications")]
    assert "person_age" in columns
    assert "new_dynamic_col" not in columns

    # 2. Create application with new column
    app_data = {
        "person_age": 30,
        "person_income": 50000,
        "loan_amnt": 10000,
        "new_dynamic_col": 123.45,
        "another_col": "test_value"
    }

    # This should trigger schema update
    app = crud.create_loan_application(db_session, app_data)

    # 3. Verify schema updated
    inspector = inspect(db_session.get_bind())
    columns = [c["name"] for c in inspector.get_columns("loan_applications")]
    assert "new_dynamic_col" in columns
    assert "another_col" in columns

    # 4. Verify data inserted
    # We need to query using raw SQL or reflect again because the model class is stale
    result = db_session.execute(text("SELECT new_dynamic_col, another_col FROM loan_applications WHERE id = :id"), {"id": app.id}).fetchone()
    assert result[0] == 123.45
    assert result[1] == "test_value"

def test_add_column_idempotency(db_session):
    # Test adding same column twice
    crud.add_column_if_not_exists(db_session, "loan_applications", "test_col", "FLOAT")
    crud.add_column_if_not_exists(db_session, "loan_applications", "test_col", "FLOAT")
    
    inspector = inspect(db_session.get_bind())
    columns = [c["name"] for c in inspector.get_columns("loan_applications")]
    assert "test_col" in columns

def test_insert_with_existing_dynamic_column(db_session):
    # 1. Add a dynamic column manually first
    crud.add_column_if_not_exists(db_session, "loan_applications", "existing_dyn_col", "FLOAT")
    
    # 2. Try to insert data using this column
    # This previously failed because the code only checked for *new* columns, 
    # so it fell back to ORM insert which rejected the unknown kwarg.
    app_data = {
        "person_age": 25,
        "person_income": 60000,
        "loan_amnt": 5000,
        "existing_dyn_col": 999.99
    }
    
    app = crud.create_loan_application(db_session, app_data)
    
    # 3. Verify data
    result = db_session.execute(text("SELECT existing_dyn_col FROM loan_applications WHERE id = :id"), {"id": app.id}).fetchone()
    assert result[0] == 999.99

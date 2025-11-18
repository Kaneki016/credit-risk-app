from pydantic import BaseModel, Field


class LoanApplication(BaseModel):
    # Numeric features
    person_age: int = Field(..., description="Age of the borrower (years).", ge=18, le=100)
    person_income: float = Field(..., description="Annual income in USD")
    person_emp_length: float = Field(..., description="Employment length in months")
    loan_amnt: float = Field(..., description="Loan amount requested in USD")
    loan_int_rate: float = Field(..., description="Loan interest rate as percentage")
    loan_percent_income: float = Field(..., description="Loan amount as percentage of income")
    cb_person_cred_hist_length: float = Field(..., description="Credit history length in years")

    # Categorical fields (match names used by frontend and API)
    home_ownership: str = Field(..., description="Home ownership status (RENT, OWN, MORTGAGE, OTHER)")
    loan_intent: str = Field(..., description="Purpose of the loan")
    loan_grade: str = Field(..., description="Loan grade assigned (A-G)")
    default_on_file: str = Field(..., description="Previous default on file (Y/N)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "person_age": 30,
                    "person_income": 50000.0,
                    "person_emp_length": 12.0,
                    "loan_amnt": 10000.0,
                    "loan_int_rate": 10.0,
                    "loan_percent_income": 0.25,
                    "cb_person_cred_hist_length": 5.0,
                    "home_ownership": "RENT",
                    "loan_intent": "PERSONAL",
                    "loan_grade": "A",
                    "default_on_file": "N"
                }
            ]
        }
    }
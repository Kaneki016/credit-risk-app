# Tests

This directory contains the test suite for the Credit Risk Prediction System.

## Structure

```
tests/
├── __init__.py                    # Test package initialization
├── test_predictor.py              # Unit tests for predictor
├── test_retrain_agent.py          # Tests for model retraining
├── backend/
│   ├── __init__.py
│   └── test_dynamic_api.py        # Integration tests for API (manual)
└── frontend/
    └── __init__.py
```

## Running Tests

### All Tests
```bash
pytest
```

### Specific Test File
```bash
pytest tests/test_predictor.py
```

### With Coverage
```bash
pytest --cov=backend --cov-report=html
```

### Verbose Output
```bash
pytest -v
```

### Quick Mode (less verbose)
```bash
pytest -q
```

## Test Types

### Unit Tests
- `test_predictor.py` - Tests for the prediction model

### Integration Tests
- `test_retrain_agent.py` - Tests for model training pipeline (slow)
- `backend/test_dynamic_api.py` - Manual API integration tests (requires running server)

## Manual Integration Tests

Some tests require the API server to be running:

```bash
# Terminal 1: Start the API
python run.py

# Terminal 2: Run integration tests
python tests/backend/test_dynamic_api.py
```

## Notes

- Integration tests that require training data are automatically skipped if data is unavailable
- API integration tests require the server to be running on `http://localhost:8000`
- For CI/CD, use `pytest --ignore=tests/backend/test_dynamic_api.py` to skip manual tests

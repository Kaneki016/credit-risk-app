# API Quick Reference

## Overview
Simplified API focused on CSV-based batch processing with AI-powered SHAP explanations.

---

## 🎯 Primary Endpoints

### 1. Single Prediction (Recommended)
**Endpoint:** `POST /predict_risk_dynamic`

**Description:** Main endpoint for single predictions. Accepts partial data with intelligent imputation.

**Request:**
```json
{
  "person_income": 50000,
  "loan_amnt": 10000,
  "loan_int_rate": 10.5,
  "home_ownership": "RENT"
}
```

**Response:**
```json
{
  "status": "success",
  "timestamp": "2024-11-19T10:30:00",
  "risk_level": "Borderline Risk 🟠",
  "probability_default_percent": 45.2,
  "binary_prediction": 0,
  "input_features_original": {...},
  "input_features_imputed": {...},
  "imputation_log": ["person_age: historical median", ...],
  "shap_explanation": {
    "loan_percent_income": 0.45,
    "person_income": -0.23,
    ...
  },
  "llm_explanation": "The loan application shows borderline risk primarily due to...",
  "remediation_suggestion": "Consider reducing the loan amount to 30% of income...",
  "data_drift_warnings": [],
  "operational_notes": "Imputed 3 fields: person_age, person_emp_length, loan_grade"
}
```

**Features:**
- ✅ Accepts partial data (missing fields auto-imputed)
- ✅ SHAP explainability
- ✅ AI-generated explanations
- ✅ Risk mitigation advice
- ✅ Data drift detection

---

### 2. Batch Prediction (CSV Upload)
**Endpoint:** `POST /predict_risk_batch`

**Description:** Process multiple loan applications at once. Optimized for CSV uploads.

**Query Parameters:**
- `include_explanations` (boolean, default: false) - Include SHAP and AI explanations

**Request:**
```json
[
  {
    "person_age": 30,
    "person_income": 50000,
    "loan_amnt": 10000
  },
  {
    "person_age": 25,
    "person_income": 35000,
    "loan_amnt": 15000
  }
]
```

**Response (Fast Mode - include_explanations=false):**
```json
{
  "status": "success",
  "timestamp": "2024-11-19T10:30:00",
  "total_processed": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "index": 0,
      "status": "success",
      "risk_level": "Low Risk 🟢",
      "probability_default_percent": 25.3,
      "binary_prediction": 0,
      "input_features": {...},
      "imputation_log": [...]
    },
    {
      "index": 1,
      "status": "success",
      "risk_level": "High Risk 🔴",
      "probability_default_percent": 72.1,
      "binary_prediction": 1,
      "input_features": {...},
      "imputation_log": [...]
    }
  ],
  "errors": []
}
```

**Response (Detailed Mode - include_explanations=true):**
```json
{
  "status": "success",
  "results": [
    {
      "index": 0,
      "risk_level": "Low Risk 🟢",
      "probability_default_percent": 25.3,
      "shap_explanation": {...},
      "llm_explanation": "...",
      "remediation_suggestion": "..."
    }
  ]
}
```

**Usage:**
```bash
# Fast batch processing (predictions only)
curl -X POST "http://localhost:8000/predict_risk_batch" \
  -H "Content-Type: application/json" \
  -d @applications.json

# Detailed batch (with explanations - slower)
curl -X POST "http://localhost:8000/predict_risk_batch?include_explanations=true" \
  -H "Content-Type: application/json" \
  -d @applications.json
```

---

## 🔧 Utility Endpoints

### Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "message": "API is running and model is ready."
}
```

---

### Reload Model
**Endpoint:** `POST /reload_model`

**Description:** Hot-reload the model from disk without restarting the API.

**Response:**
```json
{
  "status": "success",
  "message": "Model reloaded successfully."
}
```

---

### Trigger Retraining
**Endpoint:** `POST /trigger_retrain`

**Description:** Manually trigger model retraining with latest data.

**Response:**
```json
{
  "status": "success",
  "result": {
    "status": "✅ HEALTHY: Model Updated.",
    "auc": 0.8523,
    "threshold": 0.75,
    "artifacts": {...},
    "model_card": {...}
  }
}
```

---

## 💾 Database Endpoints (Optional)

### Database Health
**Endpoint:** `GET /db/health`

**Response:**
```json
{
  "status": "connected",
  "database": "postgresql",
  "message": "Database is operational"
}
```

---

### Get Predictions History
**Endpoint:** `GET /db/predictions?skip=0&limit=100&model_type=xgboost`

**Response:**
```json
{
  "status": "success",
  "count": 50,
  "predictions": [
    {
      "id": 1,
      "risk_level": "Low Risk 🟢",
      "probability_default": 0.25,
      "model_type": "xgboost",
      "created_at": "2024-11-19T10:00:00"
    }
  ]
}
```

---

### Submit Feedback
**Endpoint:** `POST /db/predictions/{prediction_id}/feedback`

**Request:**
```json
{
  "actual_outcome": 0
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback recorded successfully",
  "prediction_id": 123,
  "actual_outcome": 0
}
```

---

### Database Statistics
**Endpoint:** `GET /db/statistics`

**Response:**
```json
{
  "status": "success",
  "predictions": {
    "total": 1000,
    "with_feedback": 250,
    "accuracy": 0.85
  },
  "applications": {
    "total": 500,
    "approved": 300,
    "rejected": 200
  }
}
```

---

### Retrain from Database
**Endpoint:** `POST /db/retrain?min_samples=100&test_size=0.2`

**Response:**
```json
{
  "status": "success",
  "message": "Model retrained successfully",
  "result": {
    "samples_used": 250,
    "test_accuracy": 0.87,
    "auc": 0.89
  }
}
```

---

## 📊 Data Format

### Required Fields (None - all optional!)
All fields are optional. Missing values will be intelligently imputed.

### Recommended Fields
For best predictions, provide:
- `person_income` - Annual income
- `loan_amnt` - Loan amount requested
- `loan_int_rate` - Interest rate
- `person_age` - Applicant age

### All Available Fields
```json
{
  "person_age": 30,
  "person_income": 50000.0,
  "person_emp_length": 36.0,
  "loan_amnt": 10000.0,
  "loan_int_rate": 10.5,
  "loan_percent_income": 0.20,
  "cb_person_cred_hist_length": 5.0,
  "home_ownership": "RENT|OWN|MORTGAGE|OTHER",
  "loan_intent": "PERSONAL|EDUCATION|MEDICAL|VENTURE|HOMEIMPROVEMENT|DEBTCONSOLIDATION",
  "loan_grade": "A|B|C|D|E|F|G",
  "default_on_file": "Y|N"
}
```

---

## 🎨 Response Fields Explained

### Risk Level
- **Low Risk 🟢** - Probability < 40%
- **Borderline Risk 🟠** - Probability 40-60%
- **High Risk 🔴** - Probability > 60%

### SHAP Explanation
Dictionary of feature names to SHAP values:
- **Positive values** - Increase default risk
- **Negative values** - Decrease default risk
- **Magnitude** - Strength of impact

Example:
```json
{
  "loan_percent_income": 0.45,      // Strong risk factor
  "person_income": -0.23,            // Protective factor
  "cb_person_default_on_file_Y": 0.38,  // Previous default increases risk
  "loan_grade_A": -0.15              // Good grade reduces risk
}
```

### LLM Explanation
Natural language summary of the prediction:
- Why the decision was made
- Key contributing factors
- Risk assessment reasoning

### Remediation Suggestion
Actionable advice to reduce risk:
- Specific recommendations
- Alternative options
- Risk reduction strategies

---

## 🚀 Usage Examples

### Python
```python
import requests

# Single prediction
response = requests.post(
    "http://localhost:8000/predict_risk_dynamic",
    json={
        "person_income": 50000,
        "loan_amnt": 10000
    }
)
result = response.json()
print(f"Risk: {result['risk_level']}")
print(f"Probability: {result['probability_default_percent']}%")
print(f"Advice: {result['remediation_suggestion']}")

# Batch prediction
applications = [
    {"person_income": 50000, "loan_amnt": 10000},
    {"person_income": 35000, "loan_amnt": 15000}
]
response = requests.post(
    "http://localhost:8000/predict_risk_batch",
    json=applications
)
results = response.json()
print(f"Processed: {results['total_processed']}")
```

### JavaScript
```javascript
// Single prediction
const response = await fetch('http://localhost:8000/predict_risk_dynamic', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    person_income: 50000,
    loan_amnt: 10000
  })
});
const result = await response.json();
console.log(`Risk: ${result.risk_level}`);
console.log(`Probability: ${result.probability_default_percent}%`);

// Batch prediction with explanations
const batchResponse = await fetch(
  'http://localhost:8000/predict_risk_batch?include_explanations=true',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(applications)
  }
);
const batchResults = await batchResponse.json();
```

### cURL
```bash
# Single prediction
curl -X POST "http://localhost:8000/predict_risk_dynamic" \
  -H "Content-Type: application/json" \
  -d '{
    "person_income": 50000,
    "loan_amnt": 10000
  }'

# Batch prediction (fast)
curl -X POST "http://localhost:8000/predict_risk_batch" \
  -H "Content-Type: application/json" \
  -d '[
    {"person_income": 50000, "loan_amnt": 10000},
    {"person_income": 35000, "loan_amnt": 15000}
  ]'

# Batch with explanations (detailed)
curl -X POST "http://localhost:8000/predict_risk_batch?include_explanations=true" \
  -H "Content-Type: application/json" \
  -d @applications.json
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# Optional - for AI explanations
GEMINI_API_KEY=your-api-key-here

# Optional - database
DATABASE_URL=sqlite:///./credit_risk.db

# Optional - API config
API_HOST=0.0.0.0
API_PORT=8000
```

### Without API Key
System works without `GEMINI_API_KEY`:
- Uses rule-based explanation generation
- Provides basic remediation advice
- All predictions still work

### With API Key
Enhanced features:
- Natural language explanations
- Context-aware advice
- Better remediation strategies

---

## 📈 Performance Tips

### Fast Batch Processing
```bash
# Use include_explanations=false for speed
curl -X POST "http://localhost:8000/predict_risk_batch" \
  -H "Content-Type: application/json" \
  -d @large_file.json
```

### Detailed Analysis
```bash
# Use include_explanations=true for insights
curl -X POST "http://localhost:8000/predict_risk_batch?include_explanations=true" \
  -H "Content-Type: application/json" \
  -d @small_file.json
```

### Recommended Batch Sizes
- **Without explanations:** Up to 10,000 rows
- **With explanations:** Up to 100 rows (due to AI processing time)

---

## 🔍 Interactive Documentation

Visit http://localhost:8000/docs for:
- Interactive API explorer
- Try endpoints directly in browser
- See request/response schemas
- Test with sample data

---

## 📞 Support

- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

**Last Updated:** 2024-11-19
**API Version:** 2.1.0

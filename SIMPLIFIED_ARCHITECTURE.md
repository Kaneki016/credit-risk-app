# Simplified Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           CSV Upload Interface                      │    │
│  │  • Upload CSV file                                  │    │
│  │  • Navigate rows or batch process                   │    │
│  │  • View predictions with explanations               │    │
│  │  • Download results                                 │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Primary Endpoints                                  │    │
│  │  • POST /predict_risk_dynamic (single)              │    │
│  │  • POST /predict_risk_batch (CSV)                   │    │
│  └────────────────────────────────────────────────────┘    │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Data Processing Pipeline                           │    │
│  │  1. Validate input                                  │    │
│  │  2. Impute missing values                           │    │
│  │  3. One-hot encode categoricals                     │    │
│  │  4. Scale features                                  │    │
│  └────────────────────────────────────────────────────┘    │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  XGBoost Model                                      │    │
│  │  • Predict default probability                      │    │
│  │  • Generate SHAP values                             │    │
│  └────────────────────────────────────────────────────┘    │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  AI Explanation Layer (Optional)                    │    │
│  │  • Convert SHAP to natural language                 │    │
│  │  • Generate risk mitigation advice                  │    │
│  │  • Fallback to rule-based if no API key            │    │
│  └────────────────────────────────────────────────────┘    │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Response Assembly                                  │    │
│  │  • Risk level & probability                         │    │
│  │  • SHAP explanations                                │    │
│  │  • AI-generated insights                            │    │
│  │  • Remediation suggestions                          │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Database (Optional - PostgreSQL/SQLite)         │
│  • Store predictions                                         │
│  • Collect feedback                                          │
│  • Enable retraining                                         │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Single Prediction Flow

```
User Input (Partial Data)
    │
    ▼
┌─────────────────────┐
│ Data Validation     │
│ • Check types       │
│ • Normalize values  │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Smart Imputation    │
│ • Historical stats  │
│ • Derived values    │
│ • Safe defaults     │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Feature Engineering │
│ • One-hot encoding  │
│ • Feature mapping   │
│ • Scaling           │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ XGBoost Prediction  │
│ • Probability       │
│ • Binary decision   │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ SHAP Analysis       │
│ • Feature impact    │
│ • Contribution      │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ AI Explanation      │
│ • Natural language  │
│ • Risk advice       │
└─────────────────────┘
    │
    ▼
JSON Response with:
• Risk level
• Probability
• SHAP values
• Explanation
• Advice
```

### Batch Processing Flow

```
CSV File Upload
    │
    ▼
┌─────────────────────┐
│ Parse CSV           │
│ • Read rows         │
│ • Validate format   │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Process Each Row    │
│ (parallel possible) │
└─────────────────────┘
    │
    ├─► Row 1 ─► Predict ─► Result 1
    ├─► Row 2 ─► Predict ─► Result 2
    ├─► Row 3 ─► Predict ─► Result 3
    └─► Row N ─► Predict ─► Result N
    │
    ▼
┌─────────────────────┐
│ Aggregate Results   │
│ • Success count     │
│ • Error handling    │
└─────────────────────┘
    │
    ▼
JSON Response with:
• All predictions
• Statistics
• Errors (if any)
```

## Component Responsibilities

### Frontend (React)
**Purpose:** User interface for CSV upload and result visualization

**Responsibilities:**
- CSV file upload and parsing
- Row-by-row navigation
- Batch processing trigger
- Result display with SHAP visualizations
- Export results to CSV

**Key Files:**
- `frontend/src/App.jsx` - Main application
- `frontend/src/components/csv/CSVUploader.jsx` - File upload
- `frontend/src/components/csv/DynamicForm.jsx` - Row navigation
- `frontend/src/components/results/ResultCard.jsx` - Result display

---

### Backend API (FastAPI)
**Purpose:** REST API for predictions and model management

**Responsibilities:**
- Request validation
- Endpoint routing
- Response formatting
- Error handling
- CORS management

**Key Files:**
- `backend/api/main.py` - API endpoints
- `backend/core/schemas.py` - Request/response schemas
- `backend/core/config.py` - Configuration

---

### Predictor (XGBoost)
**Purpose:** Core ML model for credit risk prediction

**Responsibilities:**
- Load trained model
- Make predictions
- Generate SHAP values
- Feature preprocessing

**Key Files:**
- `backend/models/predictor.py` - Base predictor
- `backend/models/dynamic_predictor.py` - Dynamic input handler

---

### Imputation Service
**Purpose:** Handle missing data intelligently

**Responsibilities:**
- Detect missing values
- Apply imputation strategies
- Log imputation actions
- Validate imputed data

**Key Files:**
- `backend/services/imputation.py` - Imputation logic

**Strategies:**
1. **Derived Values** - Calculate from other fields (e.g., loan_percent_income)
2. **Historical Stats** - Use median/mode from training data
3. **Safe Defaults** - Domain-specific fallback values

---

### AI Explanation Layer (Gemini)
**Purpose:** Convert SHAP values to natural language

**Responsibilities:**
- Generate explanations from SHAP values
- Provide risk mitigation advice
- Fallback to rule-based logic

**Key Files:**
- `backend/api/main.py` - `generate_llm_explanation()` function

**Modes:**
- **With API Key:** Uses Gemini AI for natural language generation
- **Without API Key:** Uses rule-based explanation logic

---

### Database Layer (Optional)
**Purpose:** Persist predictions and enable retraining

**Responsibilities:**
- Store predictions
- Collect feedback
- Track model performance
- Enable retraining

**Key Files:**
- `backend/database/models.py` - Database schema
- `backend/database/crud.py` - Database operations

---

### Retraining Service
**Purpose:** Automated model improvement

**Responsibilities:**
- Monitor model performance
- Retrain when needed
- Generate model cards
- Version management

**Key Files:**
- `backend/services/retraining.py` - Retraining logic
- `backend/services/database_retraining.py` - DB-based retraining

---

## Key Design Decisions

### 1. Single Prediction Workflow
**Decision:** Remove manual entry, focus on CSV upload

**Rationale:**
- Simpler user experience
- Batch processing is primary use case
- Reduces code complexity
- Easier to maintain

**Impact:**
- Removed manual entry form
- Single, focused interface
- Better for production use

---

### 2. Integrated AI Explanations
**Decision:** AI enhances ML predictions rather than replacing them

**Rationale:**
- XGBoost provides accurate predictions
- SHAP provides technical explainability
- AI adds natural language layer
- Best of both worlds

**Impact:**
- Removed separate Gemini prediction endpoints
- AI integrated into main flow
- Consistent explanation format

---

### 3. Optional Explanations in Batch
**Decision:** Make explanations optional in batch processing

**Rationale:**
- Explanations are slow (AI API calls)
- Not always needed for all rows
- User can choose speed vs detail

**Impact:**
- Fast mode for large batches
- Detailed mode for analysis
- Better performance

---

### 4. Graceful Degradation
**Decision:** System works without Gemini API key

**Rationale:**
- Not everyone has API key
- Core functionality shouldn't depend on external service
- Fallback provides basic explanations

**Impact:**
- Rule-based explanation fallback
- System always functional
- API key is optional enhancement

---

### 5. Smart Imputation
**Decision:** Accept partial data with intelligent imputation

**Rationale:**
- Real-world data is often incomplete
- Users shouldn't be blocked by missing fields
- Historical data provides good defaults

**Impact:**
- More flexible input
- Better user experience
- Transparent imputation logging

---

## API Endpoint Strategy

### Before Simplification
```
POST /predict_risk              (complete data only)
POST /predict_risk_dynamic      (partial data OK)
POST /predict_risk_gemini       (Gemini AI only)
POST /predict_risk_compare      (compare models)
POST /get_mitigation_plan       (separate advice)
POST /analyze_features          (feature analysis)
POST /engineer_features         (feature engineering)
POST /predict_risk_batch        (batch processing)
```

### After Simplification
```
POST /predict_risk_dynamic      (primary - single prediction)
POST /predict_risk_batch        (primary - batch processing)
POST /predict_risk              (legacy - backward compatibility)
```

**Benefits:**
- 3 endpoints instead of 8
- Clear primary endpoints
- Easier to understand
- Less maintenance

---

## Technology Stack

### Core Technologies
- **Python 3.10+** - Backend language
- **FastAPI** - Web framework
- **XGBoost** - ML model
- **SHAP** - Explainability
- **React 18** - Frontend framework
- **Vite** - Build tool

### Optional Technologies
- **Google Gemini** - AI explanations (optional)
- **PostgreSQL/SQLite** - Database (optional)
- **Docker** - Containerization (optional)

### Key Libraries
```python
# ML & Data
xgboost==3.1.1
scikit-learn==1.7.2
pandas==2.3.3
numpy==2.3.4
shap==0.50.0

# API
fastapi==0.121.1
uvicorn==0.38.0
pydantic==2.12.4

# AI (optional)
google-generativeai==0.8.3

# Database (optional)
sqlalchemy>=2.0.0
alembic>=1.13.0
```

---

## Performance Characteristics

### Single Prediction
- **Latency:** 50-200ms (without AI)
- **Latency:** 500-2000ms (with AI explanations)
- **Throughput:** ~100 requests/second

### Batch Processing (Fast Mode)
- **Speed:** ~1000 rows/second
- **Memory:** ~100MB for 10,000 rows
- **Recommended:** Up to 10,000 rows per batch

### Batch Processing (Detailed Mode)
- **Speed:** ~5-10 rows/second (AI bottleneck)
- **Memory:** ~200MB for 100 rows
- **Recommended:** Up to 100 rows per batch

---

## Security Considerations

### API Security
- CORS configured for local development
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy
- No authentication (add if needed)

### Data Privacy
- No PII stored by default
- Database is optional
- Predictions not logged unless database enabled
- API key stored in environment variables

### Recommendations for Production
1. Add authentication (JWT, OAuth)
2. Enable HTTPS
3. Rate limiting
4. Input sanitization
5. Audit logging
6. Data encryption

---

## Monitoring & Observability

### Built-in Monitoring
- Health check endpoint (`/health`)
- Structured logging
- Error tracking
- Performance metrics

### Database Statistics
- Prediction count
- Accuracy tracking
- Feedback collection
- Model performance

### Recommended Additions
- Prometheus metrics
- Grafana dashboards
- Error alerting
- Performance monitoring

---

## Deployment Options

### Development
```bash
# Backend
python run.py

# Frontend
cd frontend && npm run dev
```

### Docker
```bash
docker-compose up -d
```

### Production
- Use production WSGI server (Gunicorn)
- Enable database for persistence
- Add reverse proxy (Nginx)
- Configure monitoring
- Set up CI/CD

---

## Future Enhancements

### Planned Features
1. **Advanced Analytics Dashboard**
   - Prediction trends
   - Model performance over time
   - Feature importance visualization

2. **Real-time Monitoring**
   - Live prediction feed
   - Performance metrics
   - Alert system

3. **Enhanced Visualizations**
   - Interactive SHAP plots
   - Risk distribution charts
   - Comparison views

4. **API Improvements**
   - GraphQL endpoint
   - WebSocket support
   - Streaming predictions

5. **Model Improvements**
   - Ensemble models
   - AutoML integration
   - A/B testing framework

---

## Maintenance Guide

### Regular Tasks
1. **Monitor model performance** - Check AUC, accuracy
2. **Review predictions** - Spot-check results
3. **Update dependencies** - Security patches
4. **Backup database** - If using database
5. **Review logs** - Check for errors

### Retraining Schedule
- **Automatic:** When performance drops below threshold
- **Manual:** Monthly or quarterly
- **Triggered:** When significant data drift detected

### Version Management
- Models versioned with timestamps
- Manifest tracks all versions
- Easy rollback to previous versions
- Model cards document changes

---

**Last Updated:** 2024-11-19
**Architecture Version:** 2.1.0

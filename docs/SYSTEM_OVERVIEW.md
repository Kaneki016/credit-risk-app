# System Overview

## What This System Does

The Credit Risk Prediction System is a comprehensive, production-ready application for assessing loan default risk. It combines traditional machine learning with modern AI capabilities to provide accurate, explainable, and actionable credit risk assessments.

---

## Core Functionality

### 1. Credit Risk Prediction

**Purpose**: Predict the probability that a loan applicant will default on their loan.

**How It Works**:
1. User provides loan application data (complete or partial)
2. System intelligently fills missing values using historical statistics
3. XGBoost model calculates default probability (0-100%)
4. Risk is classified into three levels:
   - **Low Risk 🟢**: Probability < 40% - Loan likely to be repaid
   - **Borderline Risk 🟠**: Probability 40-60% - Requires careful consideration
   - **High Risk 🔴**: Probability > 60% - High likelihood of default

**Key Features**:
- Accepts partial data (missing fields auto-imputed)
- Handles single predictions and batch processing
- Provides probability scores and binary predictions
- Supports CSV upload for bulk processing

---

### 2. Explainable AI (SHAP)

**Purpose**: Explain why a loan was approved or rejected by showing which factors contributed most to the decision.

**How It Works**:
1. SHAP (SHapley Additive exPlanations) values are calculated for each feature
2. Features are ranked by their impact on the prediction
3. Visual and numerical explanations show:
   - Which factors increased risk (positive SHAP values)
   - Which factors decreased risk (negative SHAP values)
   - The magnitude of each factor's contribution

**Benefits**:
- Transparency in decision-making
- Regulatory compliance (explainable AI)
- Helps users understand model reasoning
- Identifies key risk factors for each application

---

### 3. AI-Powered Insights

**Purpose**: Generate human-readable explanations and actionable advice using natural language processing.

**How It Works**:
1. SHAP values and prediction results are sent to AI service (OpenRouter/Gemini)
2. AI generates:
   - Natural language explanation of the decision
   - Risk mitigation suggestions
   - Actionable recommendations to improve loan approval chances

**Features**:
- Works with OpenRouter (primary) or Gemini (fallback)
- Rule-based fallback if AI unavailable
- Context-aware explanations
- Professional, client-friendly language

---

### 4. CSV Batch Processing

**Purpose**: Process multiple loan applications efficiently from CSV files.

**How It Works**:
1. User uploads CSV file with loan applications
2. System automatically:
   - Detects CSV column structure
   - Maps columns to database fields (fuzzy matching)
   - Validates data types
3. User can:
   - Process rows individually (navigate with Previous/Next)
   - Batch process all rows at once
   - Download results as CSV

**Features**:
- Automatic column mapping
- Dynamic schema adaptation
- Row-by-row navigation
- Batch processing mode
- Export results with predictions

---

### 5. Dynamic Schema Management

**Purpose**: Automatically adapt to different CSV structures without manual configuration.

**How It Works**:
1. System detects CSV column names
2. Fuzzy matching maps CSV columns to database fields
3. New columns are automatically added to schema
4. User can manually adjust mappings if needed

**Supported Operations**:
- Add new columns dynamically
- Replace entire schema (optional)
- Preserve existing data
- Map various column name formats

---

### 6. Model Training & Retraining

**Purpose**: Train and update models with new data to improve accuracy over time.

**How It Works**:
1. Import historical loan data (with outcomes) via CSV
2. System automatically:
   - Detects target column (loan_status, default, etc.)
   - Identifies numeric and categorical features
   - Handles various data formats
3. Train new XGBoost model with:
   - Automatic feature engineering
   - Cross-validation
   - Performance metrics
4. Reload model to activate changes

**Features**:
- Flexible training (any CSV structure)
- Automatic feature detection
- Model versioning
- Performance tracking
- Hot-reload capability

---

### 7. Database Management

**Purpose**: Store predictions, historical data, and training records for analysis and retraining.

**What's Stored**:
- **Loan Applications**: Original application data
- **Predictions**: Risk predictions with probabilities
- **Feedback**: Actual outcomes (for retraining)
- **Training Records**: Model versions and metrics

**Operations**:
- Import CSV data
- Clear database (with schema reset option)
- View statistics
- Export data

---

### 8. Admin Panel

**Purpose**: Comprehensive interface for managing data, models, and system status.

**Tabs**:

1. **Import Data**
   - Upload CSV files
   - Column mapping interface
   - Schema management
   - Import statistics

2. **Train Model**
   - Upload training CSV
   - Automatic feature detection
   - Model training interface
   - Model state monitoring
   - Model reloading

3. **Status**
   - Database statistics
   - API health checks
   - Model state information
   - System metrics

---

### 9. Chatbot Assistant

**Purpose**: Interactive AI assistant for querying database and getting system help.

**Capabilities**:
- Query database statistics
- View recent predictions
- Check model performance
- Get usage guidance
- Answer system questions

**Features**:
- Always available (bottom-right corner)
- Quick action buttons
- Natural language queries
- Context-aware responses

---

## Technical Architecture

### Backend (FastAPI)
- **Framework**: FastAPI (Python)
- **ML Model**: XGBoost
- **Explainability**: SHAP
- **Database**: SQLite (default), PostgreSQL support
- **AI Services**: OpenRouter (primary), Gemini (fallback)
- **API**: RESTful with OpenAPI documentation

### Frontend (React)
- **Framework**: React 18+
- **Build Tool**: Vite
- **Styling**: CSS with animations
- **Animations**: Framer Motion
- **State Management**: React Hooks

### Data Flow

```
User Input (CSV/Form)
    ↓
Frontend Processing
    ↓
API Request
    ↓
Data Imputation (if needed)
    ↓
XGBoost Prediction
    ↓
SHAP Explanation
    ↓
AI Enhancement (optional)
    ↓
Response with Results
    ↓
Database Storage
    ↓
Display to User
```

---

## Use Cases

### 1. Loan Officer Workflow
- Upload batch of loan applications
- Review predictions with explanations
- Make informed approval decisions
- Export results for reporting

### 2. Risk Management
- Monitor risk distribution
- Analyze feature importance
- Track model performance
- Generate risk reports

### 3. Model Development
- Import historical data
- Train new models
- Compare model versions
- Improve accuracy over time

### 4. Compliance & Auditing
- Explainable predictions (SHAP)
- Audit trail (database records)
- Model versioning
- Performance tracking

---

## Key Differentiators

1. **Flexible Input**: Accepts partial data with intelligent imputation
2. **Explainable**: SHAP values show why each decision was made
3. **AI-Enhanced**: Natural language explanations and advice
4. **Dynamic Schema**: Adapts to any CSV structure automatically
5. **Production-Ready**: Comprehensive error handling, logging, testing
6. **User-Friendly**: Intuitive interface with chatbot assistance
7. **Extensible**: Modular architecture for easy customization

---

## System Requirements

### Minimum
- Python 3.10+
- Node.js 18+
- 2GB RAM
- 500MB disk space

### Recommended
- Python 3.11+
- Node.js 20+
- 4GB RAM
- 1GB disk space
- GPU (optional, for faster training)

---

## Performance Characteristics

- **Single Prediction**: ~100-200ms (with explanations)
- **Batch Processing**: ~50-100ms per application
- **Model Training**: 1-5 minutes (depending on data size)
- **CSV Import**: ~1000 rows/second
- **Concurrent Requests**: Supports multiple simultaneous predictions

---

## Security & Privacy

- **Data Storage**: Local database (SQLite) or secure PostgreSQL
- **API Keys**: Stored in environment variables (never in code)
- **Rate Limiting**: Built-in protection against abuse
- **CORS**: Configured for development and production
- **Input Validation**: Comprehensive validation on all inputs

---

## Future Enhancements (Planned)

- Real-time monitoring dashboard
- Advanced analytics and reporting
- Multi-model ensemble predictions
- Automated retraining schedules
- Integration with external credit bureaus
- Mobile app support

---

## Support & Maintenance

- **Logging**: Comprehensive logging for debugging
- **Error Handling**: Graceful error handling with user-friendly messages
- **Testing**: Unit and integration tests
- **Documentation**: Extensive documentation and guides
- **Updates**: Regular updates and improvements

---

This system provides a complete solution for credit risk assessment, combining the accuracy of machine learning with the transparency of explainable AI and the convenience of modern web interfaces.

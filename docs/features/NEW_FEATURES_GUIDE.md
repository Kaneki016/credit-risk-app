# New Features Guide

## 🎉 What's New

Two powerful new features have been added to your Credit Risk application:

1. **Clear Database Button** - Easily clear all database records
2. **Flexible Model Training** - Train models with any CSV structure

---

## 1. Clear Database Feature

### Overview
A new "Manage" tab in the Admin Panel allows you to clear all data from the database with a single click.

### Location
**Admin Panel → Manage Tab → Clear Database**

### What It Does
Permanently deletes ALL data including:
- ✓ All predictions
- ✓ All loan applications
- ✓ All feature engineering records
- ✓ All mitigation plans
- ✓ All audit logs
- ✓ All model metrics

### How to Use

1. **Navigate to Admin Panel**
   - Click "🔧 Admin" button in the header

2. **Go to Manage Tab**
   - Click "🗑️ Manage" tab

3. **Clear Database**
   - Click "🗑️ Clear Database" button
   - Confirm the action (safety check)
   - Wait for completion

### Safety Features
- ⚠️ **Two-step confirmation** required
- ⚠️ **Clear warning messages** about data loss
- ⚠️ **Cannot be undone** - use with caution
- ✓ Shows summary of deleted records

### API Endpoint
```
DELETE /db/clear?confirm=true
```

### Response Example
```json
{
  "status": "success",
  "message": "Database cleared successfully",
  "deleted": {
    "predictions": 150,
    "loan_applications": 75,
    "feature_engineering": 20,
    "mitigation_plans": 30,
    "audit_logs": 100,
    "model_metrics": 5
  },
  "total_deleted": 380
}
```

### Use Cases
- 🧪 **Testing**: Clear test data between test runs
- 🔄 **Reset**: Start fresh with new data
- 🧹 **Cleanup**: Remove old/invalid data
- 📊 **Demo**: Reset for demonstrations

---

## 2. Flexible Model Training

### Overview
Train credit risk models with **any CSV structure**. The system automatically detects columns and features - no need to match exact column names!

### Location
**Admin Panel → Train Model Tab**

### What It Does
Automatically detects:
- ✓ **Target column** (loan_status, default, target, label, outcome, etc.)
- ✓ **Numeric features** (income, loan amount, age, etc.)
- ✓ **Categorical features** (home ownership, loan grade, etc.)
- ✓ **Feature types** (continuous vs discrete)

### Supported Target Column Names
The system recognizes these target column names:
- `loan_status`
- `default`
- `target`
- `label`
- `outcome`
- Any binary column (0/1, yes/no, true/false)

### Supported Target Values
Automatically maps these values:
- `default` / `no_default` → 1 / 0
- `yes` / `no` → 1 / 0
- `y` / `n` → 1 / 0
- `true` / `false` → 1 / 0
- `approved` / `rejected` → 0 / 1
- `good` / `bad` → 0 / 1
- `1` / `0` → 1 / 0

### How to Use

1. **Prepare Your CSV**
   - Include credit risk data (any structure)
   - Must have a target column (see supported names above)
   - Can have any feature columns

2. **Navigate to Admin Panel**
   - Click "🔧 Admin" button

3. **Go to Train Model Tab**
   - Click "🎯 Train Model" tab

4. **Upload CSV**
   - Click to select your CSV file
   - File can have any column names

5. **Train Model**
   - Click "🎯 Train New Model"
   - Wait for training to complete (may take a few minutes)

6. **Review Results**
   - See detected features
   - Check model metrics (accuracy, AUC-ROC)
   - View preprocessing information

7. **Reload Model**
   - Click "🔄 Reload Model in API"
   - New model is now active

### Example CSV Structures

#### Example 1: Standard Format
```csv
loan_status,income,loan_amount,credit_score,employment_years
default,35000,15000,650,2
no_default,75000,20000,720,8
default,28000,25000,580,1
```

#### Example 2: Different Column Names
```csv
target,annual_income,requested_amount,fico_score,job_tenure
1,35000,15000,650,2
0,75000,20000,720,8
1,28000,25000,580,1
```

#### Example 3: With Categorical Features
```csv
outcome,income,loan_amt,home_type,loan_purpose,grade
bad,35000,15000,RENT,PERSONAL,D
good,75000,20000,MORTGAGE,HOME,A
bad,28000,25000,RENT,DEBT,F
```

**All three formats work!** The system automatically detects the structure.

### API Endpoint
```
POST /train/flexible
Content-Type: multipart/form-data
```

### Response Example
```json
{
  "status": "success",
  "message": "Model trained successfully with flexible column detection",
  "result": {
    "model_path": "models/credit_risk_model_v20251120T120000Z.pkl",
    "metrics": {
      "accuracy": 0.8542,
      "precision": 0.8123,
      "recall": 0.7891,
      "f1_score": 0.8005,
      "auc_roc": 0.9123
    },
    "preprocessing_info": {
      "target_column": "loan_status",
      "numeric_features": ["income", "loan_amount", "credit_score"],
      "categorical_features": ["home_type", "loan_purpose"],
      "n_features": 15,
      "n_samples": 1000
    },
    "training_info": {
      "n_train": 800,
      "n_test": 200,
      "test_size": 0.2
    }
  }
}
```

### Features

#### Automatic Column Detection
- Scans CSV for target column
- Identifies numeric vs categorical features
- Handles missing values
- One-hot encodes categorical variables

#### Flexible Target Mapping
- Converts text labels to binary (0/1)
- Handles various naming conventions
- Warns about unmapped values

#### Smart Feature Engineering
- Automatically scales numeric features
- One-hot encodes categorical features
- Handles missing data with median/mode
- Creates feature names for tracking

#### Model Training
- Uses XGBoost classifier
- 80/20 train-test split
- Calculates comprehensive metrics
- Saves model with metadata

### Benefits

✓ **No Column Name Restrictions** - Use your own column names
✓ **Automatic Detection** - System figures out the structure
✓ **Flexible Data** - Works with various CSV formats
✓ **Quick Training** - Train new models in minutes
✓ **Full Metrics** - See accuracy, precision, recall, F1, AUC-ROC
✓ **Easy Integration** - Reload model immediately

### Use Cases

1. **Different Data Sources**
   - Train with data from different systems
   - Each system may have different column names
   - No need to rename columns

2. **Custom Features**
   - Add your own features
   - System automatically detects them
   - No code changes needed

3. **Experimentation**
   - Try different feature sets
   - Quick iteration
   - Compare model performance

4. **Client-Specific Models**
   - Train models for specific clients
   - Each client may have different data format
   - One system handles all

### Tips

💡 **Column Names**: Use descriptive names (income, loan_amount, etc.)
💡 **Target Column**: Make sure it's clearly named (loan_status, default, etc.)
💡 **Data Quality**: Clean data = better models
💡 **Sample Size**: More data = better accuracy (aim for 1000+ rows)
💡 **Balance**: Try to have balanced classes (similar number of defaults and non-defaults)

### Troubleshooting

**Issue**: "Could not detect target column"
- **Solution**: Rename your target column to one of the supported names (loan_status, default, target, etc.)

**Issue**: "Training failed"
- **Solution**: Check CSV format, ensure no corrupted data, verify target column has binary values

**Issue**: "Low accuracy"
- **Solution**: Need more data, check data quality, ensure features are relevant

**Issue**: "Model not loading"
- **Solution**: Click "🔄 Reload Model in API" after training

---

## Quick Start

### Clear Database
```bash
# Via API
curl -X DELETE "http://localhost:8000/db/clear?confirm=true"

# Via UI
Admin Panel → Manage → Clear Database → Confirm
```

### Train Flexible Model
```bash
# Via API
curl -X POST "http://localhost:8000/train/flexible" \
  -F "file=@your_data.csv"

# Via UI
Admin Panel → Train Model → Upload CSV → Train New Model
```

---

## Architecture

### Backend Components

1. **clear_database_endpoint.py**
   - Handles database clearing
   - Safety checks
   - Transaction management

2. **flexible_training.py**
   - Column detection
   - Feature engineering
   - Model training
   - Metrics calculation

3. **main.py**
   - API endpoints
   - Request handling
   - Error management

### Frontend Components

1. **AdminPanel.jsx**
   - New "Train Model" tab
   - New "Manage" tab
   - File upload handling
   - Result display

2. **admin.css**
   - Danger zone styling
   - Feature list styling
   - Confirmation dialogs

---

## Security Considerations

### Clear Database
- ⚠️ Requires explicit confirmation
- ⚠️ Logs all clear operations
- ⚠️ Cannot be undone
- ⚠️ Consider adding authentication in production

### Flexible Training
- ✓ Validates CSV format
- ✓ Handles errors gracefully
- ✓ Cleans up temporary files
- ✓ Logs all training operations

---

## Future Enhancements

Potential improvements:
1. **Backup before clear** - Automatic backup before clearing
2. **Selective clear** - Clear only specific tables
3. **Column mapping UI** - Manual column mapping interface
4. **Model comparison** - Compare multiple trained models
5. **Scheduled training** - Automatic retraining on schedule
6. **A/B testing** - Test multiple models simultaneously

---

## Summary

✅ **Clear Database**: Easy database management with safety checks
✅ **Flexible Training**: Train models with any CSV structure
✅ **Automatic Detection**: No manual configuration needed
✅ **Full Integration**: Works seamlessly with existing system
✅ **Production Ready**: Tested and documented

Your credit risk application is now more flexible and easier to manage!

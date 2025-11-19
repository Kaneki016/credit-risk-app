# Admin Panel Guide

## Overview

The Admin Panel provides a user-friendly interface for importing CSV data and retraining the model directly from the web browser.

---

## 🎯 Features

### 1. Import Data Tab
- Upload CSV files with loan data
- Automatic import into database
- Real-time progress feedback
- Error handling and reporting

### 2. Retrain Model Tab
- Check retraining readiness
- View database statistics
- Trigger model retraining
- View training metrics
- Hot-reload model without restart

### 3. Status Tab
- System overview
- Database statistics
- Retraining requirements
- Real-time status updates

---

## 🚀 How to Use

### Access the Admin Panel

1. **Start the application**
   ```bash
   # Terminal 1 - Backend
   python run.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

2. **Open in browser**
   ```
   http://localhost:5173
   ```

3. **Click "🔧 Admin" button** in the top right

---

## 📥 Import Data

### Step 1: Prepare Your CSV File

Your CSV should have these columns:
- `person_age`, `person_income`, `person_emp_length`
- `person_home_ownership`, `loan_amnt`, `loan_intent`
- `loan_grade`, `loan_int_rate`, `loan_percent_income`
- `cb_person_default_on_file`, `cb_person_cred_hist_length`
- **`loan_status`** (0 = no default, 1 = default) - **Required!**

Example CSV:
```csv
person_age,person_income,loan_amnt,loan_status
30,50000,10000,0
25,35000,15000,1
45,75000,20000,0
```

### Step 2: Upload File

1. Click **"Import Data"** tab
2. Click the upload area or drag & drop your CSV file
3. Click **"📥 Import Data"** button
4. Wait for import to complete

### Step 3: View Results

You'll see:
- ✅ Number of rows imported
- ⚠️ Number of errors (if any)
- Success message

---

## 🔄 Retrain Model

### Step 1: Check Readiness

1. Click **"Retrain Model"** tab
2. View the status card showing:
   - Total predictions in database
   - Predictions with feedback
   - Feedback ratio
   - Ready status (✅ or ❌)

### Requirements for Retraining:
- **Minimum 100 predictions** with actual outcomes
- **At least 1% feedback ratio**

### Step 2: Start Retraining

1. Click **"🔄 Start Retraining"** button
2. Wait for training to complete (may take 30-60 seconds)
3. View training metrics:
   - Training samples
   - Test samples
   - Accuracy
   - AUC-ROC score

### Step 3: Reload Model

After retraining completes:
1. Click **"🔄 Reload Model in API"** button
2. Model is now active and ready to use!

---

## 📊 Status Tab

View system overview:

### Database Card
- Total predictions stored
- Predictions with feedback

### Retraining Card
- Ready status
- Feedback percentage

### Requirements Card
- Minimum samples needed
- Minimum feedback ratio

Click **"🔄 Refresh Status"** to update.

---

## 🎨 UI Features

### Visual Feedback
- ✅ Success messages in green
- ❌ Error messages in red
- ⏳ Loading indicators
- 📊 Real-time statistics

### Responsive Design
- Works on desktop and mobile
- Adaptive layouts
- Touch-friendly buttons

### Smooth Animations
- Tab transitions
- Result cards
- Status updates

---

## 🔧 API Endpoints Used

The admin panel uses these endpoints:

### Import Data
```
POST /db/import_csv
Content-Type: multipart/form-data
Body: CSV file
```

### Check Retraining Status
```
GET /db/retraining/status
```

### Trigger Retraining
```
POST /db/retrain
```

### Reload Model
```
POST /reload_model
```

---

## 📝 Example Workflow

### Complete Import and Retrain Flow:

1. **Prepare Data**
   - Export your loan data to CSV
   - Include `loan_status` column with actual outcomes

2. **Import**
   - Open Admin Panel
   - Go to "Import Data" tab
   - Upload CSV file
   - Wait for import (shows progress)

3. **Verify**
   - Go to "Status" tab
   - Check total predictions
   - Verify feedback count

4. **Retrain**
   - Go to "Retrain Model" tab
   - Check readiness status
   - Click "Start Retraining"
   - Wait for completion

5. **Activate**
   - Click "Reload Model in API"
   - Model is now active!

6. **Test**
   - Go back to "Predictions" view
   - Upload test CSV
   - See improved predictions!

---

## ⚠️ Important Notes

### Data Requirements
- CSV must have `loan_status` column
- Values should be 0 (no default) or 1 (default)
- Other columns can have missing values (will be imputed)

### Retraining Requirements
- Need at least 100 predictions with feedback
- More data = better model
- Recommended: 1,000+ samples for production

### Performance
- Import: ~1,000 rows/second
- Retraining: 30-60 seconds for 10,000 samples
- Model reload: Instant

### Browser Compatibility
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Responsive design

---

## 🆘 Troubleshooting

### Import Fails
**Problem:** "Error importing data"

**Solutions:**
- Check CSV format (must be valid CSV)
- Ensure `loan_status` column exists
- Check for special characters in data
- Try smaller file first (test with 100 rows)

### Retraining Not Ready
**Problem:** "Not ready to retrain"

**Solutions:**
- Import more data (need 100+ samples)
- Ensure data has `loan_status` column
- Check feedback ratio (need 1%+)

### Model Not Loading
**Problem:** "Model reload failed"

**Solutions:**
- Check if backend is running
- Restart backend: `python run.py`
- Check logs for errors
- Verify model files exist in `models/` directory

### Upload Button Disabled
**Problem:** Can't click import button

**Solutions:**
- Select a file first
- Ensure file is .csv format
- Check file size (max 100MB recommended)
- Try refreshing the page

---

## 💡 Tips & Best Practices

### Data Preparation
1. **Clean your data** before import
2. **Include actual outcomes** (loan_status)
3. **Remove duplicates**
4. **Handle missing values** (or let system impute)

### Retraining Strategy
1. **Start with baseline** (import initial dataset)
2. **Collect feedback** (actual outcomes)
3. **Retrain periodically** (weekly/monthly)
4. **Monitor performance** (check accuracy)

### Production Use
1. **Backup before retraining**
   ```bash
   cp -r models models_backup
   cp credit_risk.db credit_risk_backup.db
   ```

2. **Test new model** before deploying
3. **Keep version history** (manifest.json)
4. **Monitor predictions** after retraining

### Performance Optimization
1. **Import in batches** (10,000 rows at a time)
2. **Retrain during off-hours**
3. **Use hot reload** instead of restart
4. **Clear old data** periodically

---

## 📈 Monitoring

### After Retraining, Check:

1. **Accuracy** - Should be >85%
2. **AUC-ROC** - Should be >0.85 (>0.9 is excellent)
3. **Precision/Recall** - Balance between false positives/negatives
4. **F1 Score** - Overall model quality

### Red Flags:
- ⚠️ Accuracy drops after retraining
- ⚠️ AUC-ROC below 0.75
- ⚠️ High false positive rate
- ⚠️ Model fails to load

**If you see these, rollback to previous version!**

---

## 🔄 Rollback Procedure

If new model performs poorly:

1. **Check manifest**
   ```bash
   cat models/manifest.json
   ```

2. **Find previous version**
   ```json
   {
     "version": "v20241119T103045Z",
     "model": "models/credit_risk_model_v20241119T103045Z.pkl",
     ...
   }
   ```

3. **Copy old model to current**
   ```bash
   cp models/credit_risk_model_v20241119T103045Z.pkl models/credit_risk_model.pkl
   cp models/scaler_v20241119T103045Z.pkl models/scaler.pkl
   cp models/feature_names_v20241119T103045Z.json models/feature_names.json
   ```

4. **Reload model**
   - Click "Reload Model" in admin panel
   - Or restart API

---

## 📚 Related Documentation

- **Import Script:** `IMPORT_AND_RETRAIN_GUIDE.md`
- **Database:** `CHECK_DATABASE.md`
- **API Reference:** `API_QUICK_REFERENCE.md`
- **Architecture:** `SIMPLIFIED_ARCHITECTURE.md`

---

## 🎯 Quick Reference

| Task | Steps |
|------|-------|
| Import CSV | Admin → Import Data → Upload → Import |
| Check Status | Admin → Status → View stats |
| Retrain Model | Admin → Retrain → Start Retraining |
| Reload Model | After retrain → Reload Model button |
| View Results | Retrain tab → See metrics |

---

## 🎉 Success Checklist

After using admin panel:

- [ ] CSV data imported successfully
- [ ] Database shows new predictions
- [ ] Retraining status shows "Ready"
- [ ] Model retrained with good metrics
- [ ] Model reloaded in API
- [ ] Test predictions work correctly
- [ ] Performance improved

---

**The Admin Panel makes it easy to continuously improve your model!** 🚀

No command line needed - everything in the browser! 🎨

# CSV Upload Feature Guide

## Overview

The frontend now supports **CSV file upload** with automatic field detection and mapping. Upload a CSV file with loan application data, and the system will:

1. **Auto-detect columns** and map them to the correct fields
2. **Generate a dynamic form** based on detected fields
3. **Navigate through rows** one at a time
4. **Batch process** all rows at once
5. **Download results** as a CSV file

## Quick Start

### 1. Switch to CSV Mode

Click the **📊 CSV Upload** button at the top of the page.

### 2. Upload Your CSV

Drag and drop a CSV file or click to browse. The system will:
- Parse the CSV
- Show a preview of the first 3 rows
- Detect and map columns automatically

### 3. Review Field Mappings

The system automatically maps CSV columns to form fields:
- `age` → Person Age
- `income` → Annual Income
- `loan_amount` → Loan Amount
- etc.

### 4. Process Data

**Single Row:**
- Navigate through rows using Previous/Next buttons
- Edit values if needed
- Click "Predict This Row" to get a prediction

**Batch Processing:**
- Click "Process All Rows" to predict all rows at once
- Download results as CSV when complete

## CSV Format

### Required Columns

Your CSV should include some or all of these columns (any subset works thanks to dynamic input):

```csv
person_age,person_income,person_emp_length,loan_amnt,loan_int_rate,loan_percent_income,cb_person_cred_hist_length,home_ownership,loan_intent,loan_grade,default_on_file
30,50000,24,10000,10.0,0.20,5,RENT,PERSONAL,B,N
```

### Column Name Variations

The system recognizes common variations:

| Standard Field | Recognized Variations |
|----------------|----------------------|
| `person_age` | age |
| `person_income` | income, annual_income |
| `person_emp_length` | employment_length, emp_length |
| `loan_amnt` | loan_amount, amount |
| `loan_int_rate` | interest_rate, rate |
| `cb_person_cred_hist_length` | credit_history, credit_hist_length |
| `home_ownership` | home, ownership |
| `loan_intent` | intent, purpose |
| `loan_grade` | grade |
| `default_on_file` | default |

### Sample CSV

A sample CSV file is included at `frontend/public/sample_data.csv`:

```csv
person_age,person_income,person_emp_length,loan_amnt,loan_int_rate,loan_percent_income,cb_person_cred_hist_length,home_ownership,loan_intent,loan_grade,default_on_file
30,50000,24,10000,10.0,0.20,5,RENT,PERSONAL,B,N
45,75000,60,20000,8.5,0.27,10,OWN,HOMEIMPROVEMENT,A,N
25,35000,12,15000,15.0,0.43,3,RENT,EDUCATION,C,N
```

## Features

### 1. Automatic Field Detection

The system automatically:
- Detects column names
- Maps to expected fields
- Shows mapping results
- Handles variations in column names

### 2. Row Navigation

Navigate through CSV rows:
- **Previous/Next buttons** - Move between rows
- **Row indicator** - Shows current position (e.g., "Row 3 of 10")
- **Auto-fill form** - Form updates with row data

### 3. Dynamic Form Generation

Form fields are generated based on detected columns:
- **Number inputs** for numeric fields
- **Dropdowns** for categorical fields
- **Validation** based on field type
- **Hints** showing expected format

### 4. Batch Processing

Process all rows at once:
1. Click "Process All Rows"
2. System processes each row sequentially
3. Shows progress indicator
4. Displays summary when complete

### 5. Results Download

After batch processing:
- View summary statistics (Total, Success, Errors)
- Download results as CSV
- Includes all predictions and input data

## Use Cases

### Use Case 1: Loan Application Review

Upload a CSV of pending applications and review predictions one by one:

```csv
applicant_id,age,income,loan_amount,grade
APP001,30,50000,10000,B
APP002,45,75000,20000,A
```

### Use Case 2: Bulk Risk Assessment

Process hundreds of applications at once:

1. Upload CSV with all applications
2. Click "Process All Rows"
3. Download results CSV
4. Import into your system

### Use Case 3: Data Quality Check

Test with partial data to see imputation:

```csv
income,loan_amount
50000,10000
75000,20000
```

Missing fields are automatically filled using smart defaults.

### Use Case 4: Historical Data Analysis

Upload historical loan data to see how the model would have predicted:

```csv
date,age,income,loan_amount,actual_default
2023-01-15,30,50000,10000,N
2023-02-20,25,35000,15000,Y
```

## API Integration

The CSV feature uses the **dynamic prediction endpoint**:

```
POST http://localhost:8000/predict_risk_dynamic
```

This endpoint:
- Accepts partial data
- Automatically imputes missing fields
- Returns detailed predictions with imputation logs

## Tips & Best Practices

### Data Preparation

1. **Clean your data** - Remove empty rows and invalid values
2. **Use standard column names** - Or close variations
3. **Include critical fields** - At minimum: income and loan_amount
4. **Check data types** - Numbers should be numeric, not text

### Performance

- **Small files** (<100 rows): Use batch processing
- **Large files** (>100 rows): Process in chunks or use API directly
- **Very large files** (>1000 rows): Consider backend batch processing

### Validation

- Review field mappings before processing
- Check first few rows manually
- Verify batch results summary
- Download and review full results

## Troubleshooting

### Issue: No fields detected

**Solution:** Check your CSV format
- Ensure first row contains column headers
- Use standard column names or variations
- Check for special characters in column names

### Issue: Wrong field mapping

**Solution:** Rename columns in your CSV
- Use exact field names from the standard list
- Or use recognized variations
- Avoid abbreviations that aren't recognized

### Issue: Batch processing fails

**Solution:** Check individual rows
- Process rows one by one to find problematic data
- Check for invalid values (negative numbers, out of range)
- Ensure categorical fields use valid options

### Issue: Download not working

**Solution:** Check browser settings
- Allow downloads from localhost
- Check browser console for errors
- Try a different browser

## Technical Details

### Libraries Used

- **PapaParse** - CSV parsing
- **Framer Motion** - Animations
- **Axios** - API requests

### Components

- `CSVUploader.jsx` - File upload and preview
- `DynamicForm.jsx` - Dynamic form generation and batch processing
- `App.jsx` - Mode switching and state management

### Data Flow

```
CSV File
  ↓
PapaParse (parse)
  ↓
Column Detection & Mapping
  ↓
Dynamic Form Generation
  ↓
API Request (dynamic endpoint)
  ↓
Results Display
```

## Future Enhancements

Potential improvements:

1. **Column mapping editor** - Manually adjust mappings
2. **Data validation** - Pre-validate before processing
3. **Progress bar** - Show detailed progress during batch
4. **Error recovery** - Retry failed rows
5. **Export templates** - Download CSV template
6. **Save mappings** - Remember column mappings
7. **Drag-and-drop reordering** - Reorder columns visually

## Support

For issues or questions:
1. Check this guide
2. Review sample CSV format
3. Test with provided sample file
4. Check browser console for errors
5. Verify API is running: `http://localhost:8000/health`

---

**Ready to try it?** Upload the sample CSV file (`frontend/public/sample_data.csv`) to see it in action!

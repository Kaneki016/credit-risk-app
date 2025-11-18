# CSV Upload UI - User Guide

## Overview

The CSV upload interface is designed to handle any number of columns efficiently with a clean, organized layout.

## Interface Layout

### 1. Header Section

**CSV Data Loaded**
- Shows number of fields mapped
- Toggle button to show/hide field mappings
- Collapsible by default to save space

**Field Mappings (Collapsible)**
- Click "▶ Field Mappings" to expand
- Shows CSV column → Form field mapping
- Compact grid layout
- Scrollable if many fields

### 2. Row Navigation

**Controls:**
- **← Previous** - Go to previous row
- **Row X of Y** - Current position indicator
- **Next →** - Go to next row

**Features:**
- Buttons disabled at boundaries
- Auto-loads row data into form
- Smooth transitions

### 3. Tab Navigation

**📝 Edit Data Tab**
- Form for editing current row
- Organized into categories
- Compact layout

**🚀 Batch Process Tab**
- Dedicated batch processing view
- Shows statistics
- Large action button

### 4. Form Categories (Edit Data Tab)

**👤 Personal Information**
- Person Age
- Annual Income
- Employment Length
- Credit History

**💰 Loan Details**
- Loan Amount
- Interest Rate
- Loan % of Income
- Loan Grade
- Loan Intent

**📋 Additional Info**
- Home Ownership
- Previous Default

### 5. Batch Processing (Batch Tab)

**Information Display:**
- Total rows to process
- Number of fields mapped
- Clear description

**Action Button:**
- Large, prominent button
- Shows progress during processing
- Disabled while processing

### 6. Results Display

**After Prediction:**
- Risk level and probability
- SHAP explanations
- Imputation logs

**After Batch Processing:**
- Summary statistics
- Success/error counts
- Download button for CSV

## How to Use

### Single Row Prediction

1. **Upload CSV** - Drag and drop your file
2. **Review Mappings** - Click "▶ Field Mappings" to verify
3. **Navigate** - Use Previous/Next to find your row
4. **Edit** - Modify values if needed (in Edit Data tab)
5. **Predict** - Click "✨ Predict This Row"
6. **Review** - See results in right panel

### Batch Processing

1. **Upload CSV** - Drag and drop your file
2. **Switch Tab** - Click "🚀 Batch Process"
3. **Review Stats** - Check total rows and fields
4. **Process** - Click "🚀 Start Batch Processing"
5. **Wait** - Progress shown during processing
6. **Download** - Click "📥 Download CSV" when complete

## Tips & Tricks

### Organizing Your View

**Hide Mappings:**
- Click "▼ Field Mappings" to collapse
- Saves screen space
- Mappings remembered

**Use Tabs:**
- Switch to Batch tab if not editing
- Cleaner view for batch operations
- Less clutter

### Efficient Navigation

**Keyboard Shortcuts:**
- Tab - Move between fields
- Enter - Submit form
- Arrow keys - Adjust number values

**Quick Review:**
- Use Previous/Next to scan data
- Edit only what needs changing
- Skip to specific rows

### Batch Processing

**Best Practices:**
- Review first few rows manually
- Check field mappings before batch
- Download results immediately
- Keep original CSV as backup

**Performance:**
- Small files (<50 rows): Very fast
- Medium files (50-200 rows): 1-2 minutes
- Large files (>200 rows): Consider chunking

## Visual Indicators

### Colors

**Green (Success):**
- ✓ Mapped fields badge
- Success statistics
- Low risk results

**Blue (Info):**
- Active tab
- Primary buttons
- Links and accents

**Orange (Warning):**
- ⚠ No fields detected
- Borderline risk

**Red (Error):**
- Error statistics
- High risk results
- Failed predictions

### Icons

- 📊 CSV Upload mode
- ✍️ Manual Entry mode
- 👤 Personal information
- 💰 Loan details
- 📋 Additional info
- ✨ Predict action
- 🚀 Batch process
- 📥 Download results
- ▶/▼ Expand/collapse

## Responsive Design

### Desktop (>768px)
- Multi-column grid (3+ columns)
- Side-by-side tabs
- Compact spacing

### Tablet (768px)
- 2-column grid
- Flexible tabs
- Medium spacing

### Mobile (<768px)
- Single column
- Stacked layout
- Full-width buttons
- Touch-friendly spacing

## Troubleshooting

### Issue: Too many fields, can't see form

**Solution:**
- Collapse field mappings (click toggle)
- Use categories to organize
- Scroll within each category

### Issue: Can't find specific field

**Solution:**
- Check field mappings section
- Look in appropriate category
- Use browser search (Ctrl+F)

### Issue: Form feels cramped

**Solution:**
- Zoom out browser (Ctrl + -)
- Use full screen mode (F11)
- Hide unnecessary browser toolbars

### Issue: Batch processing slow

**Solution:**
- Normal for large files
- Check progress indicator
- Consider processing in chunks
- Use API directly for very large files

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Tab | Next field |
| Shift+Tab | Previous field |
| Enter | Submit form |
| Arrow Up/Down | Adjust numbers |
| Shift+Arrow | Adjust by 10 |
| Esc | Close modals |

## Accessibility

**Screen Readers:**
- All fields properly labeled
- Status announcements
- Error messages read aloud

**Keyboard Navigation:**
- Full keyboard support
- Visible focus indicators
- Logical tab order

**Visual:**
- High contrast mode supported
- Scalable text
- Clear visual hierarchy

## Best Practices

### Data Preparation

1. **Clean your CSV** - Remove empty rows
2. **Use standard names** - Or close variations
3. **Check data types** - Numbers as numbers
4. **Include headers** - First row must be column names

### Workflow

1. **Start small** - Test with 1-2 rows first
2. **Verify mappings** - Check field detection
3. **Edit carefully** - Review before predicting
4. **Save results** - Download batch results
5. **Keep originals** - Don't overwrite source data

### Performance

1. **Close other tabs** - Free up memory
2. **Use modern browser** - Chrome, Firefox, Edge
3. **Stable connection** - For API calls
4. **Batch wisely** - Chunk large files

## Support

**Need Help?**
1. Check this guide
2. Review field mappings
3. Try sample CSV first
4. Check browser console for errors
5. Verify API is running

**Common Issues:**
- Field not detected → Use standard column names
- Slow processing → Normal for large files
- Form cluttered → Collapse mappings, use tabs
- Can't find field → Check category sections

---

**Enjoy the clean, organized interface!** 🎉

import React, { useState, useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'

import { ENDPOINTS } from '../../utils/api'
import { loanApplicationSchema } from '../../schemas/loanApplicationSchema'

// Use dynamic endpoint
const API_DYNAMIC = ENDPOINTS.PREDICT_DYNAMIC

// Field metadata for smart form generation
const FIELD_METADATA = {
  person_age: { type: 'number', label: 'Age', min: 18, max: 120, hint: 'Years' },
  person_income: { type: 'number', label: 'Annual Income', min: 0, hint: 'USD' },
  person_emp_length: { type: 'number', label: 'Employment Length', min: 0, hint: 'Months' },
  loan_amnt: { type: 'number', label: 'Loan Amount', min: 0, hint: 'USD' },
  loan_int_rate: { type: 'number', label: 'Interest Rate', min: 0, max: 100, hint: '%', step: 0.1 },
  loan_percent_income: { type: 'number', label: 'Loan % of Income', min: 0, max: 1, hint: '0-1', step: 0.01 },
  cb_person_cred_hist_length: { type: 'number', label: 'Credit History', min: 0, hint: 'Years' },
  home_ownership: {
    type: 'select',
    label: 'Home Ownership',
    options: ['RENT', 'OWN', 'MORTGAGE', 'OTHER']
  },
  loan_intent: {
    type: 'select',
    label: 'Loan Purpose',
    options: ['PERSONAL', 'EDUCATION', 'MEDICAL', 'VENTURE', 'HOMEIMPROVEMENT', 'DEBTCONSOLIDATION']
  },
  loan_grade: {
    type: 'select',
    label: 'Loan Grade',
    options: ['A', 'B', 'C', 'D', 'E', 'F', 'G']
  },
  default_on_file: {
    type: 'select',
    label: 'Previous Default',
    options: ['N', 'Y']
  }
}

// Map common CSV column names to our expected fields
const COLUMN_MAPPINGS = {
  'age': 'person_age',
  'income': 'person_income',
  'annual_income': 'person_income',
  'employment_length': 'person_emp_length',
  'emp_length': 'person_emp_length',
  'loan_amount': 'loan_amnt',
  'amount': 'loan_amnt',
  'interest_rate': 'loan_int_rate',
  'rate': 'loan_int_rate',
  'credit_history': 'cb_person_cred_hist_length',
  'credit_hist_length': 'cb_person_cred_hist_length',
  'home': 'home_ownership',
  'ownership': 'home_ownership',
  'intent': 'loan_intent',
  'purpose': 'loan_intent',
  'grade': 'loan_grade',
  'default': 'default_on_file'
}

export default function DynamicForm({ csvData, onResult, onLoading, onError }) {
  const [detectedFields, setDetectedFields] = useState([])
  const [currentRowIndex, setCurrentRowIndex] = useState(0)
  const [batchMode, setBatchMode] = useState(false)
  const [batchResults, setBatchResults] = useState([])
  const [processingBatch, setProcessingBatch] = useState(false)
  const [showMappings, setShowMappings] = useState(false)
  const [activeTab, setActiveTab] = useState('form')

  // Setup React Hook Form
  const {
    control,
    handleSubmit,
    reset,
    setValue,
    formState: { errors }
  } = useForm({
    resolver: zodResolver(loanApplicationSchema),
    defaultValues: {}
  })

  // React Query Mutation
  const mutation = useMutation({
    mutationFn: (data) => axios.post(API_DYNAMIC, data, { timeout: 30000 }),
    onMutate: () => {
      onLoading && onLoading()
    },
    onSuccess: (response) => {
      onResult && onResult(response.data)
    },
    onError: (err) => {
      console.error(err)
      const msg = err.response?.data?.detail || err.message || 'Request failed'
      onError && onError(String(msg))
    }
  })

  // Detect and map CSV columns to form fields
  useEffect(() => {
    if (!csvData) {
      setDetectedFields([])
      reset({})
      return
    }

    const { columns, data } = csvData
    const mapped = []
    const unmapped = []

    // Try to map each column
    columns.forEach(col => {
      const normalized = col.toLowerCase().replace(/[_\s-]/g, '')
      let mappedField = null

      // Direct match
      if (FIELD_METADATA[col]) {
        mappedField = col
      }
      // Try normalized match
      else if (FIELD_METADATA[normalized]) {
        mappedField = normalized
      }
      // Try common mappings
      else {
        for (const [pattern, field] of Object.entries(COLUMN_MAPPINGS)) {
          if (normalized.includes(pattern.replace(/_/g, ''))) {
            mappedField = field
            break
          }
        }
      }

      if (mappedField) {
        mapped.push({ csvColumn: col, formField: mappedField })
      } else {
        unmapped.push(col)
      }
    })

    setDetectedFields(mapped)

    // Load first row data
    if (data.length > 0) {
      loadRowData(0, mapped, data)
    }
  }, [csvData, reset])

  const loadRowData = (index, fields, data) => {
    const row = data[index]
    const newFormData = {}

    fields.forEach(({ csvColumn, formField }) => {
      const value = row[csvColumn]
      if (value !== null && value !== undefined && value !== '') {
        // Convert types if necessary
        const meta = FIELD_METADATA[formField]
        if (meta.type === 'number') {
          newFormData[formField] = parseFloat(value) || 0
        } else {
          newFormData[formField] = value
        }
      }
    })

    reset(newFormData)
    setCurrentRowIndex(index)
  }

  const onSubmit = (data) => {
    mutation.mutate(data)
  }

  const handleNextRow = () => {
    if (currentRowIndex < csvData.data.length - 1) {
      loadRowData(currentRowIndex + 1, detectedFields, csvData.data)
    }
  }

  const handlePrevRow = () => {
    if (currentRowIndex > 0) {
      loadRowData(currentRowIndex - 1, detectedFields, csvData.data)
    }
  }

  const handleBatchProcess = async () => {
    if (!csvData || csvData.data.length === 0) return

    setProcessingBatch(true)
    setBatchMode(true)
    const results = []

    for (let i = 0; i < csvData.data.length; i++) {
      const row = csvData.data[i]
      const rowData = {}

      detectedFields.forEach(({ csvColumn, formField }) => {
        const value = row[csvColumn]
        if (value !== null && value !== undefined && value !== '') {
          const meta = FIELD_METADATA[formField]
          if (meta.type === 'number') {
            rowData[formField] = parseFloat(value) || 0
          } else {
            rowData[formField] = value
          }
        }
      })

      try {
        const response = await axios.post(API_DYNAMIC, rowData, { timeout: 30000 })
        results.push({
          rowIndex: i,
          input: rowData,
          result: response.data,
          status: 'success'
        })
      } catch (err) {
        results.push({
          rowIndex: i,
          input: rowData,
          error: err.message,
          status: 'error'
        })
      }

      // Update progress
      setCurrentRowIndex(i)
    }

    setBatchResults(results)
    setProcessingBatch(false)
    onResult && onResult({ batchResults: results })
  }

  const downloadBatchResults = () => {
    const csv = [
      // Header
      ['Row', 'Risk Level', 'Probability %', 'Prediction', 'Status'].join(','),
      // Data
      ...batchResults.map(r => [
        r.rowIndex + 1,
        r.result?.risk_level || 'N/A',
        r.result?.probability_default_percent || 'N/A',
        r.result?.binary_prediction || 'N/A',
        r.status
      ].join(','))
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `predictions_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (!csvData) {
    return (
      <div className="dynamic-form-empty">
        <div className="empty-icon">📋</div>
        <p>Upload a CSV file to get started</p>
      </div>
    )
  }

  // Group fields by category
  const groupedFields = {
    personal: ['person_age', 'person_income', 'person_emp_length', 'cb_person_cred_hist_length'],
    loan: ['loan_amnt', 'loan_int_rate', 'loan_percent_income', 'loan_grade', 'loan_intent'],
    other: ['home_ownership', 'default_on_file']
  }

  const getFieldsByCategory = (category) => {
    return detectedFields.filter(({ formField }) =>
      groupedFields[category].includes(formField)
    )
  }

  return (
    <motion.div
      className="dynamic-form"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="form-header">
        <div className="header-left">
          <h3>CSV Data Loaded</h3>
          <div className="field-mapping-info">
            {detectedFields.length > 0 ? (
              <span className="success-badge">
                ✓ {detectedFields.length} fields mapped
              </span>
            ) : (
              <span className="warning-badge">
                ⚠ No fields detected
              </span>
            )}
          </div>
        </div>
        <button
          type="button"
          className="toggle-mappings"
          onClick={() => setShowMappings(!showMappings)}
        >
          {showMappings ? '▼' : '▶'} Field Mappings
        </button>
      </div>

      <AnimatePresence>
        {showMappings && detectedFields.length > 0 && (
          <motion.div
            className="field-mappings-collapsible"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="field-mappings">
              {detectedFields.map(({ csvColumn, formField }, i) => (
                <div key={i} className="field-mapping">
                  <span className="csv-col">{csvColumn}</span>
                  <span className="arrow">→</span>
                  <span className="form-field">{FIELD_METADATA[formField]?.label || formField}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="row-navigation">
        <button
          type="button"
          onClick={handlePrevRow}
          disabled={currentRowIndex === 0}
          className="nav-button"
        >
          ← Previous
        </button>
        <span className="row-indicator">
          Row {currentRowIndex + 1} of {csvData.data.length}
        </span>
        <button
          type="button"
          onClick={handleNextRow}
          disabled={currentRowIndex === csvData.data.length - 1}
          className="nav-button"
        >
          Next →
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          type="button"
          className={`tab-button ${activeTab === 'form' ? 'active' : ''}`}
          onClick={() => setActiveTab('form')}
        >
          📝 Edit Data
        </button>
        <button
          type="button"
          className={`tab-button ${activeTab === 'batch' ? 'active' : ''}`}
          onClick={() => setActiveTab('batch')}
        >
          🚀 Batch Process
        </button>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'form' && (
          <motion.form
            key="form"
            onSubmit={handleSubmit(onSubmit)}
            className="form"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            {/* Categorized Fields */}
            {getFieldsByCategory('personal').length > 0 && (
              <div className="field-category">
                <h4 className="category-title">👤 Personal Information</h4>
                <div className="form-grid-compact">
                  {getFieldsByCategory('personal').map(({ formField }) => {
                    const meta = FIELD_METADATA[formField]
                    if (!meta) return null

                    return (
                      <label key={formField} className="form-field-compact">
                        <span className="field-label-compact">
                          {meta.label}
                          {meta.hint && <span className="field-hint-compact">{meta.hint}</span>}
                        </span>
                        <Controller
                          name={formField}
                          control={control}
                          render={({ field }) => (
                            <input
                              {...field}
                              type={meta.type}
                              min={meta.min}
                              max={meta.max}
                              step={meta.step}
                              placeholder={meta.label}
                              onChange={(e) => field.onChange(
                                meta.type === 'number' ? parseFloat(e.target.value) : e.target.value
                              )}
                            />
                          )}
                        />
                        {errors[formField] && <span className="error-text">{errors[formField].message}</span>}
                      </label>
                    )
                  })}
                </div>
              </div>
            )}

            {getFieldsByCategory('loan').length > 0 && (
              <div className="field-category">
                <h4 className="category-title">💰 Loan Details</h4>
                <div className="form-grid-compact">
                  {getFieldsByCategory('loan').map(({ formField }) => {
                    const meta = FIELD_METADATA[formField]
                    if (!meta) return null

                    return (
                      <label key={formField} className="form-field-compact">
                        <span className="field-label-compact">
                          {meta.label}
                          {meta.hint && <span className="field-hint-compact">{meta.hint}</span>}
                        </span>
                        <Controller
                          name={formField}
                          control={control}
                          render={({ field }) => (
                            meta.type === 'select' ? (
                              <select {...field}>
                                <option value="">-- Select --</option>
                                {meta.options.map(opt => (
                                  <option key={opt} value={opt}>{opt}</option>
                                ))}
                              </select>
                            ) : (
                              <input
                                {...field}
                                type={meta.type}
                                min={meta.min}
                                max={meta.max}
                                step={meta.step}
                                placeholder={meta.label}
                                onChange={(e) => field.onChange(
                                  meta.type === 'number' ? parseFloat(e.target.value) : e.target.value
                                )}
                              />
                            )
                          )}
                        />
                        {errors[formField] && <span className="error-text">{errors[formField].message}</span>}
                      </label>
                    )
                  })}
                </div>
              </div>
            )}

            {getFieldsByCategory('other').length > 0 && (
              <div className="field-category">
                <h4 className="category-title">📋 Additional Info</h4>
                <div className="form-grid-compact">
                  {getFieldsByCategory('other').map(({ formField }) => {
                    const meta = FIELD_METADATA[formField]
                    if (!meta) return null

                    return (
                      <label key={formField} className="form-field-compact">
                        <span className="field-label-compact">{meta.label}</span>
                        <Controller
                          name={formField}
                          control={control}
                          render={({ field }) => (
                            <select {...field}>
                              <option value="">-- Select --</option>
                              {meta.options.map(opt => (
                                <option key={opt} value={opt}>{opt}</option>
                              ))}
                            </select>
                          )}
                        />
                        {errors[formField] && <span className="error-text">{errors[formField].message}</span>}
                      </label>
                    )
                  })}
                </div>
              </div>
            )}

            <div className="form-actions">
              <button type="submit" className="primary" disabled={mutation.isPending}>
                {mutation.isPending ? '⏳ Predicting...' : '✨ Predict This Row'}
              </button>
            </div>
          </motion.form>
        )}

        {activeTab === 'batch' && (
          <motion.div
            key="batch"
            className="batch-tab"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <div className="batch-info">
              <div className="batch-icon">🚀</div>
              <h4>Batch Process All Rows</h4>
              <p>Process all {csvData.data.length} rows at once and download results as CSV.</p>

              <div className="batch-stats-preview">
                <div className="stat-preview">
                  <span className="stat-number">{csvData.data.length}</span>
                  <span className="stat-label">Total Rows</span>
                </div>
                <div className="stat-preview">
                  <span className="stat-number">{detectedFields.length}</span>
                  <span className="stat-label">Fields Mapped</span>
                </div>
              </div>

              <button
                type="button"
                onClick={handleBatchProcess}
                disabled={processingBatch}
                className="batch-process-button"
              >
                {processingBatch ? (
                  <>
                    <span className="spinner"></span>
                    Processing Row {currentRowIndex + 1} of {csvData.data.length}...
                  </>
                ) : (
                  <>🚀 Start Batch Processing</>
                )}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {batchMode && batchResults.length > 0 && (
        <motion.div
          className="batch-results"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="batch-header">
            <h4>Batch Results</h4>
            <button onClick={downloadBatchResults} className="download-button">
              📥 Download CSV
            </button>
          </div>
          <div className="batch-summary">
            <div className="summary-stat">
              <span className="stat-label">Total:</span>
              <span className="stat-value">{batchResults.length}</span>
            </div>
            <div className="summary-stat success">
              <span className="stat-label">Success:</span>
              <span className="stat-value">
                {batchResults.filter(r => r.status === 'success').length}
              </span>
            </div>
            <div className="summary-stat error">
              <span className="stat-label">Errors:</span>
              <span className="stat-value">
                {batchResults.filter(r => r.status === 'error').length}
              </span>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

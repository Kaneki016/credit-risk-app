import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ENDPOINTS } from '../../utils/api'

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState('import')
  const [file, setFile] = useState(null)
  const [importing, setImporting] = useState(false)
  const [retraining, setRetraining] = useState(false)
  const [clearing, setClearing] = useState(false)
  const [importResult, setImportResult] = useState(null)
  const [retrainResult, setRetrainResult] = useState(null)
  const [clearResult, setClearResult] = useState(null)
  const [error, setError] = useState(null)
  const [showClearConfirm, setShowClearConfirm] = useState(false)
  const [dropTables, setDropTables] = useState(false)
  const [retrainStatus, setRetrainStatus] = useState(false)
  const [modelState, setModelState] = useState(null)
  const [apiStatus, setApiStatus] = useState(null)
  const [loadingModelState, setLoadingModelState] = useState(false)
  const [loadingApiStatus, setLoadingApiStatus] = useState(false)

  // Mapping State
  const [dbColumns, setDbColumns] = useState([])
  const [csvColumns, setCsvColumns] = useState([])
  const [columnMapping, setColumnMapping] = useState({})
  const [showMapping, setShowMapping] = useState(false)

  // Check retraining status
  const checkRetrainStatus = async () => {
    try {
      const response = await fetch(ENDPOINTS.RETRAIN_STATUS)
      if (!response.ok) {
        // If tables don't exist, that's okay - just set status to false
        if (response.status === 500) {
          const errorData = await response.json().catch(() => ({}))
          if (errorData.detail && (errorData.detail.includes('does not exist') || errorData.detail.includes('UndefinedTable'))) {
            setRetrainStatus(false)
            return
          }
        }
        throw new Error(`Status check failed: ${response.statusText}`)
      }
      const data = await response.json()
      setRetrainStatus(data.is_ready || data.retraining || false)
    } catch (err) {
      console.error('Failed to check retrain status:', err)
      // Don't set error state - just silently fail if tables don't exist
      setRetrainStatus(false)
    }
  }

  // Fetch model state
  const fetchModelState = async () => {
    setLoadingModelState(true)
    try {
      const response = await fetch(ENDPOINTS.MODEL_STATE)
      if (response.ok) {
        const data = await response.json()
        setModelState(data)
      } else {
        setModelState({ error: 'Failed to fetch model state' })
      }
    } catch (err) {
      console.error('Failed to fetch model state:', err)
      setModelState({ error: err.message })
    } finally {
      setLoadingModelState(false)
    }
  }

  // Check API status
  const checkApiStatus = async () => {
    setLoadingApiStatus(true)
    try {
      const [apiResponse, modelResponse] = await Promise.all([
        fetch(ENDPOINTS.API_HEALTH),
        fetch(ENDPOINTS.MODEL_HEALTH)
      ])
      
      const apiData = apiResponse.ok ? await apiResponse.json() : { status: 'error' }
      const modelData = modelResponse.ok ? await modelResponse.json() : { status: 'error' }
      
      setApiStatus({
        api: apiData,
        model: modelData,
        timestamp: new Date().toISOString()
      })
    } catch (err) {
      console.error('Failed to check API status:', err)
      setApiStatus({ error: err.message })
    } finally {
      setLoadingApiStatus(false)
    }
  }

  // Handle file selection
  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please select a CSV file')
        return
      }
      setFile(selectedFile)
      setError(null)
      setImportResult(null)
      setShowMapping(false)
      setColumnMapping({})

      // 1. Fetch DB Schema
      try {
        const schemaRes = await fetch(`${ENDPOINTS.GET_SCHEMA}/loan_applications`)
        if (schemaRes.ok) {
          const data = await schemaRes.json()
          setDbColumns(data.columns)
        }
      } catch (err) {
        console.error("Failed to fetch schema:", err)
      }

      // 2. Parse CSV Headers
      const reader = new FileReader()
      reader.onload = (event) => {
        const text = event.target.result
        const firstLine = text.split('\n')[0]
        const headers = firstLine.split(',').map(h => h.trim())
        setCsvColumns(headers)

        // Auto-map
        const initialMapping = {}
        headers.forEach(header => {
          // Simple fuzzy match
          const normalizedHeader = header.toLowerCase().replace(/_/g, '').replace(/ /g, '')
          const match = dbColumns.find(dbCol => {
            const normalizedDb = dbCol.toLowerCase().replace(/_/g, '')
            return normalizedDb === normalizedHeader || normalizedDb.includes(normalizedHeader) || normalizedHeader.includes(normalizedDb)
          })
          if (match) {
            initialMapping[header] = match
          }
        })
        setColumnMapping(initialMapping)
        setShowMapping(true)
      }
      reader.readAsText(selectedFile)
    }
  }

  // Import CSV data
  const handleImport = async () => {
    console.log('handleImport called. File:', file, 'Importing:', importing)
    if (!file) {
      setError('Please select a file first')
      return
    }
    if (importing) return

    setImporting(true)
    setError(null)
    setImportResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      if (Object.keys(columnMapping).length > 0) {
        formData.append('column_mapping', JSON.stringify(columnMapping))
      }

      const response = await fetch(`${ENDPOINTS.IMPORT_CSV}`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Import failed: ${response.statusText} - ${errorText}`)
      }

      const result = await response.json()
      console.log('Import result:', result)
      setImportResult(result)

      // Check retrain status after import
      await checkRetrainStatus()
    } catch (err) {
      console.error('Import error:', err)
      setError(err.message)
      setImportResult({
        status: 'error',
        message: err.message
      })
    } finally {
      // Always reset importing state, even if there was an error
      setImporting(false)
      console.log('Import complete, importing state reset to false')
    }
  }

  // Trigger retraining
  const handleRetrain = async () => {
    setRetraining(true)
    setError(null)
    setRetrainResult(null)

    try {
      const response = await fetch(ENDPOINTS.RETRAIN, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error(`Retraining failed: ${response.statusText}`)
      }

      const result = await response.json()
      setRetrainResult(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setRetraining(false)
    }
  }

  // Reload model
  const handleReloadModel = async () => {
    try {
      const response = await fetch(ENDPOINTS.RELOAD_MODEL, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error(`Model reload failed: ${response.statusText}`)
      }

      const result = await response.json()
      alert('Model reloaded successfully!')
    } catch (err) {
      setError(err.message)
    }
  }

  // Clear database
  const handleClearDatabase = async () => {
    setClearing(true)
    setError(null)
    setClearResult(null)

    try {
      const response = await fetch(`${ENDPOINTS.CLEAR_DB}?confirm=true&drop_tables=${dropTables}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error(`Clear database failed: ${response.statusText}`)
      }

      const result = await response.json()
      setClearResult(result)
      setShowClearConfirm(false)

      // Don't check retrain status after dropping tables (tables don't exist yet)
      // Only check if we didn't drop tables
      if (!dropTables) {
      await checkRetrainStatus()
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setClearing(false)
    }
  }

  // Load retrain status on mount
  React.useEffect(() => {
    checkRetrainStatus()
    fetchModelState()
    checkApiStatus()
  }, [])

  // Ensure importing state resets when import completes
  React.useEffect(() => {
    if (importResult && importing) {
      console.log('Import result received, resetting importing state')
      setImporting(false)
    }
  }, [importResult, importing])

  // Refresh model state when retrain tab is active
  React.useEffect(() => {
    if (activeTab === 'retrain') {
      fetchModelState()
    }
  }, [activeTab])

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h2>🔧 Admin Panel</h2>
        <p>Manage data, retrain models, and monitor system status</p>
      </div>

      {/* Tabs */}
      <div className="admin-tabs">
        <button
          className={`tab ${activeTab === 'import' ? 'active' : ''}`}
          onClick={() => setActiveTab('import')}
        >
          📥 Import Data
        </button>
        <button
          className={`tab ${activeTab === 'retrain' ? 'active' : ''}`}
          onClick={() => setActiveTab('retrain')}
        >
          🎯 Train Model
        </button>
        <button
          className={`tab ${activeTab === 'status' ? 'active' : ''}`}
          onClick={() => { 
            setActiveTab('status')
            checkApiStatus()
          }}
        >
          📊 Status
        </button>
        <button
          className={`tab ${activeTab === 'manage' ? 'active' : ''}`}
          onClick={() => setActiveTab('manage')}
        >
          🗑️ Manage
        </button>
      </div>

      {/* Content */}
      <div className="admin-content">
        <AnimatePresence mode="wait">
          {/* Import Tab */}
          {activeTab === 'import' && (
            <motion.div
              key="import"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="admin-section"
            >
              <h3>Import CSV Data & Auto-Train</h3>
              <p className="section-description">
                Upload a CSV file to import historical data. You can map columns to match the database schema.
              </p>

              <div className="file-upload-area">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="file-input"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="file-label">
                  <div className="upload-icon">📁</div>
                  <span className="upload-text">{file ? file.name : 'Choose CSV File'}</span>
                  <span className="upload-hint">Drag & drop or click to browse</span>
                </label>
              </div>



              {/* Mapping UI */}
              {showMapping && (
                <motion.div
                  className="mapping-section"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                >
                  <h4>Map Columns</h4>
                  <p className="text-small" style={{ color: '#718096', marginBottom: '1rem' }}>
                    Map your CSV columns to the database schema.
                  </p>
                  <div className="mapping-grid">
                    {csvColumns.map(col => (
                      <React.Fragment key={col}>
                        <span className="csv-col" style={{ textAlign: 'right' }}>{col}</span>
                        <span className="arrow">→</span>
                        <select
                          value={columnMapping[col] || ''}
                          onChange={(e) => setColumnMapping({ ...columnMapping, [col]: e.target.value })}
                        >
                          <option value="">-- Skip --</option>
                          {dbColumns.map(dbCol => (
                            <option key={dbCol} value={dbCol}>{dbCol}</option>
                          ))}
                        </select>
                      </React.Fragment>
                    ))}
                  </div>
                </motion.div>
              )}



              <button
                className="btn-primary"
                onClick={handleImport}
                disabled={!file || importing}
                style={{
                  marginTop: '1.5rem',
                  width: '100%',
                  opacity: (!file || importing) ? 0.5 : 1,
                  cursor: (!file || importing) ? 'not-allowed' : 'pointer'
                }}
              >
                {importing ? '⏳ Importing...' : '🚀 Import & Retrain'}
              </button>

              {importResult && (
                <div className={`result-box ${importResult.status === 'success' ? 'success' : 'error'}`}>
                  <h4>{importResult.status === 'success' ? '✅ Success' : '❌ Failed'}</h4>
                  <p>{importResult.message}</p>
                  {importResult.imported > 0 && (
                    <p className="small" style={{ marginTop: '0.5rem', fontWeight: 600 }}>
                      Imported {importResult.imported} of {importResult.total_rows} rows
                    </p>
                  )}
                </div>
              )}
            </motion.div>
          )}

          {/* Retrain Tab */}
          {activeTab === 'retrain' && (
            <motion.div
              key="retrain"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="admin-section"
            >
              <h3>Manual Model Retraining</h3>
              <p className="section-description">
                Manually trigger a retraining session using the current data in the database.
              </p>

              {/* Model State Display */}
              <div className="model-state-section" style={{ marginBottom: '2rem', padding: '1.5rem', background: '#f7fafc', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h4 style={{ margin: 0, color: '#2d3748' }}>📊 Model State</h4>
                  <button 
                    onClick={fetchModelState} 
                    disabled={loadingModelState}
                    className="btn-secondary"
                    style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                  >
                    {loadingModelState ? '⏳ Loading...' : '🔄 Refresh'}
                  </button>
                </div>
                
                {modelState && !modelState.error ? (
                  <div className="model-state-details">
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
                      <div className="state-item">
                        <span className="state-label">Predictor:</span>
                        <span className={`state-value ${modelState.predictor_loaded ? 'success' : 'error'}`}>
                          {modelState.predictor_loaded ? '✅ Loaded' : '❌ Not Loaded'}
                        </span>
                      </div>
                      <div className="state-item">
                        <span className="state-label">Dynamic Predictor:</span>
                        <span className={`state-value ${modelState.dynamic_predictor_loaded ? 'success' : 'error'}`}>
                          {modelState.dynamic_predictor_loaded ? '✅ Loaded' : '❌ Not Loaded'}
                        </span>
                      </div>
                    </div>
                    
                    {modelState.predictor_info && (
                      <div style={{ marginTop: '1rem', padding: '1rem', background: '#fff', borderRadius: '0.375rem' }}>
                        <h5 style={{ margin: '0 0 0.75rem 0', fontSize: '0.875rem', fontWeight: 600 }}>Predictor Details:</h5>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.75rem', fontSize: '0.875rem' }}>
                          <div>
                            <span style={{ color: '#718096' }}>Model:</span>
                            <span style={{ marginLeft: '0.5rem', fontWeight: 600 }}>
                              {modelState.predictor_info.has_model ? '✅' : '❌'}
                            </span>
                          </div>
                          <div>
                            <span style={{ color: '#718096' }}>Scaler:</span>
                            <span style={{ marginLeft: '0.5rem', fontWeight: 600 }}>
                              {modelState.predictor_info.has_scaler ? '✅' : '❌'}
                            </span>
                          </div>
                          <div>
                            <span style={{ color: '#718096' }}>Features:</span>
                            <span style={{ marginLeft: '0.5rem', fontWeight: 600 }}>
                              {modelState.predictor_info.feature_count || 0}
                            </span>
                          </div>
                        </div>
                        {modelState.predictor_info.load_error && (
                          <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: '#fed7d7', borderRadius: '0.375rem', fontSize: '0.875rem', color: '#c53030' }}>
                            ⚠️ Error: {modelState.predictor_info.load_error}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {modelState.manifest && (
                      <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#e6fffa', borderRadius: '0.375rem', fontSize: '0.875rem' }}>
                        <strong>Latest Model:</strong>{' '}
                        {modelState.manifest.timestamp || modelState.manifest.version || 'Unknown date'}
                      </div>
                    )}
                  </div>
                ) : modelState?.error ? (
                  <div style={{ padding: '1rem', background: '#fed7d7', borderRadius: '0.375rem', color: '#c53030' }}>
                    ❌ {modelState.error}
                  </div>
                ) : (
                  <div style={{ padding: '1rem', textAlign: 'center', color: '#718096' }}>
                    Click Refresh to load model state
                  </div>
                )}
              </div>

              <button
                className="btn-primary"
                onClick={handleRetrain}
                disabled={retraining}
              >
                {retraining ? '⏳ Retraining...' : '🔄 Start Retraining'}
              </button>

              {retrainResult && (
                <div className="result-box success">
                  <h4>✅ Retraining Complete</h4>
                  <p>{retrainResult.message}</p>
                  {retrainResult.metrics && (
                    <div className="result-stats">
                      <div className="stat">
                        <span className="stat-label">Accuracy</span>
                        <span className="stat-value">{(retrainResult.metrics.accuracy * 100).toFixed(1)}%</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">F1 Score</span>
                        <span className="stat-value">{(retrainResult.metrics.f1_score * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          )}

          {/* Status Tab */}
          {activeTab === 'status' && (
            <motion.div
              key="status"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="admin-section"
            >
              <h3>System Status</h3>
              <p className="section-description">Check the current status of the retraining system and API.</p>

              {/* API Status */}
              <div className="status-card" style={{ background: '#f7fafc', border: '1px solid #e2e8f0' }}>
                <div style={{ marginBottom: '1rem' }}>
                  <h4 style={{ margin: 0 }}>🌐 System API Status</h4>
                </div>
                
                {apiStatus && !apiStatus.error ? (
                  <div className="api-status-details">
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
                      <div className="status-item">
                        <span className="status-label">API Server:</span>
                        <span className={`status-value ${apiStatus.api?.status === 'ok' ? 'success' : 'error'}`}>
                          {apiStatus.api?.status === 'ok' ? '✅ Online' : '❌ Offline'}
                        </span>
                      </div>
                      <div className="status-item">
                        <span className="status-label">Model Service:</span>
                        <span className={`status-value ${apiStatus.model?.status === 'ok' ? 'success' : 'error'}`}>
                          {apiStatus.model?.status === 'ok' ? '✅ Ready' : '❌ Not Ready'}
                        </span>
                      </div>
                    </div>
                    
                    {apiStatus.api?.status === 'ok' && (
                      <div style={{ padding: '0.75rem', background: '#fff', borderRadius: '0.375rem', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                        <strong>API:</strong> {apiStatus.api.message || 'Running'}
                      </div>
                    )}
                    
                    {apiStatus.model?.status === 'ok' && (
                      <div style={{ padding: '0.75rem', background: '#fff', borderRadius: '0.375rem', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                        <strong>Model:</strong> {apiStatus.model.message || 'Ready'}
                      </div>
                    )}
                    
                    {apiStatus.model?.load_error && (
                      <div style={{ padding: '0.75rem', background: '#fed7d7', borderRadius: '0.375rem', fontSize: '0.875rem', color: '#c53030', marginTop: '0.5rem' }}>
                        ⚠️ Model Error: {apiStatus.model.load_error}
                      </div>
                    )}
                    
                    {apiStatus.timestamp && (
                      <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: '#718096', textAlign: 'right' }}>
                        Last checked: {new Date(apiStatus.timestamp).toLocaleString()}
                      </div>
                    )}
                  </div>
                ) : apiStatus?.error ? (
                  <div style={{ padding: '1rem', background: '#fed7d7', borderRadius: '0.375rem', color: '#c53030' }}>
                    ❌ {apiStatus.error}
                  </div>
                ) : (
                  <div style={{ padding: '1rem', textAlign: 'center', color: '#718096' }}>
                    Click Refresh to check API status
                </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Manage Tab */}
          {activeTab === 'manage' && (
            <motion.div
              key="manage"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="admin-section"
            >
              <h3>🗑️ Database Management</h3>
              <p className="section-description">
                Manage your database and clear all stored data.
              </p>

              <div className="danger-zone">
                <h4>⚠️ Danger Zone</h4>
                <p className="warning-text">
                  <strong>Warning:</strong> Clearing the database will permanently delete ALL data including:
                </p>
                <ul className="warning-list">
                  <li>All predictions</li>
                  <li>All loan applications</li>
                  <li>All feature engineering records</li>
                  <li>All mitigation plans</li>
                  <li>All audit logs</li>
                  <li>All model metrics</li>
                </ul>
                <p className="warning-text">
                  <strong>This action cannot be undone!</strong>
                </p>

                {!showClearConfirm ? (
                  <button
                    className="btn-danger"
                    onClick={() => setShowClearConfirm(true)}
                  >
                    🗑️ Clear Database
                  </button>
                ) : (
                  <div className="confirm-box">
                    <p className="confirm-text">
                      Are you absolutely sure? This will delete all data permanently.
                    </p>

                    <div className="checkbox-group" style={{ margin: '1rem 0', padding: '0.5rem', background: '#fff0f0', borderRadius: '0.5rem', border: '1px solid #feb2b2' }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
                        <input
                          type="checkbox"
                          checked={dropTables}
                          onChange={(e) => setDropTables(e.target.checked)}
                        />
                        <span style={{ fontWeight: 600, color: '#c53030' }}>Also drop tables (Reset Schema)</span>
                      </label>
                      <p style={{ fontSize: '0.85rem', color: '#e53e3e', marginTop: '0.25rem', marginLeft: '2rem' }}>
                        Check this if you want to import a CSV with different columns next.
                      </p>
                    </div>

                    <div className="confirm-buttons">
                      <button
                        className="btn-danger"
                        onClick={handleClearDatabase}
                        disabled={clearing}
                      >
                        {clearing ? '⏳ Clearing...' : '✓ Yes, Clear Everything'}
                      </button>
                      &nbsp;&nbsp;&nbsp;&nbsp;
                      <button
                        className="btn-secondary"
                        onClick={() => setShowClearConfirm(false)}
                        disabled={clearing}
                      >
                        ✗ Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {clearResult && (
                <div className="result-box success">
                  <h4>✅ Database Cleared</h4>
                  {clearResult.total_deleted !== undefined ? (
                  <div className="result-stats">
                    <div className="stat">
                      <span className="stat-label">Total Deleted</span>
                        <span className="stat-value">{clearResult.total_deleted || 0}</span>
                    </div>
                    {clearResult.deleted && (
                      <>
                        <div className="stat">
                          <span className="stat-label">Predictions</span>
                            <span className="stat-value">{clearResult.deleted.predictions || 0}</span>
                        </div>
                        <div className="stat">
                          <span className="stat-label">Applications</span>
                            <span className="stat-value">{clearResult.deleted.loan_applications || 0}</span>
                          </div>
                          <div className="stat">
                            <span className="stat-label">Feature Engineering</span>
                            <span className="stat-value">{clearResult.deleted.feature_engineering || 0}</span>
                          </div>
                          <div className="stat">
                            <span className="stat-label">Mitigation Plans</span>
                            <span className="stat-value">{clearResult.deleted.mitigation_plans || 0}</span>
                          </div>
                          <div className="stat">
                            <span className="stat-label">Audit Logs</span>
                            <span className="stat-value">{clearResult.deleted.audit_logs || 0}</span>
                          </div>
                          <div className="stat">
                            <span className="stat-label">Model Metrics</span>
                            <span className="stat-value">{clearResult.deleted.model_metrics || 0}</span>
                        </div>
                      </>
                    )}
                  </div>
                  ) : (
                    <div className="result-stats">
                      <div className="stat">
                        <span className="stat-label">Action</span>
                        <span className="stat-value">{clearResult.action === 'schema_reset' ? 'Schema Reset' : 'Cleared'}</span>
                      </div>
                    </div>
                  )}
                  <p className="result-message" style={{ textAlign: 'center', marginTop: '1rem' }}>{clearResult.message}</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Display */}
        {error && (
          <motion.div
            className="result-box error"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h4>❌ Error</h4>
            <p>{error}</p>
          </motion.div>
        )}
      </div>
    </div>
  )
}


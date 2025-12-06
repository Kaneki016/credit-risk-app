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

  // Mapping State
  const [dbColumns, setDbColumns] = useState([])
  const [csvColumns, setCsvColumns] = useState([])
  const [columnMapping, setColumnMapping] = useState({})
  const [showMapping, setShowMapping] = useState(false)

  // Check retraining status
  const checkRetrainStatus = async () => {
    try {
      const response = await fetch(ENDPOINTS.RETRAIN_STATUS)
      const data = await response.json()
      setRetrainStatus(data.retraining)
    } catch (err) {
      console.error('Failed to check retrain status:', err)
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
        throw new Error(`Import failed: ${response.statusText}`)
      }

      const result = await response.json()
      setImportResult(result)

      // Check retrain status after import
      await checkRetrainStatus()
    } catch (err) {
      setError(err.message)
    } finally {
      setImporting(false)
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

      // Refresh status
      await checkRetrainStatus()
    } catch (err) {
      setError(err.message)
    } finally {
      setClearing(false)
    }
  }

  // Load retrain status on mount
  React.useEffect(() => {
    checkRetrainStatus()
  }, [])

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
          onClick={() => { setActiveTab('status'); checkRetrainStatus(); }}
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
              <p className="section-description">Check the current status of the retraining system.</p>

              <div className={`status-card ${retrainStatus ? 'ready' : 'not-ready'}`}>
                <div>
                  <h4>{retrainStatus ? '✅ Ready to Train' : '⚠️ Not Ready'}</h4>
                  <p style={{ color: '#4a5568' }}>
                    {retrainStatus
                      ? 'System has sufficient data for retraining.'
                      : 'Not enough data to start retraining.'}
                  </p>
                </div>
                <button onClick={checkRetrainStatus} className="btn-secondary">
                  Refresh Status
                </button>
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
                          style={{ width: '1.2rem', height: '1.2rem', accentColor: '#c53030', cursor: 'pointer' }}
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
                  <div className="result-stats">
                    <div className="stat">
                      <span className="stat-label">Total Deleted</span>
                      <span className="stat-value">{clearResult.total_deleted}</span>
                    </div>
                    {clearResult.deleted && (
                      <>
                        <div className="stat">
                          <span className="stat-label">Predictions</span>
                          <span className="stat-value">{clearResult.deleted.predictions}</span>
                        </div>
                        <div className="stat">
                          <span className="stat-label">Applications</span>
                          <span className="stat-value">{clearResult.deleted.loan_applications}</span>
                        </div>
                      </>
                    )}
                  </div>
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


import React, { useState } from 'react'
import { motion } from 'framer-motion'

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState('import')
  const [file, setFile] = useState(null)
  const [importing, setImporting] = useState(false)
  const [retraining, setRetraining] = useState(false)
  const [flexTraining, setFlexTraining] = useState(false)
  const [clearing, setClearing] = useState(false)
  const [importResult, setImportResult] = useState(null)
  const [retrainResult, setRetrainResult] = useState(null)
  const [flexTrainResult, setFlexTrainResult] = useState(null)
  const [clearResult, setClearResult] = useState(null)
  const [retrainStatus, setRetrainStatus] = useState(null)
  const [error, setError] = useState(null)
  const [showClearConfirm, setShowClearConfirm] = useState(false)

  // Check retraining status
  const checkRetrainStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/db/retraining/status')
      const data = await response.json()
      setRetrainStatus(data.retraining)
    } catch (err) {
      console.error('Failed to check retrain status:', err)
    }
  }

  // Handle file selection
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please select a CSV file')
        return
      }
      setFile(selectedFile)
      setError(null)
      setImportResult(null)
    }
  }

  // Import CSV data
  const handleImport = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setImporting(true)
    setError(null)
    setImportResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/db/import_csv', {
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
      const response = await fetch('http://localhost:8000/db/retrain', {
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
      const response = await fetch('http://localhost:8000/reload_model', {
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

  // Flexible training (train with any CSV structure)
  const handleFlexibleTraining = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setFlexTraining(true)
    setError(null)
    setFlexTrainResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/train/flexible', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error(`Flexible training failed: ${response.statusText}`)
      }

      const result = await response.json()
      setFlexTrainResult(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setFlexTraining(false)
    }
  }

  // Clear database
  const handleClearDatabase = async () => {
    setClearing(true)
    setError(null)
    setClearResult(null)

    try {
      const response = await fetch('http://localhost:8000/db/clear?confirm=true', {
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
        <p>Import data and retrain the model</p>
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
          className={`tab ${activeTab === 'train' ? 'active' : ''}`}
          onClick={() => setActiveTab('train')}
        >
          🎯 Train Model
        </button>
        <button
          className={`tab ${activeTab === 'retrain' ? 'active' : ''}`}
          onClick={() => setActiveTab('retrain')}
        >
          🔄 Retrain Model
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
        {/* Train Tab - Flexible Training */}
        {activeTab === 'train' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="admin-section"
          >
            <h3>🎯 Train New Model</h3>
            <p className="section-description">
              Upload any CSV file with credit risk data. The system will automatically detect:
            </p>
            <ul className="feature-list">
              <li>✓ Target column (loan_status, default, target, etc.)</li>
              <li>✓ Numeric features (income, loan amount, etc.)</li>
              <li>✓ Categorical features (home ownership, loan grade, etc.)</li>
            </ul>
            <p className="section-description">
              <strong>Supports flexible CSV structures</strong> - no need to match exact column names!
            </p>

            <div className="file-upload-area">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                id="train-csv-file"
                style={{ display: 'none' }}
              />
              <label htmlFor="train-csv-file" className="file-upload-label">
                <div className="upload-icon">📊</div>
                <div className="upload-text">
                  {file ? file.name : 'Click to select training CSV file'}
                </div>
                <div className="upload-hint">
                  {file ? `${(file.size / 1024).toFixed(2)} KB` : 'Any CSV with credit risk data'}
                </div>
              </label>
            </div>

            <button
              className="btn-primary"
              onClick={handleFlexibleTraining}
              disabled={!file || flexTraining}
            >
              {flexTraining ? '⏳ Training Model...' : '🎯 Train New Model'}
            </button>

            {flexTrainResult && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="result-box success"
              >
                <h4>✅ Training Complete!</h4>
                {flexTrainResult.result && (
                  <>
                    <div className="result-stats">
                      <div className="stat">
                        <span className="stat-label">Features Detected:</span>
                        <span className="stat-value">
                          {flexTrainResult.result.preprocessing_info.n_features}
                        </span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Training Samples:</span>
                        <span className="stat-value">
                          {flexTrainResult.result.training_info.n_train}
                        </span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Accuracy:</span>
                        <span className="stat-value">
                          {(flexTrainResult.result.metrics.accuracy * 100).toFixed(2)}%
                        </span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">AUC-ROC:</span>
                        <span className="stat-value">
                          {flexTrainResult.result.metrics.auc_roc.toFixed(4)}
                        </span>
                      </div>
                    </div>
                    <div className="feature-info">
                      <p><strong>Detected Columns:</strong></p>
                      <p>Target: {flexTrainResult.result.preprocessing_info.target_column}</p>
                      <p>Numeric: {flexTrainResult.result.preprocessing_info.numeric_features.length} features</p>
                      <p>Categorical: {flexTrainResult.result.preprocessing_info.categorical_features.length} features</p>
                    </div>
                    <button className="btn-secondary" onClick={handleReloadModel}>
                      🔄 Reload Model in API
                    </button>
                  </>
                )}
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Import Tab */}
        {activeTab === 'import' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="admin-section"
          >
            <h3>Import CSV Data</h3>
            <p className="section-description">
              Upload a CSV file with loan data and actual outcomes (loan_status column).
              The data will be imported into the database for model retraining.
            </p>

            <div className="file-upload-area">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                id="csv-file"
                style={{ display: 'none' }}
              />
              <label htmlFor="csv-file" className="file-upload-label">
                <div className="upload-icon">📁</div>
                <div className="upload-text">
                  {file ? file.name : 'Click to select CSV file'}
                </div>
                <div className="upload-hint">
                  {file ? `${(file.size / 1024).toFixed(2)} KB` : 'CSV files only'}
                </div>
              </label>
            </div>

            <button
              className="btn-primary"
              onClick={handleImport}
              disabled={!file || importing}
            >
              {importing ? '⏳ Importing...' : '📥 Import Data'}
            </button>

            {importResult && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="result-box success"
              >
                <h4>✅ Import Successful</h4>
                <div className="result-stats">
                  <div className="stat">
                    <span className="stat-label">Imported:</span>
                    <span className="stat-value">{importResult.imported} rows</span>
                  </div>
                  {importResult.errors > 0 && (
                    <div className="stat">
                      <span className="stat-label">Errors:</span>
                      <span className="stat-value error">{importResult.errors} rows</span>
                    </div>
                  )}
                </div>
                <p className="result-message">{importResult.message}</p>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Retrain Tab */}
        {activeTab === 'retrain' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="admin-section"
          >
            <h3>Retrain Model</h3>
            <p className="section-description">
              Retrain the XGBoost model using data from the database.
              Requires at least 100 predictions with actual outcomes.
            </p>

            {retrainStatus && (
              <div className={`status-card ${retrainStatus.is_ready ? 'ready' : 'not-ready'}`}>
                <h4>Retraining Status</h4>
                <div className="status-grid">
                  <div className="status-item">
                    <span className="status-label">Total Predictions:</span>
                    <span className="status-value">{retrainStatus.total_predictions}</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">With Feedback:</span>
                    <span className="status-value">{retrainStatus.feedback_count}</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Feedback Ratio:</span>
                    <span className="status-value">
                      {(retrainStatus.feedback_ratio * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Ready:</span>
                    <span className={`status-value ${retrainStatus.is_ready ? 'ready' : 'not-ready'}`}>
                      {retrainStatus.is_ready ? '✅ Yes' : '❌ No'}
                    </span>
                  </div>
                </div>

                {!retrainStatus.is_ready && (
                  <div className="status-requirements">
                    <p>Requirements:</p>
                    <ul>
                      {retrainStatus.samples_needed > 0 && (
                        <li>Need {retrainStatus.samples_needed} more samples</li>
                      )}
                      {retrainStatus.feedback_needed > 0 && (
                        <li>Need {retrainStatus.feedback_needed} more feedback entries</li>
                      )}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <button
              className="btn-primary"
              onClick={handleRetrain}
              disabled={!retrainStatus?.is_ready || retraining}
            >
              {retraining ? '⏳ Retraining...' : '🔄 Start Retraining'}
            </button>

            {retrainResult && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="result-box success"
              >
                <h4>✅ Retraining Complete</h4>
                {retrainResult.result && (
                  <div className="result-stats">
                    <div className="stat">
                      <span className="stat-label">Training Samples:</span>
                      <span className="stat-value">{retrainResult.result.training_samples}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Test Samples:</span>
                      <span className="stat-value">{retrainResult.result.test_samples}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Accuracy:</span>
                      <span className="stat-value">
                        {(retrainResult.result.metrics.accuracy * 100).toFixed(2)}%
                      </span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">AUC-ROC:</span>
                      <span className="stat-value">
                        {retrainResult.result.metrics.auc_roc.toFixed(4)}
                      </span>
                    </div>
                  </div>
                )}
                <button className="btn-secondary" onClick={handleReloadModel}>
                  🔄 Reload Model in API
                </button>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Status Tab */}
        {activeTab === 'status' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="admin-section"
          >
            <h3>System Status</h3>
            
            {retrainStatus && (
              <div className="status-overview">
                <div className="overview-card">
                  <div className="overview-icon">📊</div>
                  <div className="overview-content">
                    <h4>Database</h4>
                    <p>{retrainStatus.total_predictions} predictions</p>
                    <p>{retrainStatus.feedback_count} with feedback</p>
                  </div>
                </div>

                <div className="overview-card">
                  <div className="overview-icon">
                    {retrainStatus.is_ready ? '✅' : '⏳'}
                  </div>
                  <div className="overview-content">
                    <h4>Retraining</h4>
                    <p>{retrainStatus.is_ready ? 'Ready' : 'Not Ready'}</p>
                    <p>{(retrainStatus.feedback_ratio * 100).toFixed(1)}% feedback</p>
                  </div>
                </div>

                <div className="overview-card">
                  <div className="overview-icon">🎯</div>
                  <div className="overview-content">
                    <h4>Requirements</h4>
                    <p>Min: {retrainStatus.min_samples_required} samples</p>
                    <p>Min: {(retrainStatus.min_feedback_ratio_required * 100).toFixed(0)}% feedback</p>
                  </div>
                </div>
              </div>
            )}

            <button className="btn-secondary" onClick={checkRetrainStatus}>
              🔄 Refresh Status
            </button>
          </motion.div>
        )}

        {/* Manage Tab - Clear Database */}
        {activeTab === 'manage' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
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
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="result-box success"
              >
                <h4>✅ Database Cleared</h4>
                <div className="result-stats">
                  <div className="stat">
                    <span className="stat-label">Total Deleted:</span>
                    <span className="stat-value">{clearResult.total_deleted} records</span>
                  </div>
                  {clearResult.deleted && (
                    <>
                      <div className="stat">
                        <span className="stat-label">Predictions:</span>
                        <span className="stat-value">{clearResult.deleted.predictions}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Applications:</span>
                        <span className="stat-value">{clearResult.deleted.loan_applications}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Other Records:</span>
                        <span className="stat-value">
                          {clearResult.deleted.feature_engineering + 
                           clearResult.deleted.mitigation_plans + 
                           clearResult.deleted.audit_logs + 
                           clearResult.deleted.model_metrics}
                        </span>
                      </div>
                    </>
                  )}
                </div>
                <p className="result-message">{clearResult.message}</p>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="result-box error"
          >
            <h4>❌ Error</h4>
            <p>{error}</p>
          </motion.div>
        )}
      </div>
    </div>
  )
}

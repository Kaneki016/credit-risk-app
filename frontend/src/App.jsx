import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import CSVUploader from './components/csv/CSVUploader'
import DynamicForm from './components/csv/DynamicForm'
import ResultCard from './components/results/ResultCard'
import BatchResultsDisplay from './components/results/BatchResultsDisplay'
import AdminPanel from './components/admin/AdminPanel'
import Chatbot from './components/chatbot/Chatbot'
import './styles/admin.css'
import './styles/chatbot.css'

export default function App(){
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [csvData, setCsvData] = useState(null)
  const [batchResults, setBatchResults] = useState(null)
  const [layout, setLayout] = useState('split') // 'split' or 'stacked'
  const [view, setView] = useState('prediction') // 'prediction' or 'admin'

  return (
    <div className="app-container">
      <header className="hero">
        <div>
          <h1>📊 Credit Risk CSV Analyzer</h1>
          <p className="subtitle">Upload CSV files for batch credit risk prediction with AI-powered insights</p>
        </div>
        <div className="view-toggle">
          <button
            className={`view-button ${view === 'prediction' ? 'active' : ''}`}
            onClick={() => setView('prediction')}
          >
            🔮 Predictions
          </button>
          <button
            className={`view-button ${view === 'admin' ? 'active' : ''}`}
            onClick={() => setView('admin')}
          >
            🔧 Admin
          </button>
        </div>
      </header>

      {view === 'prediction' && (
        <>
          {/* Layout Toggle */}
          <div className="controls-container">
            <div className="layout-toggle">
              <button
                className={`layout-button ${layout === 'split' ? 'active' : ''}`}
                onClick={() => setLayout('split')}
                title="Split view"
              >
                ⬌ Split View
              </button>
              <button
                className={`layout-button ${layout === 'stacked' ? 'active' : ''}`}
                onClick={() => setLayout('stacked')}
                title="Stacked view"
              >
                ☰ Stacked View
              </button>
            </div>
          </div>

          <main className={`main-grid ${layout === 'stacked' ? 'stacked' : ''}`}>
        <motion.section 
          className="panel"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <CSVUploader
            onDataParsed={setCsvData}
            onError={(e)=>{setError(e); setLoading(false)}}
          />
          {csvData && (
            <DynamicForm
              csvData={csvData}
              onResult={(r)=>{ 
                // Only set result for single predictions, not batch results
                if (r && !r.batchResults) {
                  setResult(r)
                  setBatchResults(null) // Clear batch results when single prediction is made
                  setLoading(false)
                  setError(null)
                }
              }} 
              onBatchResults={(results)=>{ 
                setBatchResults(results)
                setResult(null) // Clear single result when batch processing completes
                setLoading(false)
                setError(null)
              }}
              onLoading={()=>{setLoading(true); setError(null)}} 
              onError={(e)=>{setError(e); setLoading(false)}}
            />
          )}
        </motion.section>
        
        <motion.section 
          className="panel"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <AnimatePresence mode="wait">
            {loading && (
              <motion.div 
                key="loader"
                className="loader"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                Processing prediction...
              </motion.div>
            )}
            {error && (
              <motion.div 
                key="error"
                className="error"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ type: "spring", stiffness: 200, damping: 20 }}
              >
                {error}
              </motion.div>
            )}
            {batchResults && !loading && !error && (
              <BatchResultsDisplay batchResults={batchResults.batchResults} />
            )}
            {result && !batchResults && !loading && !error && <ResultCard data={result} />}
            {!result && !batchResults && !loading && !error && (
              <div style={{ 
                padding: '3rem', 
                textAlign: 'center', 
                color: '#718096',
                background: '#f7fafc',
                borderRadius: '8px',
                border: '1px dashed #cbd5e0'
              }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#4a5568' }}>Ready for Predictions</h3>
                <p style={{ margin: 0 }}>Upload a CSV file and make predictions to see results here</p>
              </div>
            )}
          </AnimatePresence>
        </motion.section>
          </main>
        </>
      )}

      {view === 'admin' && (
        <main>
          <AdminPanel />
        </main>
      )}

      <footer className="footer">
        {view === 'prediction' 
          ? 'CSV-based batch processing • AI-powered predictions • SHAP explainability'
          : 'Admin Panel • Import Data • Retrain Model • System Status'
        }
      </footer>

      {/* Chatbot */}
      <Chatbot />
    </div>
  )
}

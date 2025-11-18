import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import CSVUploader from './components/csv/CSVUploader'
import DynamicForm from './components/csv/DynamicForm'
import ResultCard from './components/results/ResultCard'

export default function App(){
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [csvData, setCsvData] = useState(null)
  const [layout, setLayout] = useState('split') // 'split' or 'stacked'

  return (
    <div className="app-container">
      <header className="hero">
        <div>
          <h1>📊 Credit Risk CSV Analyzer</h1>
          <p className="subtitle">Upload CSV files for batch credit risk prediction with AI-powered insights</p>
        </div>
      </header>

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
              onResult={(r)=>{ setResult(r); setLoading(false); setError(null)}} 
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
            {result && !loading && !error && <ResultCard data={result} />}
          </AnimatePresence>
        </motion.section>
      </main>

      <footer className="footer">CSV-based batch processing • AI-powered predictions • SHAP explainability</footer>
    </div>
  )
}

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Form from './components/Form'
import ResultCard from './components/ResultCard'

export default function App(){
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  return (
    <div className="app-container">
      <header className="hero">
        <div>
          <h1>💼 Credit Risk</h1>
          <p className="subtitle">Beautiful, fast React UI for the Agentic Credit Risk API</p>
        </div>
      </header>

      <main className="main-grid">
        <motion.section 
          className="panel"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Form 
            onResult={(r)=>{ setResult(r); setLoading(false); setError(null)}} 
            onLoading={()=>{setLoading(true); setError(null)}} 
            onError={(e)=>{setError(e); setLoading(false)}} 
          />
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

      <footer className="footer">Built for automation and human review • uses SHAP explainability</footer>
    </div>
  )
}

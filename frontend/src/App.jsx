import React, { useState } from 'react'
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
        <section className="panel">
          <Form onResult={(r)=>{ setResult(r); setLoading(false); setError(null)}} onLoading={()=>{setLoading(true); setError(null)}} onError={(e)=>{setError(e); setLoading(false)}} />
        </section>
        <section className="panel">
          {loading && <div className="loader">Loading…</div>}
          {error && <div className="error">{error}</div>}
          {result && <ResultCard data={result} />}
        </section>
      </main>

      <footer className="footer">Built for automation and human review • uses SHAP explainability</footer>
    </div>
  )
}

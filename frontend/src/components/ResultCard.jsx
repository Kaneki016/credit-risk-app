import React from 'react'

function ShapTable({shap}){
  if(!shap) return null
  const entries = Object.entries(shap).sort((a,b)=>Math.abs(b[1])-Math.abs(a[1])).slice(0,6)
  return (
    <table className="shap-table">
      <thead><tr><th>Feature</th><th>SHAP value</th></tr></thead>
      <tbody>
        {entries.map(([k,v])=> <tr key={k}><td>{k}</td><td>{v.toFixed(4)}</td></tr>)}
      </tbody>
    </table>
  )
}

export default function ResultCard({data}){
  if(!data) return null
  const prob = data.probability_default_percent ?? (data.probability_default * 100)
  return (
    <div className="result-card">
      <h3>Prediction</h3>
      <div className="result-row">
        <div>
          <div className="badge">{data.risk_level}</div>
          <div className="big-number">{prob}%</div>
        </div>
        <div className="llm">
          <h4>LLM Explanation</h4>
          <div className="llm-text">{data.llm_explanation || '—'}</div>
        </div>
      </div>

      <section>
        <h4>Top SHAP contributions</h4>
        <ShapTable shap={data.shap_explanation} />
      </section>

      {data.remediation_suggestion && (
        <section>
          <h4>Suggested Remediation</h4>
          <div className="remediation">{data.remediation_suggestion}</div>
        </section>
      )}
    </div>
  )
}

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

function ShapTable({shap}){
  if(!shap) return null
  const entries = Object.entries(shap).sort((a,b)=>Math.abs(b[1])-Math.abs(a[1])).slice(0,6)
  const maxAbs = Math.max(...entries.map(([,v]) => Math.abs(v)))
  const [hoveredFeature, setHoveredFeature] = useState(null)
  const [focusedFeature, setFocusedFeature] = useState(null)

  // Calculate total positive and negative contributions
  const totalPositive = entries.reduce((sum, [,v]) => sum + (v > 0 ? v : 0), 0)
  const totalNegative = entries.reduce((sum, [,v]) => sum + (v < 0 ? Math.abs(v) : 0), 0)
  
  return (
    <table className="shap-table">
      <thead><tr><th>Feature</th><th>Impact</th><th>Value</th></tr></thead>
      <tbody>
        {entries.map(([k,v])=> (
          <motion.tr 
            key={k}
            onHoverStart={() => setHoveredFeature(k)}
            onHoverEnd={() => setHoveredFeature(null)}
            animate={{
              backgroundColor: hoveredFeature === k ? 'rgba(25,118,210,0.05)' : 'transparent'
            }}
            transition={{ duration: 0.2 }}
          >
            <td>{k}</td>
            <td className="shap-bar-cell">
              <div className="shap-bar-container">
                <motion.div 
                  className={`shap-bar ${v < 0 ? 'negative' : 'positive'}`}
                  initial={{ width: 0 }}
                  animate={{ 
                    width: `${(Math.abs(v)/maxAbs * 100)}%`,
                    marginLeft: v < 0 ? 'auto' : '0',
                    scale: hoveredFeature === k ? 1.05 : 1
                  }}
                  transition={{ duration: 0.5 }}
                >
                  {hoveredFeature === k && (
                    <motion.div 
                      className="shap-tooltip"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      Impact: {v.toFixed(4)}
                    </motion.div>
                  )}
                </motion.div>
              </div>
            </td>
            <td className={v < 0 ? 'negative' : 'positive'}>{v.toFixed(4)}</td>
          </motion.tr>
        ))}
      </tbody>
    </table>
  )
}

export default function ResultCard({data}){
  if(!data) return null
  const prob = data.probability_default_percent ?? (data.probability_default * 100)
  const [animate, setAnimate] = useState(false)
  
  useEffect(() => {
    // Only trigger entrance animation
    setAnimate(true)
  }, [data])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="result-card"
    >
      <motion.h3
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        Prediction
      </motion.h3>
      <div className="result-row">
        <div>
          <motion.div 
            className={`badge ${data.risk_level.toLowerCase()}`}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, damping: 10 }}
          >
            {data.risk_level}
          </motion.div>
          <motion.div 
            className="risk-meter"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <motion.div 
              className="risk-fill"
              initial={{ width: 0 }}
              animate={{ width: `${prob}%` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
            />
            <motion.div 
              className="big-number"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              {prob.toFixed(1)}%
            </motion.div>
          </motion.div>
        </div>
        <motion.div 
          className="llm"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <h4>LLM Explanation</h4>
          <div className="llm-text">{data.llm_explanation || '—'}</div>
        </motion.div>
      </div>

      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
        <h4>Top SHAP contributions</h4>
        <ShapTable shap={data.shap_explanation} />
      </motion.section>

      {data.remediation_suggestion && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.5 }}
        >
          <h4>Suggested Remediation</h4>
          <div className="remediation">{data.remediation_suggestion}</div>
        </motion.section>
      )}
    </motion.div>
  )
}

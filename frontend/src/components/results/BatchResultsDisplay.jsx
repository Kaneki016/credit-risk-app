import React from 'react'
import { motion } from 'framer-motion'

export default function BatchResultsDisplay({ batchResults }) {
  if (!batchResults || batchResults.length === 0) return null

  const downloadBatchResults = () => {
    const csv = [
      // Header
      ['Row', 'Risk Level', 'Probability %', 'Prediction', 'Status'].join(','),
      // Data
      ...batchResults.map(r => [
        (r?.rowIndex ?? 0) + 1,
        r?.result?.risk_level || 'N/A',
        r?.result?.probability_default_percent || 'N/A',
        r?.result?.binary_prediction || 'N/A',
        r?.status || 'N/A'
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

  const successCount = batchResults.filter(r => r?.status === 'success').length
  const errorCount = batchResults.filter(r => r?.status === 'error').length

  return (
    <motion.div
      className="batch-results-display"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        padding: '1.5rem',
        background: '#ffffff',
        borderRadius: '8px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h3 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 600 }}>✅ Batch Processing Complete</h3>
        <button 
          onClick={downloadBatchResults} 
          style={{
            padding: '0.5rem 1rem',
            background: '#4299e1',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 600,
            fontSize: '0.9rem'
          }}
        >
          📥 Download CSV
        </button>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: '1rem', 
        marginBottom: '1.5rem' 
      }}>
        <div style={{ 
          padding: '1rem', 
          background: '#f7fafc', 
          borderRadius: '6px', 
          textAlign: 'center',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#4a5568' }}>{batchResults.length}</div>
          <div style={{ fontSize: '0.85rem', color: '#718096', marginTop: '0.25rem' }}>Total Processed</div>
        </div>
        <div style={{ 
          padding: '1rem', 
          background: '#f0fff4', 
          borderRadius: '6px', 
          textAlign: 'center',
          border: '1px solid #9ae6b4'
        }}>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#22543d' }}>✅ {successCount}</div>
          <div style={{ fontSize: '0.85rem', color: '#22543d', marginTop: '0.25rem' }}>Success</div>
        </div>
        <div style={{ 
          padding: '1rem', 
          background: '#fff5f5', 
          borderRadius: '6px', 
          textAlign: 'center',
          border: '1px solid #fc8181'
        }}>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#742a2a' }}>❌ {errorCount}</div>
          <div style={{ fontSize: '0.85rem', color: '#742a2a', marginTop: '0.25rem' }}>Errors</div>
        </div>
      </div>

      {/* Results Table */}
      <div style={{ 
        marginTop: '1.5rem', 
        maxHeight: '500px', 
        overflowY: 'auto', 
        overflowX: 'auto',
        border: '1px solid #e2e8f0',
        borderRadius: '6px'
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem', minWidth: '600px' }}>
          <thead style={{ position: 'sticky', top: 0, background: '#f7fafc', zIndex: 10 }}>
            <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
              <th style={{ padding: '0.75rem', textAlign: 'left', fontWeight: 600 }}>Row</th>
              <th style={{ padding: '0.75rem', textAlign: 'left', fontWeight: 600 }}>Risk Level</th>
              <th style={{ padding: '0.75rem', textAlign: 'left', fontWeight: 600 }}>Probability</th>
              <th style={{ padding: '0.75rem', textAlign: 'left', fontWeight: 600 }}>Prediction</th>
              <th style={{ padding: '0.75rem', textAlign: 'left', fontWeight: 600 }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {batchResults.map((result, idx) => {
              // Safely extract values with null checks to prevent crashes
              if (!result || typeof result !== 'object') {
                return (
                  <tr key={`batch-error-${idx}`} style={{ borderBottom: '1px solid #e2e8f0', backgroundColor: '#fff5f5' }}>
                    <td colSpan="5" style={{ padding: '0.75rem', color: '#e53e3e' }}>Invalid result data</td>
                  </tr>
                )
              }
              
              const riskLevel = result?.result?.risk_level || null
              const probability = result?.result?.probability_default_percent ?? null
              const binaryPred = result?.result?.binary_prediction ?? null
              const isSuccess = result?.status === 'success'
              const errorMsg = result?.error || 'Unknown error'
              const rowIndex = result?.rowIndex != null ? result.rowIndex : idx
              
              return (
                <tr 
                  key={`batch-result-${rowIndex}-${idx}`}
                  style={{ 
                    borderBottom: '1px solid #e2e8f0',
                    backgroundColor: !isSuccess ? '#fff5f5' : idx % 2 === 0 ? '#ffffff' : '#f7fafc'
                  }}
                >
                  <td style={{ padding: '0.75rem' }}>{rowIndex + 1}</td>
                  <td style={{ padding: '0.75rem' }}>
                    {isSuccess && riskLevel ? (
                      <span style={{ 
                        padding: '0.25rem 0.5rem', 
                        borderRadius: '4px',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        backgroundColor: String(riskLevel).toLowerCase().includes('low') ? '#c6f6d5' : '#fed7d7',
                        color: String(riskLevel).toLowerCase().includes('low') ? '#22543d' : '#742a2a'
                      }}>
                        {String(riskLevel)}
                      </span>
                    ) : 'N/A'}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    {isSuccess && probability != null 
                      ? `${Number(probability).toFixed(2)}%`
                      : 'N/A'}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    {isSuccess && binaryPred != null
                      ? (Number(binaryPred) === 1 ? 'High Risk' : 'Low Risk')
                      : 'N/A'}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    {isSuccess ? (
                      <span style={{ color: '#38a169', fontWeight: 600 }}>✅ Success</span>
                    ) : (
                      <span style={{ color: '#e53e3e', fontWeight: 600 }}>❌ {String(errorMsg).substring(0, 50)}</span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </motion.div>
  )
}

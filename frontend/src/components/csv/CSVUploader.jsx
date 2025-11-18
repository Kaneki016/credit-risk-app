import React, { useState, useRef } from 'react'
import Papa from 'papaparse'
import * as XLSX from 'xlsx'
import { motion, AnimatePresence } from 'framer-motion'

export default function CSVUploader({ onDataParsed, onError }) {
  const [isDragging, setIsDragging] = useState(false)
  const [fileName, setFileName] = useState(null)
  const [preview, setPreview] = useState(null)
  const fileInputRef = useRef(null)

  const isExcelFile = (filename) => {
    const excelExtensions = ['.xlsx', '.xls', '.xlsm', '.xlsb']
    return excelExtensions.some(ext => filename.toLowerCase().endsWith(ext))
  }

  const isCsvFile = (filename) => {
    return filename.toLowerCase().endsWith('.csv')
  }

  const handleExcelFile = (file) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        
        // Get first sheet
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        
        // Convert to JSON
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { 
          header: 1,
          defval: null,
          blankrows: false
        })
        
        if (jsonData.length === 0) {
          onError && onError('Excel file is empty')
          return
        }
        
        // First row is headers
        const headers = jsonData[0]
        const rows = jsonData.slice(1)
        
        // Convert to array of objects
        const parsedData = rows.map(row => {
          const obj = {}
          headers.forEach((header, index) => {
            obj[header] = row[index]
          })
          return obj
        }).filter(row => Object.values(row).some(val => val !== null && val !== undefined && val !== ''))
        
        if (parsedData.length === 0) {
          onError && onError('Excel file contains no data rows')
          return
        }
        
        // Show preview
        setPreview({
          columns: headers,
          rows: parsedData.slice(0, 3),
          totalRows: parsedData.length
        })
        
        // Pass data to parent
        onDataParsed && onDataParsed({
          columns: headers,
          data: parsedData,
          fileName: file.name
        })
        
      } catch (error) {
        console.error('Excel parsing error:', error)
        onError && onError('Failed to parse Excel file: ' + error.message)
      }
    }
    
    reader.onerror = () => {
      onError && onError('Failed to read Excel file')
    }
    
    reader.readAsArrayBuffer(file)
  }

  const handleCsvFile = (file) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: true,
      complete: (results) => {
        if (results.errors.length > 0) {
          console.error('CSV parsing errors:', results.errors)
          onError && onError('Error parsing CSV file')
          return
        }

        if (results.data.length === 0) {
          onError && onError('CSV file is empty')
          return
        }

        // Get column names from the first row
        const columns = Object.keys(results.data[0])
        
        // Show preview of first 3 rows
        setPreview({
          columns,
          rows: results.data.slice(0, 3),
          totalRows: results.data.length
        })

        // Pass data to parent
        onDataParsed && onDataParsed({
          columns,
          data: results.data,
          fileName: file.name
        })
      },
      error: (error) => {
        console.error('CSV parsing error:', error)
        onError && onError('Failed to parse CSV file')
      }
    })
  }

  const handleFile = (file) => {
    if (!file) return

    const filename = file.name
    
    if (isExcelFile(filename)) {
      setFileName(filename)
      handleExcelFile(file)
    } else if (isCsvFile(filename)) {
      setFileName(filename)
      handleCsvFile(file)
    } else {
      onError && onError('Please upload a CSV or Excel file (.csv, .xlsx, .xls)')
      return
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    handleFile(file)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleClear = () => {
    setFileName(null)
    setPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    onDataParsed && onDataParsed(null)
  }

  return (
    <div className="csv-uploader">
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.xlsx,.xls,.xlsm,.xlsb"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />

      <AnimatePresence mode="wait">
        {!fileName ? (
          <motion.div
            key="dropzone"
            className={`dropzone ${isDragging ? 'dragging' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={handleClick}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="dropzone-icon">📊</div>
            <div className="dropzone-text">
              <strong>Drop CSV or Excel file here</strong> or click to browse
            </div>
            <div className="dropzone-hint">
              Supports: .csv, .xlsx, .xls files with loan application data
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="uploaded"
            className="file-uploaded"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div className="file-info">
              <div className="file-icon">✅</div>
              <div className="file-details">
                <div className="file-name">{fileName}</div>
                {preview && (
                  <div className="file-stats">
                    {preview.totalRows} rows • {preview.columns.length} columns
                  </div>
                )}
              </div>
              <button
                type="button"
                className="clear-button"
                onClick={handleClear}
                title="Remove file"
              >
                ✕
              </button>
            </div>

            {preview && (
              <motion.div
                className="csv-preview"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                transition={{ delay: 0.2 }}
              >
                <div className="preview-title">Preview (first 3 rows):</div>
                <div className="preview-table-container">
                  <table className="preview-table">
                    <thead>
                      <tr>
                        {preview.columns.map((col, i) => (
                          <th key={i}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {preview.rows.map((row, i) => (
                        <tr key={i}>
                          {preview.columns.map((col, j) => (
                            <td key={j}>{String(row[col] ?? '')}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

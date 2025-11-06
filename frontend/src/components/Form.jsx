import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Tooltip } from 'react-tooltip'
import { motion, AnimatePresence } from 'framer-motion'

const API_WEBHOOK = window.__API_WEBHOOK_URL__ || 'http://localhost:5678/webhook/6c5765f3-1d52-4d65-be13-c37133a73bf1'

const fieldInfo = {
  person_age: { min: 18, max: 120, tip: "Applicant must be at least 18 years old" },
  person_income: { min: 0, max: 1000000, tip: "Annual income before taxes" },
  person_emp_length: { min: 0, max: 600, tip: "Employment length in years" },
  loan_amnt: { min: 1000, max: 100000, tip: "Amount requested for the loan" },
  loan_int_rate: { min: 0, max: 30, tip: "Annual interest rate %" },
  loan_percent_income: { min: 0, max: 1, tip: "Loan amount as fraction of income (0-1)" }
}

export default function Form({onResult, onLoading, onError}){
  const [form, setForm] = useState({
    person_age:30, person_income:50000, person_emp_length:12, loan_amnt:10000,
    loan_int_rate:10.0, loan_percent_income:0.25, cb_person_cred_hist_length:5,
    home_ownership:'RENT', loan_intent:'PERSONAL', loan_grade:'A', default_on_file:'N'
  })
  const [errors, setErrors] = useState({})
  const [isDirty, setIsDirty] = useState(false)

  // Validate form fields and update error state
  useEffect(() => {
    const newErrors = {}
    Object.entries(fieldInfo).forEach(([field, info]) => {
      const value = form[field]
      if (value < info.min || value > info.max) {
        newErrors[field] = `Must be between ${info.min} and ${info.max}`
      }
    })
    setErrors(newErrors)
  }, [form])

  function setField(k, v){ 
    setForm({...form, [k]: v})
    setIsDirty(true)
  }

  function handleKeyDown(e, fieldName) {
    const input = e.target
    const step = e.shiftKey ? 10 : 1

    switch(e.key) {
      case 'ArrowUp':
        e.preventDefault()
        setField(fieldName, parseFloat(input.value || 0) + step)
        break
      case 'ArrowDown':
        e.preventDefault()
        setField(fieldName, parseFloat(input.value || 0) - step)
        break
      case 'Enter':
        e.preventDefault()
        const form = input.form
        const inputs = Array.from(form.elements)
        const idx = inputs.indexOf(input)
        inputs[(idx + 1) % inputs.length].focus()
        break
    }
  }

  async function submit(e){
    e.preventDefault()
    if (Object.keys(errors).length > 0) {
      onError && onError('Please fix form errors before submitting')
      return
    }
    onLoading && onLoading()
    try{
      const resp = await axios.post(API_WEBHOOK, form, { timeout: 30000 })
      // unwrap common webhook wrappers
      let data = resp.data
      if (Array.isArray(data) && data.length===1) data = data[0]
      if (data.body) data = data.body
      onResult && onResult(data)
      setIsDirty(false)
    }catch(err){
      console.error(err)
      const msg = err.response?.data?.detail || err.message || 'Request failed'
      onError && onError(String(msg))
    }
  }

  return (
    <motion.form 
      className="form" 
      onSubmit={submit}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <motion.h3
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        Applicant Information
      </motion.h3>
      <motion.div className="row"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1 }}
      >
        <label data-tooltip-id="field-tip" data-tooltip-content={fieldInfo.person_age.tip}>
          Person Age
          <input 
            type="number" 
            value={form.person_age} 
            onChange={e=>setField('person_age', parseInt(e.target.value||0))}
            onKeyDown={e => handleKeyDown(e, 'person_age')}
            className={errors.person_age ? 'error' : ''} 
          />
          {errors.person_age && <span className="error-text">{errors.person_age}</span>}
        </label>
        <label data-tooltip-id="field-tip" data-tooltip-content={fieldInfo.person_emp_length.tip}>
          Employment (Years)
          <input 
            type="number" 
            value={form.person_emp_length} 
            onChange={e=>setField('person_emp_length', parseFloat(e.target.value||0))}
            onKeyDown={e => handleKeyDown(e, 'person_emp_length')}
            className={errors.person_emp_length ? 'error' : ''} 
          />
          {errors.person_emp_length && <span className="error-text">{errors.person_emp_length}</span>}
        </label>
      </motion.div>
      <div className="row">
        <label data-tooltip-id="field-tip" data-tooltip-content={fieldInfo.person_income.tip}>
          Annual Income
          <input 
            type="number" 
            value={form.person_income} 
            onChange={e=>setField('person_income', parseFloat(e.target.value||0))}
            className={errors.person_income ? 'error' : ''} 
          />
          {errors.person_income && <span className="error-text">{errors.person_income}</span>}
        </label>
        <label data-tooltip-id="field-tip" data-tooltip-content={fieldInfo.loan_amnt.tip}>
          Loan Amount
          <input 
            type="number" 
            value={form.loan_amnt} 
            onChange={e=>setField('loan_amnt', parseFloat(e.target.value||0))}
            className={errors.loan_amnt ? 'error' : ''} 
          />
          {errors.loan_amnt && <span className="error-text">{errors.loan_amnt}</span>}
        </label>
      </div>
      <div className="row">
        <label data-tooltip-id="field-tip" data-tooltip-content={fieldInfo.loan_percent_income.tip}>
          Loan % of Income
          <input 
            type="number" 
            step="0.01" 
            value={form.loan_percent_income} 
            onChange={e=>setField('loan_percent_income', parseFloat(e.target.value||0))}
            className={errors.loan_percent_income ? 'error' : ''} 
          />
          {errors.loan_percent_income && <span className="error-text">{errors.loan_percent_income}</span>}
        </label>
        <label data-tooltip-id="field-tip" data-tooltip-content={fieldInfo.loan_int_rate.tip}>
          Interest Rate (%)
          <input 
            type="number" 
            step="0.1" 
            value={form.loan_int_rate} 
            onChange={e=>setField('loan_int_rate', parseFloat(e.target.value||0))}
            className={errors.loan_int_rate ? 'error' : ''} 
          />
          {errors.loan_int_rate && <span className="error-text">{errors.loan_int_rate}</span>}
        </label>
      </div>
      <Tooltip id="field-tip" />

      <div className="row">
        <label>Credit History (years)<input type="number" value={form.cb_person_cred_hist_length} onChange={e=>setField('cb_person_cred_hist_length', parseInt(e.target.value||0))} /></label>
        <label>Previous Default<select value={form.default_on_file} onChange={e=>setField('default_on_file', e.target.value)}>
          <option value="N">N</option>
          <option value="Y">Y</option>
        </select></label>
      </div>

      <div className="row">
        <label>Home Ownership<select value={form.home_ownership} onChange={e=>setField('home_ownership', e.target.value)}>
          <option>RENT</option><option>OWN</option><option>MORTGAGE</option><option>OTHER</option>
        </select></label>
        <label>Loan Intent<select value={form.loan_intent} onChange={e=>setField('loan_intent', e.target.value)}>
          <option>PERSONAL</option><option>EDUCATION</option><option>MEDICAL</option><option>VENTURE</option><option>HOMEIMPROVEMENT</option><option>DEBTCONSOLIDATION</option>
        </select></label>
      </div>

      <div className="row">
        <label>Loan Grade<select value={form.loan_grade} onChange={e=>setField('loan_grade', e.target.value)}>
          <option>A</option><option>B</option><option>C</option><option>D</option><option>E</option><option>F</option><option>G</option>
        </select></label>
      </div>

      <motion.div 
        className="actions"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.5 }}
      >
        <motion.button 
          type="submit" 
          className={`primary ${Object.keys(errors).length > 0 ? 'disabled' : ''}`}
          disabled={Object.keys(errors).length > 0}
          whileHover={{ scale: Object.keys(errors).length > 0 ? 1 : 1.02 }}
          whileTap={{ scale: Object.keys(errors).length > 0 ? 1 : 0.98 }}
        >
          {isDirty ? '🔄' : '✨'} Predict Credit Risk
        </motion.button>
      </motion.div>
    </motion.form>
  )
}

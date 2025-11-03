import React, { useState } from 'react'
import axios from 'axios'

const API_WEBHOOK = window.__API_WEBHOOK_URL__ || 'http://localhost:5678/webhook/6c5765f3-1d52-4d65-be13-c37133a73bf1'

export default function Form({onResult, onLoading, onError}){
  const [form, setForm] = useState({
    person_age:30, person_income:50000, person_emp_length:12, loan_amnt:10000,
    loan_int_rate:10.0, loan_percent_income:0.25, cb_person_cred_hist_length:5,
    home_ownership:'RENT', loan_intent:'PERSONAL', loan_grade:'A', default_on_file:'N'
  })

  function setField(k, v){ setForm({...form, [k]: v}) }

  async function submit(e){
    e.preventDefault()
    onLoading && onLoading()
    try{
      const resp = await axios.post(API_WEBHOOK, form, { timeout: 30000 })
      // unwrap common webhook wrappers
      let data = resp.data
      if (Array.isArray(data) && data.length===1) data = data[0]
      if (data.body) data = data.body
      onResult && onResult(data)
    }catch(err){
      console.error(err)
      const msg = err.response?.data?.detail || err.message || 'Request failed'
      onError && onError(String(msg))
    }
  }

  return (
    <form className="form" onSubmit={submit}>
      <h3>Applicant Information</h3>
      <div className="row">
        <label>Person Age<input type="number" value={form.person_age} onChange={e=>setField('person_age', parseInt(e.target.value||0))} /></label>
        <label>Employment (months)<input type="number" value={form.person_emp_length} onChange={e=>setField('person_emp_length', parseFloat(e.target.value||0))} /></label>
      </div>
      <div className="row">
        <label>Annual Income<input type="number" value={form.person_income} onChange={e=>setField('person_income', parseFloat(e.target.value||0))} /></label>
        <label>Loan Amount<input type="number" value={form.loan_amnt} onChange={e=>setField('loan_amnt', parseFloat(e.target.value||0))} /></label>
      </div>
      <div className="row">
        <label>Loan % of Income<input type="number" step="0.01" value={form.loan_percent_income} onChange={e=>setField('loan_percent_income', parseFloat(e.target.value||0))} /></label>
        <label>Interest Rate (%)<input type="number" step="0.1" value={form.loan_int_rate} onChange={e=>setField('loan_int_rate', parseFloat(e.target.value||0))} /></label>
      </div>

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

      <div className="actions">
        <button type="submit" className="primary">✨ Predict Credit Risk</button>
      </div>
    </form>
  )
}

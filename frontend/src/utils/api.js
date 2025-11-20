// Centralized API configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const ENDPOINTS = {
  PREDICT_DYNAMIC: `${API_BASE_URL}/predict_risk_dynamic`,
  PREDICT_BATCH: `${API_BASE_URL}/predict_risk_batch`,
  IMPORT_CSV: `${API_BASE_URL}/db/import_csv`,
  RETRAIN: `${API_BASE_URL}/db/retrain`,
  RETRAIN_STATUS: `${API_BASE_URL}/db/retraining/status`,
  RELOAD_MODEL: `${API_BASE_URL}/reload_model`,
  TRAIN_FLEXIBLE: `${API_BASE_URL}/train/flexible`,
  CLEAR_DB: `${API_BASE_URL}/db/clear`,
  CHATBOT: `${API_BASE_URL}/chatbot/query`, // Note: Chatbot route might need to be moved to v1 if it exists
};

export default API_BASE_URL;

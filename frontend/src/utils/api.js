const API_BASE_URL = 'http://localhost:8000/api/v1'
const ROOT_API_URL = 'http://localhost:8000'

export const ENDPOINTS = {
  // Versioned API endpoints (under /api/v1)
    IMPORT_CSV: `${API_BASE_URL}/db/import_csv`,
    RETRAIN: `${API_BASE_URL}/db/retrain`,
    RETRAIN_STATUS: `${API_BASE_URL}/db/retraining/status`,
    CLEAR_DB: `${API_BASE_URL}/db/clear`,
    GET_SCHEMA: `${API_BASE_URL}/db/schema`,
  CHATBOT: `${API_BASE_URL}/chatbot/query`,
  
  // Prediction endpoints
  PREDICT: `${API_BASE_URL}/predict_risk`,
  PREDICT_DYNAMIC: `${API_BASE_URL}/predict_risk_dynamic`,
  PREDICT_BATCH: `${API_BASE_URL}/predict_risk_batch`,

  // Root-level management endpoints (not versioned)
  RELOAD_MODEL: `${ROOT_API_URL}/model/reload`,
  MODEL_STATE: `${ROOT_API_URL}/model/state`,
  MODEL_HEALTH: `${ROOT_API_URL}/model/health`,
  API_HEALTH: `${ROOT_API_URL}/health`,
}

export default API_BASE_URL

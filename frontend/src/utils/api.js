const API_BASE_URL = 'http://localhost:8000/api/v1'

export const ENDPOINTS = {
    IMPORT_CSV: `${API_BASE_URL}/db/import_csv`,
    RETRAIN: `${API_BASE_URL}/db/retrain`,
    RETRAIN_STATUS: `${API_BASE_URL}/db/retraining/status`,
    RELOAD_MODEL: `${API_BASE_URL}/model/reload`,
    CLEAR_DB: `${API_BASE_URL}/db/clear`,
    GET_SCHEMA: `${API_BASE_URL}/db/schema`,
}

export default API_BASE_URL

# backend/api/main.py
import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Internal imports
from backend.database import init_db, check_connection
from backend.api.clear_database_endpoint import router as clear_db_router
from backend.core.logging_setup import configure_logging
from backend.api.routes.model import router as model_router, ModelManager
from backend.api.routes.prediction import router as prediction_router
from backend.api.routes.retraining import router as retraining_router
from backend.api.routes.data_management import router as data_router
from backend.api.routes.chatbot import router as chatbot_router

# --- Setup Logging ---
configure_logging()
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# --- Rate Limiting Setup ---
limiter = Limiter(key_func=get_remote_address)

# --- Initialize FastAPI Application ---
app = FastAPI(
    title="Credit Risk Prediction API",
    version="2.0.0",
    description="AI-powered credit risk prediction with XGBoost ML model, SHAP explainability, and AI-generated insights.",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Initialize database and models on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database, check connection, and load models on startup."""
    # Database initialization
    try:
        if check_connection():
            init_db()
            logger.info("Database initialized successfully")
        else:
            logger.warning("Database connection failed - running without database")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        logger.warning("API will run without database functionality")

    # Model initialization
    ModelManager.load_models()


# Allow cross-origin requests from local frontend (development)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers with versioning
# We mount them under /api/v1
# We also keep the root paths for backward compatibility if needed, or we update the frontend.
# The plan said "Implement API Versioning", so we should prefer /api/v1.
# However, to avoid breaking the frontend immediately before I update it, I will include them twice or just update the frontend.
# I will update the frontend in the next steps, so I will move them to /api/v1.
# BUT, I also need to support the legacy paths until I update the frontend.
# Actually, I'll just add the versioned paths and keep the old ones for now?
# No, cleaner to just have versioned paths and update frontend.
# But wait, the user asked "help me to do the modification".
# I will update the frontend to use /api/v1.

api_v1_router = FastAPI()
api_v1_router.include_router(clear_db_router, tags=["database"])
api_v1_router.include_router(model_router, tags=["model"])
api_v1_router.include_router(prediction_router, tags=["prediction"])
api_v1_router.include_router(retraining_router, tags=["retraining"])
api_v1_router.include_router(data_router, tags=["data"])
api_v1_router.include_router(chatbot_router, tags=["chatbot"])

# Mount the v1 app
app.mount("/api/v1", api_v1_router)

# Also include them at root for backward compatibility during migration (optional but safer)
# app.include_router(clear_db_router, tags=["database"])
# app.include_router(model_router, tags=["model"])
# app.include_router(prediction_router, tags=["prediction"])
# I will comment them out to enforce versioning, but I must update frontend immediately.
# Actually, let's keep them at root for now to prevent breakage while I update frontend.
# I'll add a deprecation warning in logs if possible, but for now just include them.
app.include_router(clear_db_router, tags=["database"], include_in_schema=False)
app.include_router(model_router, tags=["model"], include_in_schema=False)
app.include_router(prediction_router, tags=["prediction"], include_in_schema=False)
app.include_router(retraining_router, tags=["retraining"], include_in_schema=False)
app.include_router(data_router, tags=["data"], include_in_schema=False)
app.include_router(chatbot_router, tags=["chatbot"], include_in_schema=False)


@app.get("/")
@limiter.limit("5/minute")
def root(request: Request):
    return {"message": "Credit Risk Prediction API is running. Visit /docs for documentation."}


@app.get("/health")
def health_check():
    return {"status": "ok"}

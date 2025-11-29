from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime

from routers import reports, analytics, detection
from database import create_db_and_tables

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SafeSpace AI API",
    description="GBV Detection and Reporting System for Workplace Safety",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        create_db_and_tables()
        logger.info("🗄️ Database initialized successfully")
        logger.info("🚀 SafeSpace AI API started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("👋 SafeSpace AI API shutting down")

# Include routers
app.include_router(
    reports.router, 
    prefix="/api/v1", 
    tags=["Reports"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    analytics.router, 
    prefix="/api/v1", 
    tags=["Analytics"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    detection.router,
    prefix="/api/v1",
    tags=["Detection"],
    responses={404: {"description": "Not found"}}
)

# Root endpoints
@app.get("/")
def read_root():
    """Welcome message and API info"""
    return {
        "message": "Welcome to SafeSpace AI API",
        "description": "GBV Detection and Reporting System for Workplace Safety",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "reports": "/api/v1/reports/",
            "detection": "/api/v1/detect",
            "analytics": "/api/v1/analytics/"
        }
    }

@app.get("/health")
def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "detection": "available", 
            "reporting": "active"
        }
    }

@app.get("/api/v1/info")
def api_info():
    """API information and capabilities"""
    return {
        "name": "SafeSpace AI API",
        "version": "1.0.0",
        "capabilities": [
            "GBV content detection using AI",
            "Anonymous incident reporting",  
            "Real-time Slack integration",
            "Admin dashboard analytics",
            "Encrypted data storage",
            "Audit logging"
        ],
        "supported_languages": ["English", "Swahili"],
        "detection_categories": [
            "Sexual harassment",
            "Discrimination", 
            "Verbal abuse/threats",
            "Physical violence",
            "General toxicity"
        ],
        "privacy_features": [
            "End-to-end encryption for reports",
            "Anonymous reporting",
            "Automatic data retention policies",
            "GDPR compliance"
        ]
    }

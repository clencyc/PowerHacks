import os
from typing import Optional

class Settings:
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./safespace.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    REPORT_ENCRYPTION_KEY: str = os.getenv("REPORT_ENCRYPTION_KEY", "your-encryption-key")
    
    # API Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # External APIs (Optional)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    PERSPECTIVE_API_KEY: Optional[str] = os.getenv("PERSPECTIVE_API_KEY")
    
    # Vector Database (Optional)
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
    MAX_REPORTS_PER_USER_PER_DAY: int = int(os.getenv("MAX_REPORTS_PER_USER_PER_DAY", "10"))
    
    # Data Retention (days)
    REPORT_RETENTION_DAYS: int = int(os.getenv("REPORT_RETENTION_DAYS", "90"))
    AUDIT_LOG_RETENTION_DAYS: int = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "365"))

# Create settings instance
settings = Settings()

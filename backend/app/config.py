# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://medchain_user:medchain_pass@localhost:5432/medchain_db"
    
    # API Keys
    GROQ_API_KEY: str = ""
    OPENFDA_API_KEY: Optional[str] = ""
    
    # App
    DEBUG: bool = False
    SECRET_KEY: str = "change-this-in-production"
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Hospital parameters
    HOSPITAL_BED_COUNT: int = 500
    FORECAST_HORIZON_DAYS: int = 90
    SERVICE_LEVEL: float = 0.95
    
    # Risk scoring weights (must sum to 1.0)
    WEIGHT_SUPPLIER_COUNT: float = 0.30
    WEIGHT_API_DEPENDENCY: float = 0.30
    WEIGHT_SHELF_LIFE: float = 0.15
    WEIGHT_WHO_CRITICALITY: float = 0.25

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "BLUECHAIN: AI-Powered Ocean Behaviour and Impact Prediction System"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Dual database support: PostgreSQL+PostGIS in production/Docker, SQLite in local dev/tests
    DATABASE_URL: str = "sqlite:///./bluechain.db"
    
    # Ingestion & Data Mode
    USE_SAMPLE_DATA: bool = True
    SAMPLE_DATA_DIR: str = "data/sample"
    
    # External APIs (Optional credentials)
    COPERNICUS_USERNAME: str = ""
    COPERNICUS_PASSWORD: str = ""
    ERDDAP_SERVER: str = "https://coastwatch.pfeg.noaa.gov/erddap"
    
    # ML Models directory
    MODELS_DIR: str = "ml/models"
    
    # Allowed CORS Origins
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

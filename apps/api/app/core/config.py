import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "ResQNet AI"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/resqnet.db")
    
    # Security / Auth
    COORDINATOR_API_KEY: str = os.getenv("COORDINATOR_API_KEY", "resqnet-coordinator-secret-key-2026")
    COORDINATOR_BEARER_TOKEN: str = os.getenv("COORDINATOR_BEARER_TOKEN", "mock-jwt-coordinator-token")
    
    # LLM Settings (optional live key with automated mock/heuristic extractor fallback)
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

settings = Settings()


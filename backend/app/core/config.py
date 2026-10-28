from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "ClauseGuard"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    DATABASE_URL: str = "sqlite:///./clauseguard.db"
    SECRET_KEY: str = "clauseguard_super_secret_jwt_key_change_in_production_min_32_chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    ML_MODE: str = "mock"  # 'mock' or 'real'
    MODEL_DIR: str = "./models"
    UPLOAD_DIR: str = "./data/uploads"
    REPORT_DIR: str = "./data/reports"

    MAX_UPLOAD_MB: int = 20
    MAX_PAGES: int = 60
    CONFIDENCE_THRESHOLD: float = 0.50

    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:8000"

    SEED_ADMIN_EMAIL: str = "admin@clauseguard.local"
    SEED_ADMIN_PASSWORD: str = "AdminSecurePass123!"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORT_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.MODEL_DIR, "classifier"), exist_ok=True)
os.makedirs(os.path.join(settings.MODEL_DIR, "extractor"), exist_ok=True)

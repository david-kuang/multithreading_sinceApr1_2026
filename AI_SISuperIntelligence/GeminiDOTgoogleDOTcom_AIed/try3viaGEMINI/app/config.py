"""
Configuration module using Pydantic Settings.
Automatically loads configuration constants and environment variables.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings class storing configuration constants.
    """
    APP_NAME: str = "AskGemini Web App"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ask-gemini-secure-jwt-key-9876543210")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day expiration

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ask_gemini.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
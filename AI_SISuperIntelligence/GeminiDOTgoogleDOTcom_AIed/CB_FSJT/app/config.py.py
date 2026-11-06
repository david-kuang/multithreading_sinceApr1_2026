"""
Configuration module using Pydantic Settings.
Reads environment variables with fallback defaults.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings class storing configuration constants.
    """
    APP_NAME: str = "ChatGPT Clone"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-key-change-in-production-1234567890")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day token expiration

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./chat_app.db")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "mock-key-for-testing")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
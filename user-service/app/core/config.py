import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# ----------------------------------------------------------------------
# Load environment variables from .env file (in dev mode)
# ----------------------------------------------------------------------
load_dotenv()


# ----------------------------------------------------------------------
# Base Config using Pydantic Settings
# ----------------------------------------------------------------------
class Settings(BaseSettings):
    """
    Centralized configuration for the User Management Service.
    Values are read from environment variables or default fallbacks.
    """

    # --- App Info ---
    PROJECT_NAME: str = "CampusBot User Management Service"
    ENV: str = os.getenv("ENV", "development")  # 'development' or 'production'

    # --- Database ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user_admin:user_pass@user-db:5432/user_db"
    )

    # --- JWT & Auth ---
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretjwtkey")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    # --- Account Security ---
    LOCK_THRESHOLD: int = int(os.getenv("LOCK_THRESHOLD", "5"))  # failed attempts before lock
    LOCK_MINUTES: int = int(os.getenv("LOCK_MINUTES", "15"))     # lockout duration

    # --- Redis (optional, for rate limiting or sessions) ---
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # --- Logging ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # --- Other future configs ---
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8001"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# ----------------------------------------------------------------------
# Global settings instance
# ----------------------------------------------------------------------
settings = Settings()

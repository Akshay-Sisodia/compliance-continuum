import os
from functools import lru_cache
from pydantic import BaseSettings, Field, ValidationError
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

class Settings(BaseSettings):
    ENV: str = Field("development", env="ENV")
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    # Add more fields as needed

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        raise RuntimeError(f"Config validation error: {e}")

# Usage: from config import get_settings; settings = get_settings()

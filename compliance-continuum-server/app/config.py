import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/compliance_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "<your-supabase-url>")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "<your-supabase-service-role-key>")

settings = Settings()

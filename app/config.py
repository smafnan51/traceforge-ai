from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "TraceForge")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./traceforge.db")
    api_key: str = os.getenv("API_KEY", "change-me")


settings = Settings()

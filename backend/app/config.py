from pathlib import Path
import os
from pydantic_settings import BaseSettings

# Look for .env in project root or current working dir
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    LLM_API_KEY: str = ""
    SEARCH_API_KEY: str = ""
    
    class Config:
        env_file = str(ENV_PATH) if ENV_PATH.exists() else ".env"
        extra = "ignore"
        
settings = Settings()


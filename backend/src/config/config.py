
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Vocabulary Learning API"
    DESCRIPTION:str ="API for vocabulary learning application with spaced repetition"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    # Firebase settings
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID")
    DOCS_URL="/docs"
    REDOCS_URL="/redoc"
    
settings = Settings()

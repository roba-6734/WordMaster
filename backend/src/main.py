from datetime import datetime

from firebase_admin import firestore
from fastapi import FastAPI,Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from dotenv import load_dotenv

from src.firebase import db
from src.routes import dictionary
from src.routes import words
from src.routes import progress
from src.routes import quiz
from src.routes import authentication
from src.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    description= settings.DESCRIPTION,
    version= settings.VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOCS_URL,
    debug=settings.DEBUG
   
)
app.add_middleware(
    CORSMiddleware,
    allow_origins =['*'],
    allow_credentials =True,
    allow_methods =["*"],
    allow_headers=["*"]
)

@app.middleware("http" )
async def auth_middleware(request: Request, call_next):
    response = await call_next(request)
    
    return response


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/user/login')


@app.get('/')
def index():
    return {"HomePage":"Welcome to my webapp"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "dictionary_api": "operational",
            "firebase": "operational",
            "spaced_repetition": "operational"
        }
    }


app.include_router(router=authentication.router)
app.include_router(router=dictionary.router)
app.include_router(router=words.router)
app.include_router(router=progress.router)
app.include_router(router=quiz.router)


from datetime import datetime

from firebase_admin import firestore,auth
from fastapi import FastAPI,Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm

from src.utils import create_firebase_user, verify_firebase_token, get_current_user, CustomException

from src.models import UserCreate,UserLogin,UserResponse
from src.firebase import db
from src.config import settings
from src.routes import dictionary
from src.routes import words
from src.routes import progress


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


@app.post('/api/auth/register',
          response_model=UserResponse,
          summary="Register a new user",
          description="Create a new user account with email and password")
async def register_user(user:UserCreate):
    try:
        firebase_user = create_firebase_user(
            email = user.email,
            display_name=user.display_name,
            password=user.password
        )

        user_data = {
                "email": user.email,
                "display_name": user.display_name,
                "created_at": firestore.SERVER_TIMESTAMP,
                "profile_picture":"",
                "lastLogin": firestore.SERVER_TIMESTAMP,
                "stats": {
                    "total_words_added": 0,
                    "total_quizzes_taken": 0,
                    "current_streak": 0
                }
            }
        
        db.collection('users').document(firebase_user.uid).set(user_data)

        return {
            "id": firebase_user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "created_at": datetime.now().isoformat()
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/api/auth/login',
          summary="User login",
          description="Authenticate user and return access token")
async def login(userLogin:UserLogin):
    try:
        user = auth.get_user_by_email(userLogin.email)

        

        db.collection('users').document(user.uid).update({
            'lastLoginAt':firestore.SERVER_TIMESTAMP
        })

        return {
            'access token': user.uid,
            'token type': 'bearer',
            'user_id':user.uid
        }
    
       
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

  

@app.get('/api/auth/user')
async def get_user_info(current_user=Depends(get_current_user)):
    return {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "display_name": current_user.get("display_name"),
        "created_at": current_user.get("created_at")
    }

@app.post('/api/auth/logout')
def logout():
    return {'message':"You have successfully logged out"}



app.include_router(router=dictionary.router)
app.include_router(router=words.router)
app.include_router(router=progress.router)


from firebase_admin import firestore
from fastapi import FastAPI,Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from datetime import datetime

from src.utils.auth_utils import create_firebase_user, verify_firebase_token
from src.utils.exception import CustomException
from src.models.user import UserCreate,UserLogin,UserResponse
from src.firebase.firebase_setup import db


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins =['*'],
    allow_credentials =True,
    allow_methods =["*"],
    allow_headers=["*"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/user/login')

async def get_current_user(token:str = Depends(oauth2_scheme)):
    try:
        payload = verify_firebase_token(token)
        user_id = payload.get('uid')
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        pass
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc:
        raise HTTPException(status_code=404, detail='User not found')
    
    return user_doc.to_dict



@app.get('/')
def index():
    return {"HomePage":"Welcome to my webapp"}


@app.post('/api/auth/register')
async def register_user(user:UserCreate):
    try:
        firebase_user = create_firebase_user(
            email = user.email,
            display_name=user.displayName,
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


@app.post('/api/auth/login')
def login():
    pass

@app.get('/api/auth/user')
def get_user_info():
    pass

@app.post('/api/auth/logout')
def logout():
    pass

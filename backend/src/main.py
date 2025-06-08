from firebase_admin import firestore,auth
from fastapi import FastAPI,Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from datetime import datetime

from src.utils import create_firebase_user, verify_firebase_token
from src.utils import CustomException
from src.models import UserCreate,UserLogin,UserResponse
from src.firebase import db


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
        user_id = token
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user_doc = db.collection('users').document(user_id).get()
    
    if not user_doc:
        raise HTTPException(status_code=404, detail='User not found')
    user_data = user_doc.to_dict()
    user_data['id']=user_id
    return user_data



@app.get('/')
def index():
    return {"HomePage":"Welcome to my webapp"}


@app.post('/api/auth/register')
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


@app.post('/api/auth/login')
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

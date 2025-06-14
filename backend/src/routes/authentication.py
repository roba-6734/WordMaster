from fastapi import FastAPI,HTTPException,status,Depends,APIRouter
from firebase_admin import firestore
from datetime import datetime

from src.firebase import db
from src.utils import create_firebase_user, get_current_user, CustomException,login_user
from src.models import UserCreate,UserLogin,UserResponse

router = APIRouter(prefix='/api/auth',tags=['authentication'])

@router.post('/register', response_model=UserResponse,summary='Register new user')
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
    

@router.post('/login',summary='Login user')
async def login(userLogin:UserLogin):
    try:
        user_data = login_user(userLogin.email,userLogin.password)
        id_token = user_data['idToken']
        decoded_token = await get_current_user(id_token)

        user_id =decoded_token['id']

        
        
        db.collection('users').document(user_id).update({
            'lastLoginAt':firestore.SERVER_TIMESTAMP
        })

        return {
            'access_token': id_token,
            'token_type': 'bearer',
            'user_id':user_id,
            
        }
    
       
    except Exception as e:
        print(f"🔍 Validation Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

@router.get('/user')
async def get_user_info(current_user=Depends(get_current_user)):
    return {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "display_name": current_user.get("display_name"),
        "created_at": current_user.get("created_at")
    }

@router.post('/logout')
def logout():
    return {'message':"You have successfully logged out"}



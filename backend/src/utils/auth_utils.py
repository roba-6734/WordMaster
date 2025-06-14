from email import header
from typing import Optional
from datetime import datetime, timedelta
import os
import requests

from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv


from src.utils.exception import CustomException
from src.firebase import db

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/user/login')
pwd_context =CryptContext(schemes=['bcrypt'],deprecated='auto')

def verify_password(plain_password:str, hashed_password:str)-> bool:
    return pwd_context.verify(plain_password,hashed_password)


def hash_password(plain_password:str) -> str:
    return pwd_context.hash(plain_password)


def create_firebase_user(email,password,display_name):
    try:
        user = auth.create_user(
            email= email,
            password = password,
            display_name = display_name
        )
        return user
    except auth.EmailAlreadyExistsError:
        raise CustomException("Email address is already in use")
    except auth.InvalidPasswordError:
        raise CustomException("Password must be at least 6 characters long")
    except auth.InvalidEmailError:
        raise CustomException("Invalid email format")
    except FirebaseError as e:
        raise CustomException(f"Firebase error: {str(e)}")
    except Exception as e:
        raise CustomException(f"Unexpected error: {str(e)}")

def verify_firebase_token(custom_token):
    try:
        decoded_token = auth.verify_id_token(id_token=custom_token)
        return decoded_token
    except Exception as e:
        raise CustomException(e)
        
def login_user(email, password):
    try:
        firebase_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={os.getenv('FIREBASE_API_KEY')}"
        payload = {
            "email": email,
            "password":password,
            "returnSecureToken": True
        }
        response = requests.post(firebase_url,json=payload)
        if response.status_code !=200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail= "Invalid email or password",
                headers={"www-authenticat":"Bearer"},
            )
        return response.json()
    except Exception as e:
        raise CustomException(e)



async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 🔐 Step 1: Verify the Firebase ID token
        decoded_token =verify_firebase_token(token)
        
        user_id = decoded_token["uid"]

        # 🔍 Step 2: Check if user exists in Firestore
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            raise credentials_exception

        user_data = user_doc.to_dict()
        user_data["id"] = user_id
        return user_data

    except Exception as e:
        print(f"Auth error: {e}")
        raise credentials_exception
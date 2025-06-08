from typing import Optional
import firebase_admin
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from passlib.context import CryptContext
from datetime import datetime, timedelta

from src.utils.exception import CustomException


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
        


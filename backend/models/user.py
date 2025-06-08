
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    email:EmailStr
    displayName:str
    password:str


class UserLogin(BaseModel):
    email:EmailStr
    password:str


class UserResponse(BaseModel):
    id:str
    email:EmailStr
    displayName:str
    createdAt: Optional[str] = None
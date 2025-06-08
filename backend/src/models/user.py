
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    email:EmailStr
    display_name:str
    password:str


class UserLogin(BaseModel):
    email:EmailStr
    password:str


class UserResponse(BaseModel):
    id:str
    email:EmailStr
    display_name:str
    createdAt: Optional[str] = None
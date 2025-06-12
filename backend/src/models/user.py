
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re


class UserCreate(BaseModel):
    email:EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    display_name: str = Field(..., min_length=2, max_length=50)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @validator('display_name')
    def validate_display_name(cls, v):
        if not v.strip():
            raise ValueError('Display name cannot be empty')
        return v.strip()


class UserLogin(BaseModel):
    email:str
    password:str


class UserResponse(BaseModel):
    id:str
    email:EmailStr
    display_name:str
    

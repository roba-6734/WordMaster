from fastapi import APIRouter, Depends, HTTPException, status

from src.utils import get_current_user


router = APIRouter(prefix='/api/quiz',tags=['quiz'])

@router.post('/generate')
def generate_quiz():
    pass

@router.post('/submit')
def submit_quiz():
    pass

@router.get('/types')
def get_quiz_types():
    pass

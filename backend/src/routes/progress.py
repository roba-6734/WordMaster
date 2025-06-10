from fastapi import APIRouter, Depends, HTTPException, status

from src.utils import get_current_user





router = APIRouter(prefix='/api/progress',tags=["progress"])

@router.post('/review')
def review_words(current_user = Depends(get_current_user)):
    pass

@router.get('/due')
def get_words_due_for_review(current_user = Depends(get_current_user)):
    pass

@router.get('/stats')
def get_stats(current_user = Depends(get_current_user)):
    pass


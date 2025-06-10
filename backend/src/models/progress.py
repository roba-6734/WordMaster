
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class ProgressCreate(BaseModel):
    word_id: str
    is_correct: bool
    response_time_ms: Optional[int] = None
    quiz_type : str = Field()


class ProgressResponse(BaseModel):
    id: str
    user_id: str
    word_id:str
    word: str

    strength: int = Field(ge=0,le=6)
    strength_description: str
    next_review_date: str

    total_reviews: int
    correct_reviews: int
    consecutive_correct: int    
    retention_rate: float = Field(ge=0,le=100)

    last_reviewed: Optional[str] = None
    created_at: str
    updated_at: str


class ReviewSessionCreate(BaseModel):
    
    reviews: List[ProgressCreate]


class ReviewSessionResponse(BaseModel):
    """Response after submitting reviews"""
    success: bool
    message: str
    words_reviewed: int
    correct_answers: int
    accuracy: float
    updated_words: List[ProgressResponse]

class LearningStats(BaseModel):
    """User's overall learning statistics"""
    total_words: int
    words_learning: int  # Strength 0-2
    words_strong: int    # Strength 3-5
    words_mastered: int  # Strength 6
    
    due_for_review: int
    overdue_words: int
    
    overall_accuracy: float
    current_streak: int
    longest_streak: int
    
    reviews_today: int
    reviews_this_week: int
    reviews_total: int

class DueWordsResponse(BaseModel):
    """Words that are due for review"""
    words: List[ProgressResponse]
    total_due: int
    overdue_count: int
    new_words_count: int

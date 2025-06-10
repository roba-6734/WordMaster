from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class QuizType(str, Enum):
    MULTIPLE_CHOICE = "mcq"
    FILL_IN_BLANK = "fill_blank"
    MATCHING = "matching"
    DEFINITION_TO_WORD = "def_to_word"
    WORD_TO_DEFINITION = "word_to_def"

class QuizDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    MIXED = "mixed"

class QuizGenerateRequest(BaseModel):
    """Request to generate a new quiz"""
    quiz_type: QuizType
    question_count: int = Field(default=10, ge=1, le=50)
    difficulty: QuizDifficulty = QuizDifficulty.MIXED
    include_new_words: bool = True
    include_review_words: bool = True

class QuizOption(BaseModel):
    """Single option in a multiple choice question"""
    id: str
    text: str
    is_correct: bool

class QuizQuestion(BaseModel):
    """Single quiz question"""
    id: str
    word_id: str
    word: str
    question_type: QuizType
    question_text: str
    options: Optional[List[QuizOption]] = None  # For MCQ
    correct_answer: str
    hint: Optional[str] = None

class QuizResponse(BaseModel):
    """Generated quiz response"""
    quiz_id: str
    quiz_type: QuizType
    difficulty: QuizDifficulty
    questions: List[QuizQuestion]
    total_questions: int
    estimated_time_minutes: int
    created_at: str

class QuizAnswer(BaseModel):
    """User's answer to a quiz question"""
    question_id: str
    word_id: str
    user_answer: str
    time_taken_ms: Optional[int] = None

class QuizSubmission(BaseModel):
    """Complete quiz submission"""
    quiz_id: str
    answers: List[QuizAnswer]
    total_time_ms: Optional[int] = None

class QuizResult(BaseModel):
    """Result for a single question"""
    question_id: str
    word_id: str
    word: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    time_taken_ms: Optional[int] = None

class QuizSubmissionResponse(BaseModel):
    """Response after submitting a quiz"""
    success: bool
    quiz_id: str
    score: int  # Number correct
    total_questions: int
    accuracy: float  # Percentage
    results: List[QuizResult]
    time_taken_ms: Optional[int] = None
    words_learned: int  # Words that improved in strength
    words_to_review: int  # Words that need more practice

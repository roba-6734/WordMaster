from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from firebase_admin import firestore

from src.models import (
    QuizType, QuizDifficulty, QuizGenerateRequest, QuizResponse,
    QuizSubmission, QuizSubmissionResponse, QuizAnswer
)
from src.services import quiz_service
from src.utils import get_current_user
from src.utils import logging
from src.firebase import db


router = APIRouter(prefix="/api/quiz", tags=["quiz"])

@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    quiz_request: QuizGenerateRequest,
    current_user = Depends(get_current_user)
):
    """
    Generate a new quiz based on user's learning progress
    """
    try:
        user_id = current_user["id"]
        
        print(f"🎯 Generating {quiz_request.quiz_type} quiz for user {user_id}")
        print(f"📊 Parameters: {quiz_request.question_count} questions, difficulty: {quiz_request.difficulty}")
        
        # Generate quiz using the quiz service
        quiz = await quiz_service.generate_quiz(
            user_id=user_id,
            quiz_type=quiz_request.quiz_type,
            question_count=quiz_request.question_count,
            difficulty=quiz_request.difficulty,
            include_new_words=quiz_request.include_new_words,
            include_review_words=quiz_request.include_review_words
        )
        
        print(f"✅ Generated quiz {quiz.quiz_id} with {quiz.total_questions} questions")
        
        return quiz
        
    except ValueError as e:
        print(f"⚠️ Quiz generation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        print(f"💥 Error generating quiz: {str(e)}")
        logging.error(f"Error generating quiz: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate quiz. Please try again."
        )

@router.post("/submit", response_model=QuizSubmissionResponse)
async def submit_quiz(
    submission: QuizSubmission,
    current_user = Depends(get_current_user)
):
    """
    Submit quiz answers and update learning progress
    """
    try:
        user_id = current_user["id"]
        
        print(f"📝 Submitting quiz {submission.quiz_id} with {len(submission.answers)} answers")
        
        # Convert Pydantic models to dictionaries for the service
        answers_dict = []
        for answer in submission.answers:
            answers_dict.append({
                "question_id": answer.question_id,
                "word_id": answer.word_id,
                "user_answer": answer.user_answer,
                "time_taken_ms": answer.time_taken_ms
            })
        
        # Submit quiz using the quiz service
        result = await quiz_service.submit_quiz(
            user_id=user_id,
            quiz_id=submission.quiz_id,
            answers=answers_dict,
            total_time_ms=submission.total_time_ms
        )

        db.collection('users').document(user_id).update({
            "stats.total_quizzes_taken":firestore.Increment(1)
        })
        
        print(f"✅ Quiz submitted: {result.score}/{result.total_questions} ({result.accuracy:.1f}%)")
        
        return result
        
    except ValueError as e:
        print(f"⚠️ Quiz submission error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        print(f"💥 Error submitting quiz: {str(e)}")
        logging.error(f"Error submitting quiz: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to submit quiz. Please try again."
        )

@router.get("/types")
async def get_quiz_types():
    """
    Get available quiz types and their descriptions
    """
    return {
        "quiz_types": [
            {
                "type": "mcq",
                "name": "Multiple Choice",
                "description": "Choose the correct definition from multiple options",
                "estimated_time_per_question": 30
            },
            {
                "type": "fill_blank",
                "name": "Fill in the Blank",
                "description": "Complete the sentence with the correct word",
                "estimated_time_per_question": 45
            },
            {
                "type": "word_to_def",
                "name": "Word to Definition",
                "description": "Provide the definition for the given word",
                "estimated_time_per_question": 40
            },
            {
                "type": "def_to_word",
                "name": "Definition to Word",
                "description": "Identify the word from its definition",
                "estimated_time_per_question": 35
            }
        ],
        "difficulties": [
            {
                "level": "easy",
                "description": "Words you know well, longer review intervals"
            },
            {
                "level": "medium", 
                "description": "Mix of familiar and challenging words"
            },
            {
                "level": "hard",
                "description": "Focus on difficult words that need practice"
            },
            {
                "level": "mixed",
                "description": "Adaptive difficulty based on your progress"
            }
        ]
    }

@router.get("/preview/{quiz_type}")
async def preview_quiz(
    quiz_type: QuizType,
    current_user = Depends(get_current_user)
):
    """
    Preview what a quiz would look like without generating a full quiz
    """
    try:
        user_id = current_user["id"]
        
        print(f"👀 Generating quiz preview for {quiz_type}")
        
        # Generate a small preview quiz (3 questions)
        preview_quiz = await quiz_service.generate_quiz(
            user_id=user_id,
            quiz_type=quiz_type,
            question_count=3,
            difficulty=QuizDifficulty.MIXED,
            include_new_words=True,
            include_review_words=True
        )
        
        # Return just the first question as a preview
        if preview_quiz.questions:
            sample_question = preview_quiz.questions[0]
            return {
                "quiz_type": quiz_type,
                "sample_question": {
                    "question_text": sample_question.question_text,
                    "word": sample_question.word,
                    "has_options": sample_question.options is not None,
                    "option_count": len(sample_question.options) if sample_question.options else 0
                },
                "estimated_time": preview_quiz.estimated_time_minutes,
                "available_words": len(preview_quiz.questions)
            }
        else:
            return {
                "quiz_type": quiz_type,
                "message": "No words available for this quiz type",
                "available_words": 0
            }
            
    except Exception as e:
        print(f"💥 Error generating preview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate quiz preview"
        )

@router.get("/history")
async def get_quiz_history(
    limit: int = 20,
    current_user = Depends(get_current_user)
):
    """
    Get user's quiz history and performance
    """
    try:
        user_id = current_user["id"]
        
        print(f"📚 Getting quiz history for user {user_id}")
        
        # Get recent quiz results from Firestore
        quiz_results_query = (db.collection("quiz_results")
                             .where("userId", "==", user_id)
                             .order_by("reviewDate", direction=firestore.Query.DESCENDING)
                             .limit(limit))
        
        quiz_results = list(quiz_results_query.stream())
        
        # Group results by quiz session (same reviewDate)
        quiz_sessions = {}
        
        for result_doc in quiz_results:
            result_data = result_doc.to_dict()
            review_date = result_data.get("reviewDate")
            
            if review_date and hasattr(review_date, 'timestamp'):
                session_key = int(review_date.timestamp() // 300)  # Group by 5-minute intervals
                
                if session_key not in quiz_sessions:
                    quiz_sessions[session_key] = {
                        "date": datetime.fromtimestamp(review_date.timestamp()).isoformat(),
                        "questions": [],
                        "total_questions": 0,
                        "correct_answers": 0,
                        "quiz_type": result_data.get("quizType", "unknown")
                    }
                
                quiz_sessions[session_key]["questions"].append({
                    "word_id": result_data.get("wordId"),
                    "is_correct": result_data.get("isCorrect", False),
                    "strength_before": result_data.get("strengthBefore", 0),
                    "strength_after": result_data.get("strengthAfter", 0)
                })
                
                quiz_sessions[session_key]["total_questions"] += 1
                if result_data.get("isCorrect"):
                    quiz_sessions[session_key]["correct_answers"] += 1
        
        # Convert to list and calculate accuracy
        history = []
        for session_data in quiz_sessions.values():
            accuracy = (session_data["correct_answers"] / session_data["total_questions"] * 100) if session_data["total_questions"] > 0 else 0
            
            history.append({
                "date": session_data["date"],
                "quiz_type": session_data["quiz_type"],
                "total_questions": session_data["total_questions"],
                "correct_answers": session_data["correct_answers"],
                "accuracy": round(accuracy, 1),
                "words_improved": len([q for q in session_data["questions"] if q["strength_after"] > q["strength_before"]])
            })
        
        # Sort by date (most recent first)
        history.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "quiz_history": history[:limit],
            "total_sessions": len(history)
        }
        
    except Exception as e:
        print(f"💥 Error getting quiz history: {str(e)}")
        logging.error(f"Error getting quiz history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get quiz history"
        )

@router.delete("/{quiz_id}")
async def cancel_quiz(
    quiz_id: str,
    current_user = Depends(get_current_user)
):
    """
    Cancel an active quiz (remove from memory)
    """
    try:
        user_id = current_user["id"]
        
        # Check if quiz exists and belongs to user
        if quiz_id in quiz_service.active_quizzes:
            quiz_data = quiz_service.active_quizzes[quiz_id]
            
            if quiz_data["user_id"] == user_id:
                del quiz_service.active_quizzes[quiz_id]
                return {"success": True, "message": "Quiz cancelled successfully"}
            else:
                raise HTTPException(status_code=403, detail="Quiz does not belong to user")
        else:
            raise HTTPException(status_code=404, detail="Quiz not found")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Error cancelling quiz: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel quiz"
        )

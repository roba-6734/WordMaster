from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime

from src.models import (
    ProgressCreate,
    ProgressResponse, 
    ReviewSessionCreate,
    ReviewSessionResponse,
    LearningStats,
    DueWordsResponse
)
from src.services import progress_service, learning_service
from src.firebase import db
from src.utils import get_current_user
from src.utils import logging

router = APIRouter(prefix="/api/progress", tags=["progress"])

@router.post("/review", response_model=ProgressResponse)
async def record_review(
    review_data: ProgressCreate,
    current_user = Depends(get_current_user)
):
    """
    Record a single word review and update progress
    """
    try:
        user_id = current_user["id"]
        
        print(f"📝 Recording review for word {review_data.word_id}")
        
        # Update progress using the spaced repetition algorithm
        updated_progress = await progress_service.update_progress(
            user_id=user_id,
            word_id=review_data.word_id,
            is_correct=review_data.is_correct,
            quiz_type=review_data.quiz_type,
            response_time_ms=review_data.response_time_ms
        )
        
        # Get word details for response
        word_doc = db.collection("words").document(review_data.word_id).get()
        word_data = word_doc.to_dict() if word_doc.exists else {}
        
        # Handle timestamp conversion
        next_review = updated_progress.get("nextReviewDate")
        if next_review and hasattr(next_review, 'timestamp'):
            next_review_str = datetime.fromtimestamp(next_review.timestamp()).isoformat()
        else:
            next_review_str = datetime.now().isoformat()
        
        last_reviewed = updated_progress.get("lastReviewed")
        if last_reviewed and hasattr(last_reviewed, 'timestamp'):
            last_reviewed_str = datetime.fromtimestamp(last_reviewed.timestamp()).isoformat()
        else:
            last_reviewed_str = datetime.now().isoformat()
        
        created_at = updated_progress.get("createdAt")
        if created_at and hasattr(created_at, 'timestamp'):
            created_at_str = datetime.fromtimestamp(created_at.timestamp()).isoformat()
        else:
            created_at_str = datetime.now().isoformat()
        
        # Calculate retention rate
        total_reviews = updated_progress.get("totalReviews", 0)
        correct_reviews = updated_progress.get("correctReviews", 0)
        retention_rate = learning_service.calculate_retention_score(correct_reviews, total_reviews)
        
        # Get strength description
        strength = updated_progress.get("strength", 0)
        strength_description = learning_service.get_strength_description(strength)
        
        response = ProgressResponse(
            id=updated_progress["id"],
            user_id=user_id,
            word_id=review_data.word_id,
            word=word_data.get("word", ""),
            strength=strength,
            strength_description=strength_description,
            next_review_date=next_review_str,
            total_reviews=total_reviews,
            correct_reviews=correct_reviews,
            consecutive_correct=updated_progress.get("consecutiveCorrect", 0),
            retention_rate=retention_rate,
            last_reviewed=last_reviewed_str,
            created_at=created_at_str,
            updated_at=last_reviewed_str
        )
        
        print(f"✅ Review recorded. New strength: {strength} ({strength_description})")
        
        return response
        
    except Exception as e:
        print(f"💥 Error recording review: {str(e)}")
        logging.error(f"Error recording review: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to record review. Please try again."
        )

@router.post("/review-session", response_model=ReviewSessionResponse)
async def record_review_session(
    session_data: ReviewSessionCreate,
    current_user = Depends(get_current_user)
):
    """
    Record multiple word reviews in a single session (for quiz results)
    """
    try:
        user_id = current_user["id"]
        
        print(f"📚 Recording review session with {len(session_data.reviews)} reviews")
        
        updated_words = []
        correct_count = 0
        
        for review in session_data.reviews:
            # Record each review
            updated_progress = await progress_service.update_progress(
                user_id=user_id,
                word_id=review.word_id,
                is_correct=review.is_correct,
                quiz_type=review.quiz_type,
                response_time_ms=review.response_time_ms
            )
            
            if review.is_correct:
                correct_count += 1
            
            # Get word details
            word_doc = db.collection("words").document(review.word_id).get()
            word_data = word_doc.to_dict() if word_doc.exists else {}
            
            # Convert to response format (similar to single review above)
            # ... (timestamp conversion code similar to above)
            
            # Add to updated words list
            # updated_words.append(progress_response)
        
        # Calculate session statistics
        total_reviews = len(session_data.reviews)
        accuracy = (correct_count / total_reviews * 100) if total_reviews > 0 else 0
        
        return ReviewSessionResponse(
            success=True,
            message=f"Recorded {total_reviews} reviews with {accuracy:.1f}% accuracy",
            words_reviewed=total_reviews,
            correct_answers=correct_count,
            accuracy=accuracy,
            updated_words=updated_words
        )
        
    except Exception as e:
        print(f"💥 Error recording review session: {str(e)}")
        logging.error(f"Error recording review session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to record review session. Please try again."
        )

@router.get("/due", response_model=DueWordsResponse)
async def get_due_words(
    limit: int = 20,
    current_user = Depends(get_current_user)
):
    """
    Get words that are due for review based on spaced repetition algorithm
    """
    try:
        user_id = current_user["id"]
        
        print(f"📅 Getting due words for user {user_id}")
        
        # Get due words from progress service
        due_words_data = await progress_service.get_due_words(user_id, limit)
        
        print(f"📊 Found {len(due_words_data)} due words")
        
        # Convert to response format
        due_words = []
        overdue_count = 0
        new_words_count = 0
        
        now = datetime.now()
        
        for word_data in due_words_data:
            # Handle timestamp conversion
            next_review = word_data.get("nextReviewDate")
            if next_review and hasattr(next_review, 'timestamp'):
                next_review_dt = datetime.fromtimestamp(next_review.timestamp())
                next_review_str = next_review_dt.isoformat()
                
                # Check if overdue
                if next_review_dt < now:
                    overdue_count += 1
            else:
                next_review_str = datetime.now().isoformat()
            
            # Check if new word
            strength = word_data.get("strength", 0)
            if strength == 0:
                new_words_count += 1
            
            # Calculate retention rate
            total_reviews = word_data.get("totalReviews", 0)
            correct_reviews = word_data.get("correctReviews", 0)
            retention_rate = learning_service.calculate_retention_score(correct_reviews, total_reviews)
            
            # Get strength description
            strength_description = learning_service.get_word_strength_description(strength)
            
            # Handle other timestamps
            last_reviewed = word_data.get("lastReviewed")
            if last_reviewed and hasattr(last_reviewed, 'timestamp'):
                last_reviewed_str = datetime.fromtimestamp(last_reviewed.timestamp()).isoformat()
            else:
                last_reviewed_str = None
            
            created_at = word_data.get("createdAt")
            if created_at and hasattr(created_at, 'timestamp'):
                created_at_str = datetime.fromtimestamp(created_at.timestamp()).isoformat()
            else:
                created_at_str = datetime.now().isoformat()
            
            progress_response = ProgressResponse(
                id=word_data["progress_id"],
                user_id=user_id,
                word_id=word_data["word_id"],
                word=word_data.get("word", ""),
                strength=strength,
                strength_description=strength_description,
                next_review_date=next_review_str,
                total_reviews=total_reviews,
                correct_reviews=correct_reviews,
                consecutive_correct=word_data.get("consecutiveCorrect", 0),
                retention_rate=retention_rate,
                last_reviewed=last_reviewed_str,
                created_at=created_at_str,
                updated_at=last_reviewed_str or created_at_str
            )
            
            due_words.append(progress_response)
        
        return DueWordsResponse(
            words=due_words,
            total_due=len(due_words),
            overdue_count=overdue_count,
            new_words_count=new_words_count
        )
        
    except Exception as e:
        print(f"💥 Error getting due words: {str(e)}")
        logging.error(f"Error getting due words: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get due words. Please try again."
        )

@router.get("/stats", response_model=LearningStats)
async def get_learning_stats(
    current_user = Depends(get_current_user)
):
    """
    Get comprehensive learning statistics for the user
    """
    try:
        user_id = current_user["id"]
        
        print(f"📈 Getting learning stats for user {user_id}")
        
        # Get stats from progress service
        stats_data = await progress_service.get_learning_stats(user_id)
        
        # Get user's current and longest streak from user document
        user_doc = db.collection("users").document(user_id).get()
        user_data = user_doc.to_dict() if user_doc.exists else {}
        user_stats = user_data.get("stats", {})
        
        stats = LearningStats(
            total_words=stats_data["total_words"],
            words_learning=stats_data["words_learning"],
            words_strong=stats_data["words_strong"],
            words_mastered=stats_data["words_mastered"],
            due_for_review=stats_data["due_for_review"],
            overdue_words=stats_data["overdue_words"],
            overall_accuracy=stats_data["overall_accuracy"],
            current_streak=user_stats.get("currentStreak", 0),
            longest_streak=user_stats.get("longestStreak", 0),
            reviews_today=stats_data["reviews_today"],
            reviews_this_week=stats_data["reviews_this_week"],
            reviews_total=stats_data["reviews_total"]
        )
        
        print(f"📊 Stats: {stats.total_words} words, {stats.due_for_review} due")
        
        return stats
        
    except Exception as e:
        print(f"💥 Error getting learning stats: {str(e)}")
        logging.error(f"Error getting learning stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get learning statistics. Please try again."
        )

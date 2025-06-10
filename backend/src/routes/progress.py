from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Dict, Any
from datetime import datetime,timedelta

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
    
@router.get("/analytics", response_model=Dict[str, Any])
async def get_learning_analytics(
    days: int = 30,
    current_user = Depends(get_current_user)
):
    """
    Get detailed learning analytics and insights
    """
    try:
        user_id = current_user["id"]
        
        print(f"📊 Getting learning analytics for user {user_id} (last {days} days)")
        
        # Get basic stats
        basic_stats = await progress_service.get_learning_stats(user_id)
        
        # Get performance trends
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get quiz results for trend analysis
        quiz_results_query = (db.collection("quiz_results")
                             .where("userId", "==", user_id)
                             .where("reviewDate", ">=", start_date)
                             .order_by("reviewDate"))
        
        quiz_results = list(quiz_results_query.stream())
        
        # Analyze performance trends
        daily_performance = {}
        quiz_type_performance = {}
        word_difficulty_analysis = {}
        
        for result_doc in quiz_results:
            result_data = result_doc.to_dict()
            review_date = result_data.get("reviewDate")
            
            if review_date and hasattr(review_date, 'timestamp'):
                date_str = datetime.fromtimestamp(review_date.timestamp()).strftime("%Y-%m-%d")
                quiz_type = result_data.get("quizType", "unknown")
                is_correct = result_data.get("isCorrect", False)
                strength_before = result_data.get("strengthBefore", 0)
                
                # Daily performance
                if date_str not in daily_performance:
                    daily_performance[date_str] = {"correct": 0, "total": 0}
                
                daily_performance[date_str]["total"] += 1
                if is_correct:
                    daily_performance[date_str]["correct"] += 1
                
                # Quiz type performance
                if quiz_type not in quiz_type_performance:
                    quiz_type_performance[quiz_type] = {"correct": 0, "total": 0}
                
                quiz_type_performance[quiz_type]["total"] += 1
                if is_correct:
                    quiz_type_performance[quiz_type]["correct"] += 1
                
                # Word difficulty analysis
                difficulty_level = "easy" if strength_before >= 4 else "medium" if strength_before >= 2 else "hard"
                
                if difficulty_level not in word_difficulty_analysis:
                    word_difficulty_analysis[difficulty_level] = {"correct": 0, "total": 0}
                
                word_difficulty_analysis[difficulty_level]["total"] += 1
                if is_correct:
                    word_difficulty_analysis[difficulty_level]["correct"] += 1
        
        # Calculate trends
        performance_trend = []
        for date_str, perf in sorted(daily_performance.items()):
            accuracy = (perf["correct"] / perf["total"] * 100) if perf["total"] > 0 else 0
            performance_trend.append({
                "date": date_str,
                "accuracy": round(accuracy, 1),
                "questions_answered": perf["total"]
            })
        
                # Generate insights (FIXED VERSION)
        insights = []

        # Get overall accuracy safely
        overall_accuracy = basic_stats.get("overall_accuracy", 0)

        # Overall performance insight
        if overall_accuracy >= 80:
            insights.append("🎉 Excellent! You're maintaining high accuracy across your vocabulary.")
        elif overall_accuracy >= 60:
            insights.append("👍 Good progress! Keep practicing to improve your accuracy.")
        else:
            insights.append("💪 Focus on reviewing words more frequently to improve retention.")

        # Quiz type insights
        best_quiz_type = max(quiz_type_performance.items(), key=lambda x: x[1]["correct"]/max(x[1]["total"], 1)) if quiz_type_performance else None
        if best_quiz_type:
            accuracy = best_quiz_type[1]["correct"] / best_quiz_type[1]["total"] * 100
            insights.append(f"🎯 You perform best with {best_quiz_type[0]} quizzes ({accuracy:.1f}% accuracy).")

        # Difficulty insights
        if "hard" in word_difficulty_analysis:
            hard_accuracy = word_difficulty_analysis["hard"]["correct"] / word_difficulty_analysis["hard"]["total"] * 100
            if hard_accuracy < 50:
                insights.append("📚 Consider reviewing difficult words more frequently.")

        # Streak insights (SAFELY handle missing current_streak)
        current_streak = basic_stats.get("current_streak", 0)
        if current_streak >= 7:
            insights.append(f"🔥 Amazing {current_streak}-day streak! Keep it up!")
        elif current_streak >= 3:
            insights.append(f"⭐ Great {current_streak}-day streak! You're building a good habit.")
        elif current_streak == 0:
            insights.append("🎯 Start a learning streak by practicing daily!")

        return {
            "basic_stats": basic_stats,
            "performance_trend": performance_trend[-14:],  # Last 14 days
            "quiz_type_performance": {
                quiz_type: {
                    "accuracy": round(perf["correct"] / perf["total"] * 100, 1) if perf["total"] > 0 else 0,
                    "total_questions": perf["total"]
                }
                for quiz_type, perf in quiz_type_performance.items()
            },
            "difficulty_analysis": {
                level: {
                    "accuracy": round(perf["correct"] / perf["total"] * 100, 1) if perf["total"] > 0 else 0,
                    "total_questions": perf["total"]
                }
                for level, perf in word_difficulty_analysis.items()
            },
            "insights": insights,
            "recommendations": [
                f"Review {basic_stats.get('due_for_review', 0)} words due today",
                f"Focus on {basic_stats.get('words_learning', 0)} words still being learned",
                "Take a quiz to practice your vocabulary" if basic_stats.get("due_for_review", 0) > 0 else "Add more words to expand your vocabulary"
            ]
        }

        
    except Exception as e:
        print(f"💥 Error getting analytics: {str(e)}")
        logging.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get learning analytics"
        )


from datetime import datetime, timedelta,timezone
from typing import List,Optional,Dict,Any
from firebase_admin import firestore


from src.services import learning_service
from src.firebase import db
from src.utils import logging


class ProgressService:
    """Service for managing user learning progress"""
    
    async def get_or_create_progress(self, user_id: str, word_id: str) -> Dict[str, Any]:
        """Get existing progress or create new progress entry for a word"""
        
        # Check if progress already exists
        progress_query = db.collection("progress").filter(
            "userId", "==", user_id,
            "wordId", "==", word_id
        )
        existing_progress = list(progress_query.stream())

        
        if existing_progress:
            # Return existing progress
            doc = existing_progress[0]
            return {"id": doc.id, **doc.to_dict()}
        
        # Create new progress entry
        new_progress = {
            "userId": user_id,
            "wordId": word_id,
            "strength": 0,  # New word
            "totalReviews": 0,
            "correctReviews": 0,
            "consecutiveCorrect": 0,
            "nextReviewDate": datetime.now(),  # Available for immediate review
            "lastReviewed": None,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection("progress").add(new_progress)
        progress_id = doc_ref[1].id
        
        return {"id": progress_id, **new_progress}
    
    async def update_progress(
        self, 
        user_id: str, 
        word_id: str, 
        is_correct: bool,
        quiz_type: str,
        response_time_ms: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update word progress based on review result"""
        
        # Get current progress
        progress = await self.get_or_create_progress(user_id, word_id)
        progress_id = progress["id"]
        
        # Get word difficulty level
        word_doc = db.collection("words").document(word_id).get()
        word_data = word_doc.to_dict() if word_doc.exists else {}
        difficulty_level = word_data.get("difficultyLevel")
        
        # Calculate new strength and next review date
        current_strength = progress.get("strength", 0)
        consecutive_correct = progress.get("consecutiveCorrect", 0)
        
        next_review_date, new_strength = learning_service.calculate_next_review(
            current_strength=current_strength,
            is_correct=is_correct,
            difficulty_level=difficulty_level,
            consecutive_correct=consecutive_correct if is_correct else 0
        )
        
        # Update counters
        new_total_reviews = progress.get("totalReviews", 0) + 1
        new_correct_reviews = progress.get("correctReviews", 0) + (1 if is_correct else 0)
        new_consecutive_correct = (consecutive_correct + 1) if is_correct else 0
        
        # Prepare update data
        update_data = {
            "strength": new_strength,
            "totalReviews": new_total_reviews,
            "correctReviews": new_correct_reviews,
            "consecutiveCorrect": new_consecutive_correct,
            "nextReviewDate": next_review_date,
            "lastReviewed": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }




        db.collection("progress").document(progress_id).update(update_data)
        
        # Record this review in quiz_results collection
        quiz_result = {
            "userId": user_id,
            "wordId": word_id,
            "isCorrect": is_correct,
            "quizType": quiz_type,
            "responseTimeMs": response_time_ms,
            "strengthBefore": current_strength,
            "strengthAfter": new_strength,
            "reviewDate": firestore.SERVER_TIMESTAMP
        }
        db.collection("quiz_results").add(quiz_result)
        
        # Update user stats
        await self._update_user_stats(user_id, is_correct)
        
        # Return updated progress
        updated_progress = {**progress, **update_data}
        updated_progress["id"] = progress_id
        return updated_progress
        
    async def get_due_words(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get words that are due for review"""
        
        now = datetime.now()
        print("we are inside due word function")
        # Get all progress for user where next review is due
        progress_query = (db.collection("progress")
                        .where("userId", "==", user_id)
                        .where("nextReviewDate", "<=", now)
                        .order_by("nextReviewDate")
                        .limit(limit))
        
        progress_docs = list(progress_query.stream())
        
        # Get word details for each progress entry
        due_words = []
        for progress_doc in progress_docs:
            progress_data = progress_doc.to_dict()
            word_id = progress_data["wordId"]
            
            # Get word details
            word_doc = db.collection("words").document(word_id).get()
            if word_doc.exists:
                word_data = word_doc.to_dict()
                
                # Combine progress and word data
                combined_data = {
                    "progress_id": progress_doc.id,
                    "word_id": word_id,
                    "word": word_data.get("word", ""),
                    "definitions": word_data.get("definitions", []),
                    "phonetics": word_data.get("phonetics", []),
                    "synonyms": word_data.get("synonyms", []),
                    "antonyms": word_data.get("antonyms", []),
                    "user_notes": word_data.get("userNotes"),
                    **progress_data
                }
                due_words.append(combined_data)
        
        return due_words
    
    async def get_learning_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""    
        try:
            # Get user's progress entries
            progress_query = db.collection("progress").where("userId", "==", user_id)
            progress_docs = list(progress_query.stream())
            
            # Get user document for streak info
            user_doc = db.collection("users").document(user_id).get()
            user_data = user_doc.to_dict() if user_doc.exists else {}
            user_stats = user_data.get("stats", {})
            
            # Initialize stats
            stats = {
                "total_words_added": len(progress_docs),
                "words_learning": 0,  # strength 1-3
                "words_strong": 0,    # strength 4-5  
                "words_mastered": 0,  # strength 6+
                "due_for_review": 0,
                "overdue_words": 0,
                "overall_accuracy": 0,
                "current_streak": user_stats.get("currentStreak", 0),  # ← ADD THIS
                "longest_streak": user_stats.get("longestStreak", 0),   # ← ADD THIS
                "reviews_today": 0,
                "reviews_this_week": 0,
                "reviews_total": 0
            }
            
            # Rest of your existing logic...
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)
            
            total_reviews = 0
            correct_reviews = 0
            
            for doc in progress_docs:
                data = doc.to_dict()
                strength = data.get("strength", 0)
                next_review = data.get("nextReviewDate")
                total_word_reviews = data.get("totalReviews", 0)
                correct_word_reviews = data.get("correctReviews", 0)
                
                # Categorize by strength
                if strength <= 1:
                    stats["words_learning"] += 1
                elif strength <= 3:
                    stats["words_learning"] += 1
                elif strength <= 5:
                    stats["words_strong"] += 1
                else:
                    stats["words_mastered"] += 1
                
                # Check if due for review
                if next_review:
                    if hasattr(next_review, 'timestamp'):
                        next_review_dt = datetime.fromtimestamp(next_review.timestamp())
                        if next_review_dt <= now:
                            stats["due_for_review"] += 1
                            if next_review_dt < today_start:
                                stats["overdue_words"] += 1
                
                # Add to totals
                total_reviews += total_word_reviews
                correct_reviews += correct_word_reviews
            
            # Calculate overall accuracy
            if total_reviews > 0:
                stats["overall_accuracy"] = round((correct_reviews / total_reviews) * 100, 1)
            
            # Get recent review activity
           
            quiz_results_query = (db.collection('quiz_results').filter(
                "userId", "==", user_id,
                "reviewDate", ">=", today_start
            ))
            
            today_results = list(quiz_results_query.stream())
            stats["reviews_today"] = len(today_results)
            
            # Get week activity  
            week_results_query = (db.collection("quiz_results")
                                .where("userId", "==", user_id)
                                .where("reviewDate", ">=", week_start))
            
            week_results = list(week_results_query.stream())
            stats["reviews_this_week"] = len(week_results)
            stats["reviews_total"] = total_reviews
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting learning stats: {str(e)}")
            # Return default stats if error
            return {
                "total_words": 0,
                "words_learning": 0,
                "words_strong": 0,
                "words_mastered": 0,
                "due_for_review": 0,
                "overdue_words": 0,
                "overall_accuracy": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "reviews_today": 0,
                "reviews_this_week": 0,
                "reviews_total": 0
            }

    
    async def _update_user_stats(self, user_id: str, is_correct: bool):
        """Update user's overall statistics"""
        
        user_ref = db.collection("users").document(user_id)
        
        # Update quiz count
        user_ref.update({
            "stats.totalQuizzesTaken": firestore.Increment(1)
        })
        
        # Update streak if correct
        if is_correct:
            # This is simplified - in a real app you'd track daily streaks
            user_ref.update({
                "stats.currentStreak": firestore.Increment(1)
            })

# Create global instance
progress_service = ProgressService()
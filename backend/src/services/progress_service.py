from datetime import datetime, timedelta
from typing import List,Optional,Dict,Any
from firebase_admin import firestore

from src.services import learning_service
from src.firebase import db


class ProgressService:
    """Service for managing user learning progress"""
    
    async def get_or_create_progress(self, user_id: str, word_id: str) -> Dict[str, Any]:
        """Get existing progress or create new progress entry for a word"""
        
        # Check if progress already exists
        progress_query = db.collection("progress").where("userId", "==", user_id).where("wordId", "==", word_id)
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
        """Get comprehensive learning statistics for user"""
        
        # Get all progress for user
        progress_query = db.collection("progress").where("userId", "==", user_id)
        progress_docs = list(progress_query.stream())
        
        # Initialize counters
        stats = {
            "total_words": len(progress_docs),
            "words_learning": 0,  # Strength 0-2
            "words_strong": 0,    # Strength 3-5
            "words_mastered": 0,  # Strength 6
            "due_for_review": 0,
            "overdue_words": 0,
            "overall_accuracy": 0.0,
            "reviews_today": 0,
            "reviews_this_week": 0,
            "reviews_total": 0
        }
        
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        
        total_reviews = 0
        total_correct = 0
        
        for doc in progress_docs:
            data = doc.to_dict()
            strength = data.get("strength", 0)
            next_review = data.get("nextReviewDate", now)
            
            # Categorize by strength
            if strength <= 2:
                stats["words_learning"] += 1
            elif strength <= 5:
                stats["words_strong"] += 1
            else:
                stats["words_mastered"] += 1
            
            # Check if due for review
            if next_review <= now:
                stats["due_for_review"] += 1
                if next_review < today_start:
                    stats["overdue_words"] += 1
            
            # Add to accuracy calculation
            word_total = data.get("totalReviews", 0)
            word_correct = data.get("correctReviews", 0)
            total_reviews += word_total
            total_correct += word_correct
        
        # Calculate overall accuracy
        if total_reviews > 0:
            stats["overall_accuracy"] = (total_correct / total_reviews) * 100
        
        # Get recent quiz results for time-based stats
        recent_results = (db.collection("quiz_results")
                        .where("userId", "==", user_id)
                        .where("reviewDate", ">=", week_start)
                        .stream())
        
        for result in recent_results:
            result_data = result.to_dict()
            review_date = result_data.get("reviewDate")
            
            if review_date:
                if hasattr(review_date, 'timestamp'):
                    review_datetime = datetime.fromtimestamp(review_date.timestamp())
                else:
                    continue
                
                stats["reviews_total"] += 1
                
                if review_datetime >= today_start:
                    stats["reviews_today"] += 1
                
                if review_datetime >= week_start:
                    stats["reviews_this_week"] += 1
        
        return stats
    
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
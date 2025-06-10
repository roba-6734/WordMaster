import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from src.models import (
    QuizType, QuizDifficulty, QuizQuestion, QuizOption, 
    QuizResponse, QuizResult, QuizSubmissionResponse
)
from src.services import progress_service
from src.firebase import db

class QuizService:
    """Service for generating and managing quizzes"""
    
    def __init__(self):
        self.active_quizzes = {}  # Store active quizzes in memory
        
    async def generate_quiz(
        self, 
        user_id: str, 
        quiz_type: QuizType,
        question_count: int = 10,
        difficulty: QuizDifficulty = QuizDifficulty.MIXED,
        include_new_words: bool = True,
        include_review_words: bool = True
    ) -> QuizResponse:
        """Generate a new quiz for the user"""
        
        print(f"🎯 Generating {quiz_type} quiz with {question_count} questions")
        
        # Get candidate words for the quiz
        candidate_words = await self._get_candidate_words(
            user_id, question_count * 2, include_new_words, include_review_words
        )
        
        if len(candidate_words) < question_count:
            # Not enough words, adjust question count
            question_count = len(candidate_words)
            if question_count == 0:
                raise ValueError("No words available for quiz generation")
        
        # Select words for quiz based on spaced repetition priority
        selected_words = self._select_quiz_words(candidate_words, question_count)
        
        # Generate questions based on quiz type
        questions = []
        for i, word_data in enumerate(selected_words):
            question = await self._generate_question(word_data, quiz_type, i)
            questions.append(question)
        
        # Create quiz
        quiz_id = str(uuid.uuid4())
        quiz = QuizResponse(
            quiz_id=quiz_id,
            quiz_type=quiz_type,
            difficulty=difficulty,
            questions=questions,
            total_questions=len(questions),
            estimated_time_minutes=self._estimate_quiz_time(len(questions), quiz_type),
            created_at=datetime.now().isoformat()
        )
        
        # Store quiz in memory for validation during submission
        self.active_quizzes[quiz_id] = {
            "quiz": quiz,
            "user_id": user_id,
            "created_at": datetime.now(),
            "word_ids": [q.word_id for q in questions]
        }
        
        print(f"✅ Generated quiz {quiz_id} with {len(questions)} questions")
        return quiz
    
    async def submit_quiz(
        self, 
        user_id: str, 
        quiz_id: str, 
        answers: List[Dict[str, Any]],
        total_time_ms: Optional[int] = None
    ) -> QuizSubmissionResponse:
        """Submit quiz answers and update progress"""
        
        print(f"📝 Submitting quiz {quiz_id} with {len(answers)} answers")
        
        # Validate quiz exists and belongs to user
        if quiz_id not in self.active_quizzes:
            raise ValueError("Quiz not found or expired")
        
        quiz_data = self.active_quizzes[quiz_id]
        if quiz_data["user_id"] != user_id:
            raise ValueError("Quiz does not belong to user")
        
        quiz = quiz_data["quiz"]
        
        # Process each answer
        results = []
        correct_count = 0
        words_learned = 0
        words_to_review = 0
        
        for answer in answers:
            question_id = answer["question_id"]
            word_id = answer["word_id"]
            user_answer = answer["user_answer"]
            time_taken = answer.get("time_taken_ms")
            
            # Find the corresponding question
            question = next((q for q in quiz.questions if q.id == question_id), None)
            if not question:
                continue
            
            # Check if answer is correct
            is_correct = self._check_answer(question, user_answer)
            if is_correct:
                correct_count += 1
            
            # Update word progress using spaced repetition
            old_progress = await progress_service.get_or_create_progress(user_id, word_id)
            old_strength = old_progress.get("strength", 0)
            
            updated_progress = await progress_service.update_progress(
                user_id=user_id,
                word_id=word_id,
                is_correct=is_correct,
                quiz_type=quiz.quiz_type.value,
                response_time_ms=time_taken
            )
            
            new_strength = updated_progress.get("strength", 0)
            
            # Track learning progress
            if new_strength > old_strength:
                words_learned += 1
            elif new_strength < old_strength:
                words_to_review += 1
            
            # Create result
            result = QuizResult(
                question_id=question_id,
                word_id=word_id,
                word=question.word,
                user_answer=user_answer,
                correct_answer=question.correct_answer,
                is_correct=is_correct,
                time_taken_ms=time_taken
            )
            results.append(result)
        
        # Calculate final score
        total_questions = len(answers)
        accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Clean up quiz from memory
        del self.active_quizzes[quiz_id]
        
        response = QuizSubmissionResponse(
            success=True,
            quiz_id=quiz_id,
            score=correct_count,
            total_questions=total_questions,
            accuracy=accuracy,
            results=results,
            time_taken_ms=total_time_ms,
            words_learned=words_learned,
            words_to_review=words_to_review
        )
        
        print(f"✅ Quiz submitted: {correct_count}/{total_questions} ({accuracy:.1f}%)")
        return response
    
    async def _get_candidate_words(
        self, 
        user_id: str, 
        limit: int,
        include_new: bool,
        include_review: bool
    ) -> List[Dict[str, Any]]:
        """Get words that can be used for quiz generation"""
        
        candidate_words = []
        
        if include_review:
            # Get due words (highest priority)
            due_words = await progress_service.get_due_words(user_id, limit)
            candidate_words.extend(due_words)
        
        if include_new and len(candidate_words) < limit:
            # Get words that haven't been reviewed yet
            remaining_limit = limit - len(candidate_words)
            
            # Get user's words that don't have progress entries (new words)
            user_words_query = db.collection("words").where("userId", "==", user_id).limit(remaining_limit * 2)
            user_words = list(user_words_query.stream())
            
            for word_doc in user_words:
                word_data = word_doc.to_dict()
                word_id = word_doc.id
                
                # Check if this word has progress
                progress_query = db.collection("progress").where("userId", "==", user_id).where("wordId", "==", word_id)
                has_progress = len(list(progress_query.stream())) > 0
                
                if not has_progress:
                    # This is a new word
                    word_data["word_id"] = word_id
                    word_data["progress_id"] = None
                    word_data["strength"] = 0
                    word_data["totalReviews"] = 0
                    candidate_words.append(word_data)
                    
                    if len(candidate_words) >= limit:
                        break
        
        return candidate_words[:limit]
    
    def _select_quiz_words(self, candidate_words: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        """Select words for quiz based on learning priority"""
        
        # Sort by priority (due words first, then by strength)
        def priority_score(word):
            strength = word.get("strength", 0)
            next_review = word.get("nextReviewDate")
            
            if next_review:
                # Due words get higher priority
                if hasattr(next_review, 'timestamp'):
                    next_review_dt = datetime.fromtimestamp(next_review.timestamp())
                else:
                    next_review_dt = datetime.now()
                
                if next_review_dt <= datetime.now():
                    return -strength  # Lower strength = higher priority for due words
            
            return strength * 10  # Not due words get lower priority
        
        sorted_words = sorted(candidate_words, key=priority_score)
        return sorted_words[:count]
    
    async def _generate_question(
        self, 
        word_data: Dict[str, Any], 
        quiz_type: QuizType, 
        question_index: int
    ) -> QuizQuestion:
        """Generate a single quiz question"""
        
        word = word_data.get("word", "")
        word_id = word_data.get("word_id", "")
        definitions = word_data.get("definitions", [])
        
        if not definitions:
            # Fallback if no definitions
            definitions = [{"definition": "No definition available", "partOfSpeech": "unknown"}]
        
        main_definition = definitions[0]["definition"]
        
        question_id = f"q_{question_index}_{word_id}"
        
        if quiz_type == QuizType.MULTIPLE_CHOICE:
            return await self._generate_mcq_question(question_id, word, word_id, main_definition)
        elif quiz_type == QuizType.FILL_IN_BLANK:
            return self._generate_fill_blank_question(question_id, word, word_id, main_definition)
        elif quiz_type == QuizType.WORD_TO_DEFINITION:
            return self._generate_word_to_def_question(question_id, word, word_id, main_definition)
        else:
            # Default to MCQ
            return await self._generate_mcq_question(question_id, word, word_id, main_definition)
    
    async def _generate_mcq_question(
        self, 
        question_id: str, 
        word: str, 
        word_id: str, 
        correct_definition: str
    ) -> QuizQuestion:
        """Generate multiple choice question"""
        
        # Get wrong answers from other words
        wrong_definitions = await self._get_wrong_definitions(word_id, 3)
        
        # Create options
        options = [
            QuizOption(id="a", text=correct_definition, is_correct=True)
        ]
        
        option_ids = ["b", "c", "d"]
        for i, wrong_def in enumerate(wrong_definitions):
            if i < len(option_ids):
                options.append(QuizOption(
                    id=option_ids[i], 
                    text=wrong_def, 
                    is_correct=False
                ))
        
        # Shuffle options
        random.shuffle(options)
        
        return QuizQuestion(
            id=question_id,
            word_id=word_id,
            word=word,
            question_type=QuizType.MULTIPLE_CHOICE,
            question_text=f"What is the definition of '{word}'?",
            options=options,
            correct_answer=correct_definition
        )
    
    def _generate_fill_blank_question(
        self, 
        question_id: str, 
        word: str, 
        word_id: str, 
        definition: str
    ) -> QuizQuestion:
        """Generate fill in the blank question"""
        
        # Create a sentence with the word blanked out
        question_text = f"Fill in the blank: '{definition}' is the definition of ______."
        
        return QuizQuestion(
            id=question_id,
            word_id=word_id,
            word=word,
            question_type=QuizType.FILL_IN_BLANK,
            question_text=question_text,
            options=None,
            correct_answer=word.lower()
        )
    
    def _generate_word_to_def_question(
        self, 
        question_id: str, 
        word: str, 
        word_id: str, 
        definition: str
    ) -> QuizQuestion:
        """Generate word to definition question"""
        
        return QuizQuestion(
            id=question_id,
            word_id=word_id,
            word=word,
            question_type=QuizType.WORD_TO_DEFINITION,
            question_text=f"What does '{word}' mean?",
            options=None,
            correct_answer=definition
        )
    
    async def _get_wrong_definitions(self, exclude_word_id: str, count: int) -> List[str]:
        """Get wrong definitions for MCQ distractors"""
        
        # Get random definitions from other words
        words_query = db.collection("words").limit(count * 3)
        words = list(words_query.stream())
        
        wrong_definitions = []
        for word_doc in words:
            if word_doc.id == exclude_word_id:
                continue
                
            word_data = word_doc.to_dict()
            definitions = word_data.get("definitions", [])
            
            if definitions:
                wrong_definitions.append(definitions[0]["definition"])
                
            if len(wrong_definitions) >= count:
                break
        
        # Pad with generic definitions if needed
        while len(wrong_definitions) < count:
            wrong_definitions.append("A common English word")
        
        return wrong_definitions[:count]
    
    def _check_answer(self, question: QuizQuestion, user_answer: str) -> bool:
        """Check if user's answer is correct"""
        
        if question.question_type == QuizType.MULTIPLE_CHOICE:
            # For MCQ, check if the selected option is correct
            correct_option = next((opt for opt in question.options if opt.is_correct), None)
            return correct_option and user_answer.lower() == correct_option.text.lower()
        
        elif question.question_type == QuizType.FILL_IN_BLANK:
            # For fill in blank, check if answer matches the word (case insensitive)
            return user_answer.lower().strip() == question.correct_answer.lower().strip()
        
        else:
            # For other types, do basic string matching
            return user_answer.lower().strip() in question.correct_answer.lower()
    
    def _estimate_quiz_time(self, question_count: int, quiz_type: QuizType) -> int:
        """Estimate time needed for quiz in minutes"""
        
        time_per_question = {
            QuizType.MULTIPLE_CHOICE: 30,  # 30 seconds per question
            QuizType.FILL_IN_BLANK: 45,   # 45 seconds per question
            QuizType.MATCHING: 60,        # 60 seconds per question
            QuizType.WORD_TO_DEFINITION: 40,
            QuizType.DEFINITION_TO_WORD: 35
        }
        
        seconds_per_question = time_per_question.get(quiz_type, 40)
        total_seconds = question_count * seconds_per_question
        return max(1, total_seconds // 60)  # Convert to minutes, minimum 1

# Create global instance
quiz_service = QuizService()

import math
import random
from typing import Optional, List, Tuple, Dict
from datetime import datetime, timedelta

from firebase_admin import firestore
from numpy import diff


class SpacedRepetitionSevice:

    def __init__(self):
        self.base_intervals = {
            0: 1,      # New word - review tomorrow
            1: 2,      # Weak - review in 2 days  
            2: 4,      # Learning - review in 4 days
            3: 8,      # Good - review in 8 days
            4: 16,     # Strong - review in 16 days
            5: 32,     # Very strong - review in 32 days
            6: 64      # Mastered - review in 64 days
        }

        self.difficulty_multipliers = {
            "easy": 1.2,        # 20% longer intervals
            "intermediate": 1.0, # Normal intervals
            "hard": 0.8         # 20% shorter intervals
        }

    def calculate_next_review(self,
                            current_strength: int,
                            is_correct: bool,
                            difficulty_level: Optional[str]=None, 
                            consecutive_correct: int =0) -> Tuple[datetime, int]:
        
        if is_correct:
            new_strength = max(1+current_strength,6)
            bonus_multiplier = 1 + (consecutive_correct*0.1)
            
        else:
            new_strength = max(0, current_strength-2)
            bonus_multiplier =1

        base_days = self.base_intervals[new_strength]
        difficulty_multiplier = self.difficulty_multipliers.get(difficulty_level,1)

        final_days = base_days * difficulty_multiplier * bonus_multiplier

        randomness = random.uniform(0.8,1.2)
        final_days *=randomness

        next_review = datetime.now() + timedelta(days=final_days)

        return next_review, new_strength
    
    def get_strength_description(self,strength: int) -> str:
        descriptions = {
            0: "New",
            1: "Learning", 
            2: "Familiar",
            3: "Good",
            4: "Strong",
            5: "Very Strong",
            6: "Mastered"
        }
        return descriptions.get(strength, "Unknown")

    def calculate_retention_score(self,correct_count: int, total_review: int) -> float:
        
        if total_review ==0:
            return 0
        else:
            return (correct_count/total_review)*100
        
    def should_review_word(self, next_review_date: datetime) -> bool:

        return datetime.now() >= next_review_date
    
    def get_review_priority(self, next_review_date: datetime, strength: int) -> int:

        now = datetime.now()

        if next_review_date <=now:
            days_overdue = (now - next_review_date).days
            return (strength * 10) - days_overdue
        else:
            return 1000 + strength

learning_service = SpacedRepetitionSevice()

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class ProgressCreate(BaseModel):
    word_id: str
    is_correct: bool
    response_time_ms: Optional[int] = None
    quiz_type : str = Field()





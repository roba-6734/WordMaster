from typing import Optional, List

from pydantic import BaseModel, Field


class PhoneticModel(BaseModel):
    text: str 
    audio: Optional[str] =""


class DefinitionModel(BaseModel):
    partOfSpeech: str
    definition: str
    example: Optional[str] =""


class DictionaryResponse(BaseModel):
    word: str
    phonetic: Optional[str] = ""
    phonetics: List[PhoneticModel] = []
    definitions: List[DefinitionModel] = []
    synonyms: List[str] = []
    antonyms: List[str] = []
    source: str


class WordLookupResponse(BaseModel):
    success: bool
    data: Optional[DictionaryResponse] = None
    message: str


class WordCreate(BaseModel):
    """Model for new word creation."""
    word: str = Field(min_length=1,max_length=100)
    user_notes: Optional[str] = Field(None, max_length=500)
    source: Optional[str] = Field(default="manual") 
    source_url: Optional[str] = Field(None)  


class WordUpdate(BaseModel):
    """Model for updating an existing word"""
    user_notes: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = Field(None)
    is_favorite: Optional[bool] = Field(None)
    difficulty_level: Optional[str] = Field(None, regex="^(easy|intermediate|hard)$")


class WordResponse(BaseModel):
    """Model for word responses"""
    id: str
    user_id: str
    word: str
    added_at: str  
    source: str
    source_url: Optional[str] = None
    
    
    definitions: List[DefinitionModel]
    phonetics: List[PhoneticModel] = []
    synonyms: List[str] = []
    antonyms: List[str] = []
    
    
    user_notes: Optional[str] = None
    is_favorite: bool = False
    difficulty_level: Optional[str] = None


class WordListResponse(BaseModel):
    """Model for paginated word list"""
    words: List[WordResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

class WordCreateResponse(BaseModel):
    """Response when creating a word"""
    success: bool
    message: str
    data: Optional[WordResponse] = None


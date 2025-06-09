from typing import Optional, List

from pydantic import BaseModel


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


    

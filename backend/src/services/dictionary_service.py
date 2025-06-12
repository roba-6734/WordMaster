from typing import List, Dict, Optional, Any
import asyncio

from fastapi import HTTPException
import httpx

from src.utils import logging


class DictionaryService:
    def __init__(self ):
        self.base_url = "https://api.dictionaryapi.dev/api/v2/entries/en"
        self.timeout = 1000

    async def lookup_word(self, word: str ) -> Optional[Dict[str,Any]] :
        try:
            async with httpx.AsyncClient(timeout=self.timeout ) as client:
                url = f"{self.base_url}/{word.lower()}"
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    formatted_data = self._format_word_data(data[0])
                    return formatted_data
                elif response.status_code == 404:
                    logging.info(f"The word: {word} is not found in the dictionary")
                    return None
                else:
                    logging.info(f"Dictionary API Error: {response.status_code}")
                    return None
        except httpx.TimeoutException:
            logging.error(f"Dictionary API timeout for word: {word}")
            return None
        except Exception as e:
            logging.error(f"Dictionary API error for word '{word}': {str(e)}")
            return None
    
    def _format_word_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            word = raw_data.get("word", "")
            main_phonetic = ""
            phonetics = []
            for p in raw_data.get("phonetics", []):
                phonetic_text = p.get("text", "")
                phonetic_audio = p.get("audio", "")
                if phonetic_text or phonetic_audio:
                    phonetics.append({
                        "text": phonetic_text,
                        "audio": phonetic_audio
                    })
                    if phonetic_text and not main_phonetic:
                        main_phonetic = phonetic_text
            definitions = []
            synonyms = set()
            antonyms = set()
            for meaning in raw_data.get("meanings", []):
                part_of_speech = meaning.get("partOfSpeech", "")
                synonyms.update(meaning.get("synonyms", []))
                antonyms.update(meaning.get("antonyms", []))
                for definition in meaning.get("definitions", []):
                    def_data = {
                        "partOfSpeech": part_of_speech,
                        "definition": definition.get("definition", ""),
                        "example": definition.get("example", "")
                    }
                    definitions.append(def_data)
                    synonyms.update(definition.get("synonyms", []))
                    antonyms.update(definition.get("antonyms", []))
            result = {
                "word": word,
                "phonetic": main_phonetic,
                "phonetics": phonetics,
                "definitions": definitions,
                "synonyms": list(synonyms)[:5],  
                "antonyms": list(antonyms)[:5],   
                "source": "dictionaryapi.dev"
            }
            return result
        except Exception as e:
            logging.error(f"Error formatting word data: {str(e)}")
            return {
                "word": raw_data.get("word", ""),
                "phonetic": "",
                "definitions": [{"definition": "Definition unavailable", "partOfSpeech": "unknown", "example": ""}],
                "phonetics": [],
                "synonyms": [],
                "antonyms": [],
                "source": "dictionaryapi.dev"
            }


dictionary_service = DictionaryService()

from fastapi import APIRouter, HTTPException, Depends

from src.models import WordLookupResponse, DictionaryResponse
from src.services import dictionary_service
from src.main import get_current_user


router = APIRouter(prefix='/api/dictionary', tags=['dictionary'])


@router.get('/lookup/{word}',response_model=WordLookupResponse)
async def lookup_word(word: str, current_user = Depends(get_current_user)):
    if not word or len(word.strip()) == 0:
        raise HTTPException(status_code=400, detail="Word cannot be empty")
    
    clean_word = word.strip().lower()
    word_data = dictionary_service.lookup_word(clean_word)

    if word_data:
        return WordLookupResponse(
            success= True,
            data= DictionaryResponse(**word_data),
            message="Word found successfully"
        )
    else:
        return WordLookupResponse(
            success= False,
            data = None,
            message=f"The word: {word} is not found in the dictionary"
        )
    


@router.get("/test/{word}")
async def test_lookup(word: str):
    """
    Test endpoint (no authentication required) for testing dictionary API
    """
    word_data = await dictionary_service.lookup_word(word)
    return {"word": word, "found": word_data is not None, "data": word_data}
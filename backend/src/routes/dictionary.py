from fastapi import APIRouter, HTTPException, Depends

from src.models import WordLookupResponse, DictionaryResponse
from src.services import dictionary_service
from src.utils import get_current_user


router = APIRouter(prefix='/api/dictionary', tags=['dictionary'])


@router.get('/lookup/{word}',response_model=WordLookupResponse)
async def lookup_word(word: str, current_user = Depends(get_current_user)):
    if not word or len(word.strip()) == 0:
        raise HTTPException(status_code=400, detail="Word cannot be empty")
    
    clean_word = word.strip().lower()
    word_data = await dictionary_service.lookup_word(clean_word)

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

@router.get("/debug/{word}")
async def debug_lookup(word: str):
    """
    Debug endpoint to see what's happening with the API call
    """
    import httpx
    
    try:
        async with httpx.AsyncClient(timeout=10.0 ) as client:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower( )}"
            print(f"Making request to: {url}")
            
            response = await client.get(url)
            
            print(f"Status code: {response.status_code}")
            print(f"Response text: {response.text}")
            
            return {
                "url": url,
                "status_code": response.status_code,
                "response_text": response.text,
                "response_json": response.json() if response.status_code == 200 else None
            }
    except Exception as e:
        return {"error": str(e)}

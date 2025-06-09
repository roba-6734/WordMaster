from curses.ascii import HT
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, status
from firebase_admin import firestore

from src.models import (
    WordCreate,
    WordCreateResponse,
    WordListResponse,
    WordLookupResponse,
    WordResponse,
    WordUpdate
)
from src.services import dictionary_service
from src.firebase import db
from src.utils import get_current_user
from src.utils import logging


router = APIRouter(prefix='/api/words',tags=["words"])


@router.post("/", response_model=WordCreateResponse)
async def add_word(word_data: WordCreate, current_user = Depends(get_current_user)):
    try:
        user_id = current_user['id']
        word_text = word_data.word.strip().lower()
        existing_words = db.collection("words").where("userId", "==", user_id).where("word", "==", word_text).stream()
        if any(existing_words):
            raise HTTPException(
                status_code=400, 
                detail=f"Word '{word_text}' already exists in your vocabulary"
            )
        dictionary_data = await dictionary_service.lookup_word(word_text)
        if not dictionary_data:
            raise HTTPException(
                status_code=404,
                detail=f"Word '{word_text}' not found in dictionary. Please check spelling."
            )
        word_doc = {
            "userId": user_id,
            "word": word_text,
            "addedAt": firestore.SERVER_TIMESTAMP,
            "source": word_data.source,
            "sourceUrl": word_data.source_url,
            
            # Dictionary data
            "definitions": dictionary_data["definitions"],
            "phonetics": dictionary_data["phonetics"],
            "synonyms": dictionary_data["synonyms"],
            "antonyms": dictionary_data["antonyms"],
            
            # User data
            "userNotes": word_data.user_notes,
            "isFavorite": False,
            "difficultyLevel": None
        }
        doc_ref = db.collection("words").add(word_doc)
        word_id = doc_ref[1].id
        user_ref = db.collection("users").document(user_id)
        user_ref.update({
            "stats.totalWordsAdded": firestore.Increment(1)
        })
        response_data = WordResponse(
            id=word_id,
            user_id=user_id,
            word=word_text,
            added_at=datetime.now().isoformat(),
            source=word_data.source,
            source_url=word_data.source_url,
            definitions=dictionary_data["definitions"],
            phonetics=dictionary_data["phonetics"],
            synonyms=dictionary_data["synonyms"],
            antonyms=dictionary_data["antonyms"],
            user_notes=word_data.user_notes,
            is_favorite=False,
            difficulty_level=None
        )
        logging.info("Word Added successfully")
        return WordCreateResponse(
            success=True,
            message=f"Word '{word_text}' added successfully to your vocabulary",
            data=response_data
        )

        
    except HTTPException:
        logging.error(f"word: {word_text} already exists")
        raise HTTPException(
                status_code=400, 
                detail=f"Word '{word_text}' already exists in your vocabulary"
            )
    except Exception as e:
        logging.error("Error while trying to add the word {}".format(e))
        
        raise HTTPException(
            status_code=500,
            detail="Failed to add word. Please try again."
        )
       

@router.get("/", response_model=WordListResponse)
async def get_word(
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    current_user = Depends(get_current_user)):

    try:
        user_id = current_user["id"]
        
        
        
       
        query = db.collection("words").where("userId", "==", user_id)
        
        
        if search:
            search_term = search.strip().lower()
            query = query.where("word", ">=", search_term).where("word", "<=", search_term + "\uf8ff")
        
        
        query = query.order_by("addedAt", direction=firestore.Query.DESCENDING)
        
        
        total_docs = list(query.stream())
        total = len(total_docs)
        
        
        offset = (page - 1) * per_page
        has_next = offset + per_page < total
        has_prev = page > 1
        
       
        paginated_docs = total_docs[offset:offset + per_page]
        
        
        words = []
        for doc in paginated_docs:
            doc_data = doc.to_dict()
            word_response = WordResponse(
                id=doc.id,
                user_id=doc_data["userId"],
                word=doc_data["word"],
                added_at=doc_data["addedAt"].isoformat() if doc_data.get("addedAt") else datetime.now().isoformat(),
                source=doc_data.get("source", "manual"),
                source_url=doc_data.get("sourceUrl"),
                definitions=doc_data.get("definitions", []),
                phonetics=doc_data.get("phonetics", []),
                synonyms=doc_data.get("synonyms", []),
                antonyms=doc_data.get("antonyms", []),
                user_notes=doc_data.get("userNotes"),
                is_favorite=doc_data.get("isFavorite", False),
                difficulty_level=doc_data.get("difficultyLevel")
            )
            words.append(word_response)
        
        return WordListResponse(
            words=words,
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )
    except Exception as e:
        logging.info(f"💥 Error getting words: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve words. Please try again."
        )


@router.get("/{word_id}", response_model=WordResponse)
async def get_word(word_id: str, current_user = Depends(get_current_user)):
    try:
        user_id = current_user['id']

        doc = db.collection('words').document(word_id).get()
        if not doc.exists:
            raise HTTPException(
                status_code=404, detail="Word not found"
            )
        doc_data = doc.to_dict()

        if doc_data['user_id'] == user_id:
            raise HTTPException(status_code=403, detail="Access Denied")
        word_response = WordResponse(
            id=doc.id,
            user_id=doc_data["userId"],
            word=doc_data["word"],
            added_at=doc_data["addedAt"].isoformat() if doc_data.get("addedAt") else datetime.now().isoformat(),
            source=doc_data.get("source", "manual"),
            source_url=doc_data.get("sourceUrl"),
            definitions=doc_data.get("definitions", []),
            phonetics=doc_data.get("phonetics", []),
            synonyms=doc_data.get("synonyms", []),
            antonyms=doc_data.get("antonyms", []),
            user_notes=doc_data.get("userNotes"),
            is_favorite=doc_data.get("isFavorite", False),
            difficulty_level=doc_data.get("difficultyLevel")
        )
        
        return word_response

    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Error getting word: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve word. Please try again."
        )
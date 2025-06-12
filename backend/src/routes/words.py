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
            "stats.total_words_added": firestore.Increment(1)
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
async def get_words(
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
        try:
            docs_without_order = list(query.stream())
        except Exception as e:
            raise e
        try:
            query = query.order_by("addedAt", direction=firestore.Query.DESCENDING)
            total_docs = list(query.stream())
            total = len(total_docs)
        except Exception as e:
            total_docs = docs_without_order
            total = len(total_docs)
        offset = (page - 1) * per_page
        has_next = offset + per_page < total
        has_prev = page > 1
        paginated_docs = total_docs[offset:offset + per_page]
        words = []
        for i, doc in enumerate(paginated_docs):
            try:
                doc_data = doc.to_dict()
                added_at = doc_data.get("addedAt")
                if added_at and hasattr(added_at, 'timestamp'):
                    added_at_str = datetime.fromtimestamp(added_at.timestamp()).isoformat()
                else:
                    added_at_str = datetime.now().isoformat()
                word_response = WordResponse(
                    id=doc.id,
                    user_id=doc_data.get("userId", user_id),
                    word=doc_data.get("word", ""),
                    added_at=added_at_str,
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
            except Exception as e:
                import traceback
                traceback.print_exc()
                continue
        result = WordListResponse(
            words=words,
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"Error getting words: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve words: {str(e)}"
        )


@router.get("/{word_id}", response_model=WordResponse)
async def get_specific_word(word_id: str, current_user = Depends(get_current_user)):  # ← Changed function name
    try:
        user_id = current_user['id']

        doc = db.collection('words').document(word_id).get()
        if not doc.exists:
            raise HTTPException(
                status_code=404, detail="Word not found"
            )
        doc_data = doc.to_dict()

        # ← FIX: Correct field name and logic
        if doc_data.get('userId') != user_id:  # Use 'userId' and != (not ==)
            raise HTTPException(status_code=403, detail="Access Denied")
        
        # ← FIX: Handle Firestore timestamp properly
        added_at = doc_data.get("addedAt")
        if added_at and hasattr(added_at, 'timestamp'):
            added_at_str = datetime.fromtimestamp(added_at.timestamp()).isoformat()
        else:
            added_at_str = datetime.now().isoformat()
        
        word_response = WordResponse(
            id=doc.id,
            user_id=doc_data["userId"],
            word=doc_data["word"],
            added_at=added_at_str,  # ← FIX: Use the properly converted timestamp
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
        logging.error(f"💥 Error getting word: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve word. Please try again."
        )

@router.put("/{word_id}", response_model=WordResponse)
async def update_word(
    word_id: str,
    word_update: WordUpdate,
    current_user = Depends(get_current_user)
):
    """
    Update a word's user-specific data (notes, favorite status, difficulty)
    """
    try:
        user_id = current_user["id"]
        
        # Get the word document
        doc_ref = db.collection("words").document(word_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Word not found")
        
        doc_data = doc.to_dict()
        
        # Check ownership
        if doc_data.get("userId") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Prepare update data (only update fields that are provided)
        update_data = {}
        
        if word_update.user_notes is not None:
            update_data["userNotes"] = word_update.user_notes
            
        if word_update.is_favorite is not None:
            update_data["isFavorite"] = word_update.is_favorite
            
        if word_update.difficulty_level is not None:
            update_data["difficultyLevel"] = word_update.difficulty_level
        
        # Add update timestamp
        update_data["updatedAt"] = firestore.SERVER_TIMESTAMP
        
        # Update the document
        doc_ref.update(update_data)
        
        # Get updated document
        updated_doc = doc_ref.get()
        updated_data = updated_doc.to_dict()
        
        # Handle timestamp
        added_at = updated_data.get("addedAt")
        if added_at and hasattr(added_at, 'timestamp'):
            added_at_str = datetime.fromtimestamp(added_at.timestamp()).isoformat()
        else:
            added_at_str = datetime.now().isoformat()
        
        # Return updated word
        word_response = WordResponse(
            id=updated_doc.id,
            user_id=updated_data["userId"],
            word=updated_data["word"],
            added_at=added_at_str,
            source=updated_data.get("source", "manual"),
            source_url=updated_data.get("sourceUrl"),
            definitions=updated_data.get("definitions", []),
            phonetics=updated_data.get("phonetics", []),
            synonyms=updated_data.get("synonyms", []),
            antonyms=updated_data.get("antonyms", []),
            user_notes=updated_data.get("userNotes"),
            is_favorite=updated_data.get("isFavorite", False),
            difficulty_level=updated_data.get("difficultyLevel")
        )
        
        return word_response
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating word: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update word. Please try again."
        )

@router.delete("/{word_id}")
async def delete_word(
    word_id: str,
    current_user = Depends(get_current_user)
):
    """
    Delete a word from user's collection
    """
    try:
        user_id = current_user["id"]
        
        # Get the word document
        doc_ref = db.collection("words").document(word_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Word not found")
        
        doc_data = doc.to_dict()
        
        # Check ownership
        if doc_data.get("userId") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        word_text = doc_data.get("word", "unknown")
        
        # Delete the document
        doc_ref.delete()
        
        # Update user stats
        user_ref = db.collection("users").document(user_id)
        user_ref.update({
            "stats.totalWordsAdded": firestore.Increment(-1)
        })
        
        return {
            "success": True,
            "message": f"Word '{word_text}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting word: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete word. Please try again."
        )

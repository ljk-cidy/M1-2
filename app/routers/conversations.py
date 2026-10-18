"""Persist and restore complete conversations."""

from fastapi import APIRouter, Depends, HTTPException

from app.config import get_db
from app.models import ConversationCreate

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", status_code=201)
def save_conversation(conv: ConversationCreate, db=Depends(get_db)):
    doc = db.collection("conversations").document()
    payload = conv.model_dump()
    doc.set(payload)
    return {"id": doc.id, **payload}


@router.get("")
def list_conversations(db=Depends(get_db)):
    """The list includes messages; the detail endpoint also returns them."""
    return [
        {**doc.to_dict(), "id": doc.id}
        for doc in db.collection("conversations").stream()
    ]


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str, db=Depends(get_db)):
    doc = db.collection("conversations").document(conversation_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {**doc.to_dict(), "id": doc.id}


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db=Depends(get_db)):
    doc = db.collection("conversations").document(conversation_id)
    if not doc.get().exists:
        raise HTTPException(status_code=404, detail="Conversation not found")
    doc.delete()
    return {"message": "Conversation deleted"}

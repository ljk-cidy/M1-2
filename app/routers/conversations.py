from fastapi import APIRouter, HTTPException
from app.config import db
from app.models import ConversationCreate

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.post("", status_code=201)
def save_conversation(conv: ConversationCreate):
    doc_ref = db.collection("conversations").document()
    doc_data = conv.dict()
    doc_ref.set(doc_data)
    return {"id": doc_ref.id, **doc_data}

@router.get("")
def list_conversations():
    docs = db.collection("conversations").stream()
    result = []
    for doc in docs:
        d = doc.to_dict()
        result.append({
            "id": doc.id,
            "title": d.get("title", "대화 기록"),
            "messages": d.get("messages", [])
        })
    return result

@router.get("/{id}")
def get_conversation(id: str):
    doc = db.collection("conversations").document(id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"id": doc.id, **doc.to_dict()}

@router.delete("/{id}")
def delete_conversation(id: str):
    doc_ref = db.collection("conversations").document(id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Conversation not found")
    doc_ref.delete()
    return {"message": "Conversation deleted"}
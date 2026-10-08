from fastapi import APIRouter, HTTPException
from app.config import db
from app.models import DataItemCreate, DataItemUpdate
from app.services.analyzer import calculate_summary

router = APIRouter(prefix="/api/data", tags=["data"])

@router.post("", status_code=201)
def create_data(item: DataItemCreate):
    doc_ref = db.collection("data").document()
    doc_data = item.dict()
    doc_ref.set(doc_data)
    return {"id": doc_ref.id, **doc_data}

@router.get("")
def get_all_data():
    docs = db.collection("data").stream()
    result = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        result.append(d)
    return sorted(result, key=lambda x: x.get("date", ""))

@router.put("/{id}")
def update_data(id: str, item: DataItemUpdate):
    doc_ref = db.collection("data").document(id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Data not found")
    
    update_dict = {k: v for k, v in item.dict().items() if v is not None}
    doc_ref.update(update_dict)
    return {"id": id, **doc_ref.get().to_dict()}

@router.delete("/{id}")
def delete_data(id: str):
    doc_ref = db.collection("data").document(id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Data not found")
    doc_ref.delete()
    return {"message": f"Item {id} deleted successfully"}

@router.get("/summary")
def get_data_summary():
    docs = db.collection("data").stream()
    data_list = [doc.to_dict() for doc in docs]
    return calculate_summary(data_list)
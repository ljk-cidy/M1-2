"""Firestore CRUD and summary endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.config import get_db
from app.models import DataItemCreate, DataItemResponse, DataItemUpdate
from app.services.analyzer import calculate_summary

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("", status_code=201, response_model=DataItemResponse)
def create_data(item: DataItemCreate, db=Depends(get_db)):
    doc = db.collection("data").document()
    payload = item.model_dump(mode="json")
    doc.set(payload)
    return {"id": doc.id, **payload}


@router.get("", response_model=list[DataItemResponse])
def get_all_data(db=Depends(get_db)):
    items = [
        {**doc.to_dict(), "id": doc.id}
        for doc in db.collection("data").stream()
    ]
    return sorted(items, key=lambda item: (item["date"], item["id"]))


@router.get("/summary")
def get_data_summary(db=Depends(get_db)):
    return calculate_summary(
        [doc.to_dict() for doc in db.collection("data").stream()]
    )


@router.put("/{item_id}", response_model=DataItemResponse)
def update_data(item_id: str, item: DataItemUpdate, db=Depends(get_db)):
    doc = db.collection("data").document(item_id)
    if not doc.get().exists:
        raise HTTPException(status_code=404, detail="Data not found")
    doc.update(item.model_dump(mode="json", exclude_unset=True))
    return {**doc.get().to_dict(), "id": item_id}


@router.delete("/{item_id}")
def delete_data(item_id: str, db=Depends(get_db)):
    doc = db.collection("data").document(item_id)
    if not doc.get().exists:
        raise HTTPException(status_code=404, detail="Data not found")
    doc.delete()
    return {"message": "Data deleted"}

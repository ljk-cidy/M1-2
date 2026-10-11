from pydantic import BaseModel, Field
from typing import List, Optional

class DataItemCreate(BaseModel):
    date: str = Field(..., example="2026-10-01")
    value: float = Field(..., example="4.5")
    memo: str = Field(..., example="FastAPI CRUD 개발")

class DataItemUpdate(BaseModel):
    date: Optional[str] = None
    value: Optional[float] = None
    memo: Optional[str] = None

class DataItemResponse(DataItemCreate):
    id: str

class Message(BaseModel):
    role: str  # "user" 또는 "assistant"
    content: str

class ConversationCreate(BaseModel):
    title: str
    messages: List[Message]

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
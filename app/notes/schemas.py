import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class NoteBase(BaseModel):
    image_url: str
    title: Optional[str] = "Batch Entry"
    raw_text: Optional[str] = None
    refined_text: Optional[str] = None
    batch_id: Optional[uuid.UUID] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None

class NoteResponse(NoteBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class BatchResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    combined_text: Optional[str] = None
    pdf_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    notes: list[NoteResponse] = []

    model_config = ConfigDict(from_attributes=True)

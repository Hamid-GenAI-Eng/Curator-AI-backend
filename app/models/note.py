import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Note(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    batch_id: Optional[uuid.UUID] = None
    image_url: str
    title: Optional[str] = "Batch Entry"
    raw_text: Optional[str] = None
    refined_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

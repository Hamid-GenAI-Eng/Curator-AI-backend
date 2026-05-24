import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Batch(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    name: str = "Untitled Project"
    description: Optional[str] = None
    combined_text: Optional[str] = None
    pdf_url: Optional[str] = None
    status: str = "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

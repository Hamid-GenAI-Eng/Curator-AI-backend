import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: str
    full_name: str
    hashed_password: Optional[str] = None
    google_id: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

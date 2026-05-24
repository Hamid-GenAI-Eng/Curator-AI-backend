import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Auth schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)

class UserResetPasswordRequest(BaseModel):
    email: EmailStr

class UserResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class GoogleAuth(BaseModel):
    id_token: str

# User response schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    is_verified: bool = False

class UserResponse(UserBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

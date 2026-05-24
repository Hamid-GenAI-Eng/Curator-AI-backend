import httpx
from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.models.user import User
from app.auth.schemas import UserSignup, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token, create_password_reset_token, verify_password_reset_token
from app.core.email import send_reset_password_email
from app.core.config import settings

async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[User]:
    doc = await db.users.find_one({"email": email})
    if doc:
        doc["id"] = doc.pop("_id")
        return User(**doc)
    return None

async def create_user(db: AsyncIOMotorDatabase, user_in: UserSignup) -> User:
    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    
    db_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )
    user_dict = db_user.model_dump()
    user_dict["_id"] = user_dict.pop("id")
    await db.users.insert_one(user_dict)
    return db_user

async def authenticate_user(db: AsyncIOMotorDatabase, login_data: UserLogin) -> Optional[User]:
    user = await get_user_by_email(db, login_data.email)
    if not user or not user.hashed_password:
        return None
    if not verify_password(login_data.password, user.hashed_password):
        return None
    return user

async def process_google_login(db: AsyncIOMotorDatabase, id_token: str) -> User:
    # Verify Google token (server-side verification)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )
        
        google_data = response.json()
        email = google_data.get("email")
        google_id = google_data.get("sub")
        full_name = google_data.get("name", "")

        user = await get_user_by_email(db, email)
        
        if user:
            # Link Google account if not already linked
            if not user.google_id:
                await db.users.update_one(
                    {"_id": user.id}, 
                    {"$set": {"google_id": google_id, "updated_at": datetime.utcnow()}}
                )
                user.google_id = google_id
        else:
            # Create new user via Google
            user = User(
                email=email,
                full_name=full_name,
                google_id=google_id,
                is_active=True,
                is_verified=True # Google emails are verified
            )
            user_dict = user.model_dump()
            user_dict["_id"] = user_dict.pop("id")
            await db.users.insert_one(user_dict)
            
        return user

async def request_password_reset(db: AsyncIOMotorDatabase, email: str) -> None:
    user = await get_user_by_email(db, email)
    if user:
        token = create_password_reset_token(email)
        send_reset_password_email(email, token)

async def reset_password(db: AsyncIOMotorDatabase, token: str, new_password: str) -> bool:
    email = verify_password_reset_token(token)
    if not email:
        return False
    
    user = await get_user_by_email(db, email)
    if not user:
        return False
    
    new_hash = get_password_hash(new_password)
    await db.users.update_one(
        {"_id": user.id},
        {"$set": {"hashed_password": new_hash, "updated_at": datetime.utcnow()}}
    )
    return True

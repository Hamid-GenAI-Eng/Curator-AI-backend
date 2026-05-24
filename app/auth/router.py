from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.auth import schemas, service

router = APIRouter()

@router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: schemas.UserSignup, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Create a new user.
    """
    return await service.create_user(db, user_in)

@router.post("/login", response_model=schemas.Token)
async def login(login_data: schemas.UserLogin, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    OAuth2 compatible token login, retrieve an access token for future requests.
    """
    user = await service.authenticate_user(db, login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(user.email, expires_delta=access_token_expires),
        "token_type": "bearer",
    }

@router.post("/google", response_model=schemas.Token)
async def google_login(google_auth: schemas.GoogleAuth, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Login or Signup with Google ID Token.
    """
    user = await service.process_google_login(db, google_auth.id_token)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(user.email, expires_delta=access_token_expires),
        "token_type": "bearer",
    }

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(request: schemas.UserResetPasswordRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Request a password reset email.
    """
    await service.request_password_reset(db, request.email)
    return {"message": "If an account exists with this email, a reset link has been sent."}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: schemas.UserResetPassword, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Reset password using a token.
    """
    success = await service.reset_password(db, data.token, data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    return {"message": "Password reset successfully."}

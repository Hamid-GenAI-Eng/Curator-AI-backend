from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, AnyHttpUrl, Field

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "AI Note Assistant"
    DEBUG: bool = True
    SECRET_KEY: str = "super_secret_dev_key_replace_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Config
    DATABASE_URL: str = ""
    MONGODB_URL: Optional[str] = None
    MONGODB_DB_NAME: str = "note_assistant_db"
    
    # Google OAuth2 Config
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    # SMTP Config (Brevo)
    SMTP_HOST: Optional[str] = "smtp-relay.brevo.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Cloudinary Config
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    
    # AI Configuration (Groq Multimodal Architecture)
    GROQ_API_KEY: str = Field("default_key_replace_in_production", env="GROQ_API_KEY")
    LLM_MODEL_NAME: str = "llama-3.3-70b-versatile"
    LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    
    VISION_MODEL_ID: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    GOOGLE_API_KEY: Optional[str] = None # No longer required for Vision
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

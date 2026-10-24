from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

_client = None
_db = None

def get_mongo_url() -> str:
    mongo_url = settings.MONGODB_URL
    if not mongo_url and settings.DATABASE_URL:
        if settings.DATABASE_URL.startswith(("mongodb://", "mongodb+srv://")):
            mongo_url = settings.DATABASE_URL
    if not mongo_url:
        mongo_url = "mongodb://localhost:27017"
    return mongo_url

def get_client():
    global _client, _db
    if _client is None:
        url = get_mongo_url()
        _client = AsyncIOMotorClient(url, uuidRepresentation="standard", serverSelectionTimeoutMS=5000)
        _db = _client[settings.MONGODB_DB_NAME]
    return _client

# Backward compatibility properties if imported directly
class LazyDB:
    def __getattr__(self, name):
        global _db
        if _db is None:
            get_client()
        return getattr(_db, name)

db = LazyDB()

# Dependency to get DB client
async def get_db():
    global _db
    try:
        if _db is None:
            get_client()
        yield _db
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable: {str(e)}. Please verify your MONGODB_URL environment variable in Atlas/Vercel."
        )


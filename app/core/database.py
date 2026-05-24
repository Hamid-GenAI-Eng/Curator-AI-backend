from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Determine the MongoDB URL (support backward compatibility with DATABASE_URL)
mongo_url = settings.MONGODB_URL
if not mongo_url and settings.DATABASE_URL:
    if settings.DATABASE_URL.startswith(("mongodb://", "mongodb+srv://")):
        mongo_url = settings.DATABASE_URL

if not mongo_url:
    # Default fallback
    mongo_url = "mongodb://localhost:27017"

# Create Motor client with standard UUID representation enabled
client = AsyncIOMotorClient(mongo_url, uuidRepresentation="standard")
db = client[settings.MONGODB_DB_NAME]

# Dependency to get DB client
async def get_db():
    yield db

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.auth.router import router as auth_router
from app.notes.router import router as notes_router

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"/openapi.json",
    debug=settings.DEBUG
)

# Set robust production CORS configurations
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "https://curator-ai-chi.vercel.app",
    "https://curator-ai-gamma.vercel.app",
]

if settings.BACKEND_CORS_ORIGINS:
    for o in settings.BACKEND_CORS_ORIGINS:
        origins.append(str(o).rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://curator-ai-.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include Routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(notes_router, prefix="/notes", tags=["Notes"])

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

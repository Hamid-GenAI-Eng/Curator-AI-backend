import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Response
from fastapi.responses import StreamingResponse
import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.note import Note
from app.models.batch import Batch
from app.notes import schemas
from app.services import ai_service

router = APIRouter()

@router.post("/process", response_model=schemas.NoteResponse, status_code=status.HTTP_201_CREATED)
async def process_note(
    file: UploadFile = File(...),
    batch_id: Optional[uuid.UUID] = Form(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a note and link it to a batch (new or existing).
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type."
        )
    
    try:
        image_bytes = await file.read()
        note = await ai_service.process_and_save_note(db, current_user.id, image_bytes, batch_id)
        return note
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )

@router.get("/batches", response_model=List[schemas.BatchResponse])
async def get_batches(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all projects (batches) for the user."""
    batch_docs = await db.batches.find({"user_id": current_user.id}).sort("created_at", -1).to_list(length=None)
    batches = []
    for b in batch_docs:
        b["id"] = b.pop("_id")
        note_docs = await db.notes.find({"batch_id": b["id"]}).sort("created_at", 1).to_list(length=None)
        for n in note_docs:
            n["id"] = n.pop("_id")
        b["notes"] = note_docs
        batches.append(b)
    return batches

@router.get("/batches/{batch_id}", response_model=schemas.BatchResponse)
async def get_batch_detail(
    batch_id: uuid.UUID,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed project synthesis and note gallery."""
    batch_doc = await db.batches.find_one({"_id": batch_id, "user_id": current_user.id})
    if not batch_doc:
        raise HTTPException(status_code=404, detail="Project not found")
    
    batch_doc["id"] = batch_doc.pop("_id")
    note_docs = await db.notes.find({"batch_id": batch_id}).sort("created_at", 1).to_list(length=None)
    for n in note_docs:
        n["id"] = n.pop("_id")
    batch_doc["notes"] = note_docs
    return batch_doc

@router.get("/batches/{batch_id}/download")
async def download_batch_pdf(
    batch_id: uuid.UUID,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate PDF on the fly dynamically and serve as an attachment download.
    """
    batch_doc = await db.batches.find_one({"_id": batch_id, "user_id": current_user.id})
    if not batch_doc:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    batch_doc["id"] = batch_doc.pop("_id")
    batch = Batch(**batch_doc)
    
    # Fetch all notes linked to this batch in order
    note_docs = await db.notes.find({"batch_id": batch_id}).sort("created_at", 1).to_list(length=None)
    for n in note_docs:
        n["id"] = n.pop("_id")
    notes = [Note(**n) for n in note_docs]
    
    if not notes:
        raise HTTPException(status_code=400, detail="Cannot generate PDF for an empty project batch.")
        
    try:
        from app.services.batch_service import generate_professional_pdf
        import os
        
        # Compile PDF on the fly
        pdf_path = generate_professional_pdf(batch.name or "Untitled Note Archive", notes)
        
        def iter_pdf(path: str):
            try:
                with open(path, "rb") as f:
                    while chunk := f.read(8192):
                        yield chunk
            finally:
                # Always clean up the temp file after streaming completes!
                if os.path.exists(path):
                    try: os.remove(path)
                    except: pass
                    
        filename = f"{batch.name or 'note_archive'}.pdf"
        # Sanitize filename
        filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
        
        return StreamingResponse(
            iter_pdf(pdf_path),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dynamic PDF compilation failed: {str(e)}"
        )

@router.get("/", response_model=List[schemas.NoteResponse])
async def get_notes_history(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve history of all notes."""
    note_docs = await db.notes.find({"user_id": current_user.id}).sort("created_at", -1).to_list(length=None)
    for n in note_docs:
        n["id"] = n.pop("_id")
    return note_docs

@router.get("/{note_id}", response_model=schemas.NoteResponse)
async def get_note_detail(
    note_id: uuid.UUID,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note_doc = await db.notes.find_one({"_id": note_id, "user_id": current_user.id})
    if not note_doc:
        raise HTTPException(status_code=404, detail="Note not found")
    note_doc["id"] = note_doc.pop("_id")
    return note_doc

@router.patch("/{note_id}", response_model=schemas.NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    note_update: schemas.NoteUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note_doc = await db.notes.find_one({"_id": note_id, "user_id": current_user.id})
    if not note_doc:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note_update.title is not None:
        await db.notes.update_one({"_id": note_id}, {"$set": {"title": note_update.title}})
        note_doc["title"] = note_update.title
    
    note_doc["id"] = note_doc.pop("_id")
    return note_doc

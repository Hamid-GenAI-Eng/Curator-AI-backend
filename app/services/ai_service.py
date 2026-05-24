from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.preprocessor import enhance_handwritten_image
from app.services.ocr_engine import extract_text_from_image
from app.services.llm_engine import refine_handwritten_text
from app.services.cloudinary_service import upload_image_to_cloudinary
from app.services.batch_service import sync_batch_document
from app.models.note import Note
from app.models.batch import Batch
import uuid
from typing import Optional
from datetime import datetime

async def process_and_save_note(
    db: AsyncIOMotorDatabase, 
    user_id: uuid.UUID, 
    image_bytes: bytes,
    batch_id: Optional[uuid.UUID] = None
) -> Note:
    """
    Unified pipeline with Batch Support (MongoDB):
    1. Preprocess & OCR
    2. LLM Refinement (with highlights)
    3. Cloudinary Upload
    4. Batch Handling (Link or Create)
    5. Save & Sync Batch Document
    """
    # 1. OCR Extraction
    enhanced_img = enhance_handwritten_image(image_bytes)
    raw_text = extract_text_from_image(enhanced_img)
    
    # 2. LLM Refinement
    refined_text = refine_handwritten_text(raw_text)
    
    # 3. Cloudinary Upload
    image_url = upload_image_to_cloudinary(image_bytes)
    
    # 4. Batch Handling
    batch = None
    if batch_id:
        doc = await db.batches.find_one({"_id": batch_id, "user_id": user_id})
        if doc:
            doc["id"] = doc.pop("_id")
            batch = Batch(**doc)
            
    if not batch:
        batch = Batch(user_id=user_id)
        batch_dict = batch.model_dump()
        batch_dict["_id"] = batch_dict.pop("id")
        await db.batches.insert_one(batch_dict)
    
    # 5. Save Note
    db_note = Note(
        user_id=user_id,
        batch_id=batch.id,
        image_url=image_url,
        raw_text=raw_text,
        refined_text=refined_text
    )
    note_dict = db_note.model_dump()
    note_dict["_id"] = note_dict.pop("id")
    await db.notes.insert_one(note_dict)
    
    # 6. Sync Project Document (Combined Text & PDF)
    await sync_batch_document(db, batch)
    
    return db_note

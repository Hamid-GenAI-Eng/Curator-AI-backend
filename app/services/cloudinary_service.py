import base64
import logging
import cloudinary
import cloudinary.uploader
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Cloudinary
if settings.CLOUDINARY_CLOUD_NAME:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )

def upload_image_to_cloudinary(image_bytes: bytes, folder: str = "notes", resource_type: str = "auto") -> str:
    """
    Uploads bytes to Cloudinary and returns the secure URL.
    Falls back gracefully to data URL if Cloudinary is unavailable.
    """
    if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY:
        try:
            response = cloudinary.uploader.upload(
                image_bytes,
                folder=folder,
                resource_type=resource_type
            )
            secure_url = response.get("secure_url")
            if secure_url:
                return secure_url
        except Exception as e:
            logger.warning(f"Cloudinary upload failed ({e}), falling back to data URL.")
    
    # Fallback to data URL
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    mime = "application/pdf" if resource_type == "raw" else "image/jpeg"
    return f"data:{mime};base64,{b64}"

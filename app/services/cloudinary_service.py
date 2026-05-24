import cloudinary
import cloudinary.uploader
from app.core.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

def upload_image_to_cloudinary(image_bytes: bytes, folder: str = "notes", resource_type: str = "auto") -> str:
    """
    Uploads bytes to Cloudinary and returns the secure URL.
    """
    try:
        response = cloudinary.uploader.upload(
            image_bytes,
            folder=folder,
            resource_type=resource_type
        )
        return response.get("secure_url")
    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {str(e)}")

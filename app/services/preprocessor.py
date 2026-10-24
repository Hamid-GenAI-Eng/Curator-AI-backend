import io
import cv2
import numpy as np
from PIL import Image, ImageOps
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def enhance_handwritten_image(image_bytes: bytes) -> np.ndarray:
    """
    Decodes, normalizes, and bounds resolution for AI Vision OCR.
    Handles JPG, PNG, WEBP, BMP, TIFF, GIF, and RGBA conversions.
    """
    image = None
    try:
        # First attempt with OpenCV
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception:
        image = None

    if image is None:
        try:
            # Fallback attempt with PIL (handles EXIF, RGBA, WEBP, etc.)
            pil_img = Image.open(io.BytesIO(image_bytes))
            pil_img = ImageOps.exif_transpose(pil_img)
            pil_img = pil_img.convert("RGB")
            image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"Image decoding failed: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Image decoding failed: {str(e)}. Please upload a valid image file."
            )

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Could not decode image data. Please ensure it is a valid image."
        )

    # Bound resolution for optimal Vision OCR (avoid massive base64 payloads)
    h, w = image.shape[:2]
    max_dim = max(h, w)
    if max_dim > 1600:
        scale = 1600.0 / max_dim
        new_w, new_h = int(w * scale), int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    elif max_dim < 600:
        scale = 1000.0 / max_dim
        new_w, new_h = int(w * scale), int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    return image


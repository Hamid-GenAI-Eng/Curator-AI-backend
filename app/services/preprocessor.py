import cv2
import numpy as np
from fastapi import HTTPException

def enhance_handwritten_image(image_bytes: bytes) -> np.ndarray:
    """
    Standardizes image for Google Cloud Vision OCR.
    Google Vision is extremely robust, so we only perform basic normalization.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Could not decode image.")

        # 1. Scaling: Google Vision likes high resolution (up to 4000px height is fine)
        # We target a comfortable 2000px height to preserve all handwriting detail.
        target_height = 2000
        h, w = image.shape[:2]
        if h < target_height:
            aspect_ratio = w / h
            target_width = int(target_height * aspect_ratio)
            image = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_CUBIC)

        # 2. Basic Normalization
        # We return the color image (BGR) as Google Vision handles color and contrast
        # internally much better than manual thresholding does for handwriting.
        
        return image

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image preprocessing failed: {str(e)}")

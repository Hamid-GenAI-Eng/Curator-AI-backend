import base64
import logging
import numpy as np
import cv2
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Groq Client for Vision
try:
    groq_client = Groq(api_key=settings.GROQ_API_KEY)
    logger.info(f"Initialized Groq Vision with model: {settings.VISION_MODEL_ID}")
except Exception as e:
    logger.error(f"Failed to initialize Groq Vision: {e}")
    groq_client = None

def extract_text_from_image(image_array: np.ndarray) -> str:
    """
    Extracts text from an image using Groq's high-speed multimodal models.
    Supports Urdu Nasta'liq and English handwriting.
    """
    if groq_client is None:
        raise RuntimeError("Groq Vision Client failed to initialize. Check your API key.")

    try:
        # 1. Convert OpenCV image (numpy array) to base64
        success, encoded_image = cv2.imencode('.jpg', image_array)
        if not success:
            raise ValueError("Could not encode image for Vision Extraction.")
        
        base64_image = base64.b64encode(encoded_image.tobytes()).decode('utf-8')

        # 2. Prepare the payload for Groq Vision
        prompt = (
            "Extract all text from this handwritten or printed note image accurately. \n\n"
            "CRITICAL RULES:\n"
            "1. LANGUAGE: Support both English and Urdu. If the text is Urdu, maintain Nasta'liq-friendly grammar and Right-to-Left logic.\n"
            "2. ACCURACY: Detect all characters, dots (nuqtas), and punctuation marks precisely.\n"
            "3. FORMAT: Only return the extracted raw text. Do not include any explanations, labels, or conversational filler.\n"
            "4. BI-LINGUAL: If English words appear in Urdu sentences, transcribe them correctly in place."
        )
        
        # 3. Call Groq Completion API (Multimodal) with fallback
        models_to_try = [settings.VISION_MODEL_ID, "qwen/qwen3.8-27b"]
        unique_models = []
        for m in models_to_try:
            if m and m not in unique_models:
                unique_models.append(m)

        completion = None
        last_error = None
        for model_name in unique_models:
            try:
                completion = groq_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.1,
                    max_tokens=2048,
                )
                logger.info(f"Vision Extraction (Groq {model_name}): Successfully extracted text.")
                break
            except Exception as exc:
                last_error = exc
                err_msg = str(exc).lower()
                if "model_not_found" in err_msg or "does not exist" in err_msg or "404" in err_msg:
                    logger.warning(f"Vision model {model_name} not found on Groq, trying fallback...")
                    continue
                raise

        if not completion:
            raise last_error or Exception("No vision model succeeded.")

        extracted_text = completion.choices[0].message.content
        
        if not extracted_text:
            logger.warning("Vision Extraction: No text detected in image.")
            return ""

        return extracted_text.strip()
        
    except Exception as e:
        logger.error(f"Vision Extraction (Groq) failed: {str(e)}")
        raise Exception(f"Vision Text Extraction failed: {str(e)}")

import os
from openai import OpenAI
from app.core.config import settings

# Initialize the Groq/OpenAI client using settings
client = None
if settings.GROQ_API_KEY:
    client = OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=settings.LLM_BASE_URL
    )

def refine_handwritten_text(raw_ocr_text: str) -> str:
    """
    Sends raw OCR text to the Groq API for semantic refinement and critical info highlighting.
    """
    if not client:
        return raw_ocr_text 
        
    if not raw_ocr_text or len(raw_ocr_text) < 2:
        return "No clear text detected to refine."

    system_prompt = """
    You are a professional multi-lingual text refinement assistant specializing in English and Urdu.
    Your job is to take raw, messy OCR output from handwritten notes and convert it into high-quality digital text.
    
    Processing Rules:
    1. LANGUAGE: Support both English and Urdu. Maintain proper grammar for both.
    2. REFINEMENT: Fix spelling, missing dots (nuqtas), and grammatical errors.
    3. HIGHLIGHTING: Identify CRITICAL information (dates, names, formulas, or key action items) and wrap them in [B]...[/B] tags for our PDF processor. Example: [B]October 12th[/B].
    4. STRUCTURE: Use proper paragraphing and bullet points.
    5. OUTPUT: Return ONLY the refined text. No introductory remarks.
    """

    try:
        completion = client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Handwritten OCR Input:\n{raw_ocr_text}"}
            ],
            temperature=0.1,
            max_tokens=2048
        )
        
        return completion.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"LLM Refinement failed: {str(e)}")
        return raw_ocr_text

def generate_batch_name(sample_text: str) -> str:
    """
    Generate a professional, concise title for a project based on its content.
    """
    if not client or not sample_text or len(sample_text) < 10:
        return "New Note Project"

    system_prompt = "You are a professional archivist. Summarize the following text into a CONCISE 3-5 word title for a note folder. Be professional. Return ONLY the title."
    
    try:
        completion = client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Note Content Sample:\n{sample_text[:1000]}"}
            ],
            temperature=0.5,
            max_tokens=20
        )
        return completion.choices[0].message.content.strip().strip('"').strip("'")
    except Exception:
        return "Synthesized Note Project"

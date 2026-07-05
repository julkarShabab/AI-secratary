import base64
import fitz
import io
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image

router = APIRouter()

ALLOWED_DOCUMENT_TYPES = [
    "application/pdf",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]

ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif"
]

MAX_FILE_SIZE = 10 * 1024 * 1024


def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text_from_docx(file_bytes: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    text = ""
    for para in doc.paragraphs:
        if para.text.strip():
            text += para.text + "\n"
    return text.strip()


def analyze_image_with_gemini(base64_image: str) -> str:
    """
    Sends image to Gemini for analysis.
    Returns a text description of the image.
    """
    try:
        from app.llm.gemini import GeminiLLM
        gemini = GeminiLLM()
        description = gemini.analyze_image(
            base64_image=base64_image,
            prompt="Please describe this image in detail. Include any text, people, objects, colors, and any other relevant information you can see."
        )
        return description
    except Exception as e:
        return f"Could not analyze image: {str(e)}"


@router.post("/upload/document")
async def upload_document(file: UploadFile = File(...)):
    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")

    try:
        filename = file.filename or ""

        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        elif filename.endswith(".docx"):
            text = extract_text_from_docx(file_bytes)
        elif filename.endswith(".doc"):
            raise HTTPException(
                status_code=400,
                detail="Old .doc format not supported. Please save as .docx"
            )
        else:
            text = extract_text_from_txt(file_bytes)

        if not text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from file."
            )

        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "type": "document",
            "content": text[:8000],
            "char_count": len(text),
            "truncated": len(text) > 8000
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )


@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type. Allowed: JPEG, PNG, WEBP, GIF"
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large. Max 10MB.")

    try:
        img = Image.open(io.BytesIO(file_bytes))
        max_size = (1024, 1024)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        fmt = "JPEG" if file.content_type == "image/jpeg" else "PNG"
        img.save(output, format=fmt)
        compressed_bytes = output.getvalue()

        base64_image = base64.b64encode(compressed_bytes).decode("utf-8")

        print("[ImageUpload] Analyzing image with Gemini...")
        description = analyze_image_with_gemini(base64_image)
        print(f"[ImageUpload] Analysis complete: {description[:100]}...")

        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "type": "image",
            "content_type": file.content_type,
            "base64": base64_image,
            "description": description,
            "size": len(compressed_bytes)
        })

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        )
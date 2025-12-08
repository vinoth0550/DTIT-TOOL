# services/add_pg_no.py

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from typing import Optional
from pydantic import BaseModel
import uuid
import fitz
from utils.storage_manager import save_upload, build_output_path
import config


router = APIRouter(
    prefix="/add-page-number",
    tags=["PDF Page Numbering"]
)

TOOL_NAME = "add_pg_no"


# ------------------------------
# Your Original Function (unchanged)
# ------------------------------
def add_page_numbers(input_path, output_path):
    try:
        doc = fitz.open(input_path)
        total_pages = len(doc)

        for page_num in range(total_pages):
            page = doc[page_num]
            text = f" {page_num + 1} "
            text_width = fitz.get_text_length(text, fontname="helv", fontsize=8)
            page_rect = page.rect
            x = (page_rect.width - text_width) / 2
            y = page_rect.height - 15  
            page.insert_text((x, y), text, fontname="helv", fontsize=10)

        doc.save(output_path)
        return True

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False


# ------------------------------
# Response Model
# ------------------------------
class PageNumberResponse(BaseModel):
    success: bool
    message: str
    download_url: Optional[str] = None



# ------------------------------
# API Route
# ------------------------------
@router.post("/", response_model=PageNumberResponse)
async def create_numbered_pdf(
    file: UploadFile = File(...),
    position: str = Form("bottom"),
    custom_text: Optional[str] = Form(None)
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # Save uploaded file
    input_path = save_upload(file, TOOL_NAME)

    # Output filename
    output_path = build_output_path(input_path.stem, "_numbered.pdf", TOOL_NAME)

    # Run your conversion function
    success = add_page_numbers(str(input_path), str(output_path))

    if not success:
        raise HTTPException(status_code=500, detail="Processing failed")

    # Download URL
    download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{output_path.name}"

    return PageNumberResponse(
        success=True,
        message="Page numbers added successfully!",
        download_url=download_url
    )


# Optional download route (similar style to others)
@router.get("/file/{file_name}")
def download_file(file_name: str):
    file_path = config.OUTPUT_ROOT / TOOL_NAME / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=file_name
    )

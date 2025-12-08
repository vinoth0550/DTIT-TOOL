# services/word_to_pdf.py

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import mammoth
from weasyprint import HTML
from utils.storage_manager import save_upload, build_output_path
import config

router = APIRouter(
    prefix="/word-to-pdf",
    tags=["Word to PDF"]
)

TOOL_NAME = "word_to_pdf"  # Folder name inside storage/uploads & storage/outputs


def convert_word_to_pdf(input_path: Path, output_path: Path):
    """Convert Word file → HTML → PDF"""
    try:
        # Step 1: Convert DOCX to HTML
        with open(input_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_content = result.value or "<p>(No content found)</p>"

        # Step 2: Convert HTML to PDF
        html_final = f"""
        <html><head><meta charset='UTF-8'>
        <style>
        body {{
            font-family: 'Times New Roman', serif;
            margin: 40px;
            font-size: 14px;
            line-height: 1.6;
            color: #000;
        }}
        </style></head><body>{html_content}</body></html>
        """

        HTML(string=html_final).write_pdf(str(output_path))

    except Exception as e:
        if output_path.exists():
            output_path.unlink()  # delete broken file
        raise Exception(f"Conversion error: {str(e)}")


@router.post("/")
async def word_to_pdf(file: UploadFile = File(...)):
    """Upload Word → PDF Conversion Route"""

    # Validate format
    if not file.filename.lower().endswith((".doc", ".docx")):
        return {
            "status": "error",
            "message": "Only .doc or .docx files allowed"
        }

    try:
        # Step A: Save upload
        input_path = save_upload(file, TOOL_NAME)

        # Step B: Build output path (.pdf)
        output_path = build_output_path(input_path.stem, ".pdf", TOOL_NAME)

        # Step C: Convert Word → PDF
        convert_word_to_pdf(input_path, output_path)

        # Step D: Download link
        download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{output_path.name}"

        return {
            "status": "success",
            "message": "Converted successfully!",
            "download_link": download_url,
            "file_name": output_path.name,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{file_name}")
def download_word_to_pdf(file_name: str):
    """Download converted PDF"""
    file_path = config.OUTPUT_ROOT / TOOL_NAME / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        str(file_path),
        media_type="application/pdf",
        filename=file_name
    )

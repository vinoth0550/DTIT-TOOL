
# converters/split_pdf.py

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
import tempfile
from utils.storage_manager import save_upload, build_output_path
import config

router = APIRouter(
    prefix="/split-pdf",
    tags=["Split PDF"]
)

TOOL_NAME = "split_pdf"

@router.post("/")
async def split_pdf(
    file: UploadFile = File(...),
    start_page: int = Form(...),
    end_page: int = Form(...)
):
    tmp_path = None

    # Validate file is PDF
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Only PDF files allowed"}
        )

    try:
        # Save uploaded PDF using storage manager
        input_path = save_upload(file, TOOL_NAME)

        # Create temp file copy for reading
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(Path(input_path).read_bytes())
            tmp_path = tmp.name

        pdf = PdfReader(tmp_path)
        total_pages = len(pdf.pages)

        # Validate page range
        if start_page < 1 or end_page > total_pages or start_page > end_page:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": f"Invalid page range. PDF has {total_pages} pages."}
            )

        # Split logic 
        writer = PdfWriter()
        for page_index in range(start_page - 1, end_page):
            writer.add_page(pdf.pages[page_index])

        # Create filename format based on original name
        original_stem = Path(file.filename).stem
        base_output_name = f"{original_stem}_pages_{start_page}_to_{end_page}"

        # Counter save system 
        output_path = build_output_path(base_output_name, ".pdf", TOOL_NAME)

        # Save output
        with open(output_path, "wb") as f:
            writer.write(f)

        download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{output_path.name}"

        return {
            "status": "success",
            "message": "PDF split successfully!",
            "download_link": download_url
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
    finally:
        if tmp_path and Path(tmp_path).exists():
            Path(tmp_path).unlink()


@router.get("/file/{filename}")
def download_split_file(filename: str):
    file_path = config.OUTPUT_ROOT / TOOL_NAME / filename

    if file_path.exists():
        return FileResponse(str(file_path), media_type="application/pdf", filename=filename)

    return JSONResponse(status_code=404, content={"status": "error", "message": "File not found"})

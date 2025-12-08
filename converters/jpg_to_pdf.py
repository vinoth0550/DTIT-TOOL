# services/jpg_to_pdf.py

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from PIL import Image

from utils.storage_manager import save_upload, build_output_path
import config

router = APIRouter(
    prefix="/jpg-to-pdf",
    tags=["JPG to PDF"]
)

TOOL_NAME = "jpg_to_pdf"


@router.post("/")
async def convert_jpg_to_pdf(file: UploadFile = File(...)):
    # Validate extension
    orig_name = file.filename
    ext = Path(orig_name).suffix.lower()

    if ext not in (".jpg", ".jpeg"):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "JPG or JPEG format only."}
        )

    # ----------- Save uploaded file (same logic retained) ----
    input_path = save_upload(file, TOOL_NAME)

    # Output filename structure: example → photo.pdf, photo(1).pdf, etc.
    base_name = Path(orig_name).stem
    output_path = build_output_path(base_name, ".pdf", TOOL_NAME)

    try:
        image = Image.open(input_path)
        image.convert("RGB").save(output_path, "PDF")
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal conversion error"}
        )

    # Build download link
    download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{Path(output_path).name}"

    return {
        "status": "success",
        "message": "JPG file converted into PDF successfully!",
        "download_link": download_url
    }


@router.get("/file/{filename}")
def download_pdf(filename: str):
    file_path = config.OUTPUT_ROOT / TOOL_NAME / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path), media_type="application/pdf", filename=filename)

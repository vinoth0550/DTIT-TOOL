
# converters/excel_to_pdf.py

import os
import shutil
import subprocess
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from utils.storage_manager import save_upload, build_output_path
import config


router = APIRouter(
    prefix="/excel-to-pdf",
    tags=["Excel to PDF"]
)

TOOL_NAME = "excel_to_pdf"


def excel_to_pdf(input_path, desired_output_path):
    """Convert Excel file to PDF using LibreOffice headless mode."""

    soffice = shutil.which("soffice")
    if not soffice:
        raise RuntimeError(
            "LibreOffice (soffice) not found. Install LibreOffice and ensure it's added to PATH."
        )

    cmd = [
        soffice,
        "--headless",
        "--norestore",
        "--nolockcheck",
        "--invisible",
        "--convert-to", "pdf",
        "--outdir", os.path.abspath(config.OUTPUT_ROOT / TOOL_NAME),
        os.path.abspath(input_path),
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"LibreOffice conversion failed: {e.stderr.decode(errors='ignore')}")

    # Find generated PDF
    base_name = Path(input_path).stem
    produced_pdf_path = config.OUTPUT_ROOT / TOOL_NAME / f"{base_name}.pdf"

    if not produced_pdf_path.exists():
        candidates = list((config.OUTPUT_ROOT / TOOL_NAME).glob("*.pdf"))
        if not candidates:
            raise RuntimeError("Converted PDF not found after conversion.")

        produced_pdf_path = candidates[0]

    # Rename to final requested name
    os.replace(produced_pdf_path, desired_output_path)

    return desired_output_path



# Main Route

@router.post("/")
async def convert_excel_to_pdf(file: UploadFile = File(...)):

    allowed_ext = (".xlsx", ".xls", ".xlsm")

    if not file.filename.lower().endswith(allowed_ext):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls, .xlsm) allowed.")

    # Save input
    input_path = save_upload(file, TOOL_NAME)

    # Output path
    output_path = build_output_path(input_path.stem, ".pdf", TOOL_NAME)

    try:
        excel_to_pdf(str(input_path), str(output_path))

        download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{output_path.name}"

        return {
            "status": "success",
            "message": "Excel converted to PDF successfully!",
            "download_link": download_url,
            "file_name": output_path.name
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")



# File Download Route

@router.get("/file/{file_name}")
def download_pdf(file_name: str):

    file_path = config.OUTPUT_ROOT / TOOL_NAME / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path), media_type="application/pdf", filename=file_name)

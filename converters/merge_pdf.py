
# converters/merge_pdf.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from typing import List
import pypdf
import os

from utils.storage_manager import save_upload, build_output_path
import config

router = APIRouter(
    prefix="/merge-pdf",
    tags=["PDF Merge"]
)

TOOL_NAME = "merge_pdf"


@router.post("/")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        return JSONResponse(status_code=400, content={"status": "error", "message": "No files provided"})

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Only PDF files are allowed"}
            )

    #  Save uploaded files 
    saved_paths = []
    for file in files:
        path = save_upload(file, TOOL_NAME)
        saved_paths.append(path)

    #  Merge Logic
    try:
        pdf_writer = pypdf.PdfWriter()

        for pdf_path in saved_paths:
            with open(pdf_path, "rb") as f:
                pdf_reader = pypdf.PdfReader(f)

                for page_num in range(len(pdf_reader.pages)):
                    pdf_writer.add_page(pdf_reader.pages[page_num])

        # Use counter-safe filename
        output_path = build_output_path("merged-file", ".pdf", TOOL_NAME)

        with open(output_path, "wb") as f:
            pdf_writer.write(f)

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": f"Error merging PDFs: {str(e)}"
        })

    return {
        "status": "success",
        "message": "Successfully merged PDF files!",
        "download_link": f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{output_path.name}"
    }


@router.get("/file/{filename}")
def download(filename: str):
    path = config.OUTPUT_ROOT / TOOL_NAME / filename

    if not path.exists():
        return JSONResponse(status_code=404, content={"status": "error", "message": "File not found"})

    return FileResponse(str(path), media_type="application/pdf", filename=filename)

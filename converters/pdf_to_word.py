

# converters/pdf_to_word.py

from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from fastapi import HTTPException
from pdf2docx import Converter

from utils.storage_manager import save_upload, build_output_path
import config

router = APIRouter(
    prefix="/pdf-to-word",
    tags=["PDF to Word"],
)

TOOL_NAME = "pdf_to_word"  


def pdf_to_word_internal(pdf_path: Path, output_path: Path):
    try:
        cv = Converter(str(pdf_path))
        cv.convert(str(output_path))
        cv.close()
    except Exception as e:
        if output_path.exists():
            output_path.unlink()  
        raise Exception(f"Conversion failed: {str(e)}")


@router.post("/")
async def convert_pdf_to_word(file: UploadFile = File(...)):
    #  Validate extension
    if not file.filename.lower().endswith(".pdf"):
        return {
            "status": "error",
            "message": "Only PDF files are allowed",
        }

    try:
        # Save upload in storage/uploads/pdf_to_word/
        input_path = save_upload(file, TOOL_NAME)

        # Prepare output path in storage/outputs/pdf_to_word/
        original_name = input_path.stem  # filename without extension
        output_path = build_output_path(original_name, ".docx", TOOL_NAME)

        # Convert
        pdf_to_word_internal(input_path, output_path)

        #  download link
     
        download_link = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{output_path.name}"

        return {
            "status": "success",
            "message": "PDF converted successfully!",
            "download_link": download_link,
            "file_name": output_path.name,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Conversion failed: {str(e)}",
        }


# (Optional) backward-compatible route similar to /api/filesword/{file_name}
@router.get("/file/{file_name}")
def download_pdf_to_word(file_name: str):
    word_path = config.OUTPUT_ROOT / TOOL_NAME / file_name
    if word_path.exists():
        from fastapi.responses import FileResponse
        return FileResponse(
            str(word_path),
            media_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            filename=file_name,
        )

    raise HTTPException(status_code=404, detail="File not found.")

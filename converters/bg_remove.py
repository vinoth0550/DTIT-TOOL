
# converters/bg_remove.py

import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
from rembg import remove
import config
from utils.storage_manager import save_upload, build_output_path


router = APIRouter(
    prefix="/remove-bg",
    tags=["Background Remover"]
)

TOOL_NAME = "bg_remove"

# Allowed file extensions

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "gif", "tiff"}


def is_valid_image(filename: str) -> bool:
    """Check valid image format"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS




def process_background_removal(input_path: Path, output_path: Path):
    input_img = Image.open(input_path)
    output_img = remove(input_img)
    output_img.save(output_path)
    return True



@router.post("/")
async def remove_background_api(file: UploadFile = File(...)):

    if not is_valid_image(file.filename):
        raise HTTPException(status_code=400, detail="Images only are allowed.")

    try:
        # Save uploaded image
        input_path = save_upload(file, TOOL_NAME)

        # Result should always be PNG since transparency is needed
        output_path = build_output_path(input_path.stem, ".png", TOOL_NAME)

        # Process background removal
        process_background_removal(input_path, output_path)

        download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{output_path.name}"

        return {
            "status": "success",
            "message": "Background removed successfully!",
            "download_link": download_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{file_name}")
def download_removed_bg(file_name: str):

    file_path = config.OUTPUT_ROOT / TOOL_NAME / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path), media_type="image/png", filename=file_name)


# converters/bg_white_adder.py

import os
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from PIL import Image
from rembg import remove

from utils.storage_manager import save_upload, build_output_path
import config

router = APIRouter(
    prefix="/white-background",
    tags=["Background White Adder"] 
)

TOOL_NAME = "bg_white_adder"

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "gif", "tiff"}


def is_valid_image(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/")
async def remove_background(file: UploadFile = File(...)):
    if not is_valid_image(file.filename):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Only image files allowed"}
        )

    try:
        #  Uploaded File
        input_path = save_upload(file, TOOL_NAME)

        # Extract base name for clean output name 
        original_name = Path(file.filename).stem
        output_filename = build_output_path(original_name, ".jpg", TOOL_NAME)

        # Image Processing 
        input_img = Image.open(input_path)
        output_img = remove(input_img)

        output_img = output_img.convert("RGBA")
        white_bg = Image.new("RGBA", output_img.size, (255, 255, 255, 255))
        final_img = Image.alpha_composite(white_bg, output_img).convert("RGB")

        # Save result
        final_img.save(output_filename, "JPEG")

        # Download URL
        download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{Path(output_filename).name}"

        return {
            "status": "success",
            "message": "White background added successfully",
            "download_link": download_url
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@router.get("/file/{file_name}")
def download_whitebg_image(file_name: str):
    file_path = config.OUTPUT_ROOT / TOOL_NAME / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path), media_type="image/jpeg", filename=file_name)

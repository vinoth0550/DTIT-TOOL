
# converters/bw_converter.py

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from PIL import Image

from utils.storage_manager import save_upload, build_output_path
import config

router = APIRouter(
    prefix="/bw-converter",
    tags=["Black & White Converter"]
)

TOOL_NAME = "bw_converter"

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}


@router.post("/")
async def convert_to_bw(img: UploadFile = File(...)):

    ext = Path(img.filename).suffix.lower()
    if ext not in VALID_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Images only"
            }
        )

    try:
        #  Save Upload 
        input_path = save_upload(img, TOOL_NAME)

        # Build Output Name Using Smart Counter

        original_name = Path(img.filename).stem
        output_path = build_output_path(original_name, ext, TOOL_NAME)

        # Convert to B&W 
        image = Image.open(input_path)
        bw_img = image.convert("1")  # Pure black & white 

        bw_img.save(output_path)

        download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{Path(output_path).name}"

        return {
            "status": "success",
            "message": "Successfully converted image into B&W format.",
            "download_link": download_url
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Conversion error: {str(e)}"
            }
        )


@router.get("/file/{filename}")
def download_bw_file(filename: str):
    file_path = config.OUTPUT_ROOT / TOOL_NAME / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path), media_type="image/jpeg", filename=filename)

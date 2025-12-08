
# converters/pdf_to_jpg.py

from pathlib import Path
import shutil
import fitz
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from utils.storage_manager import save_upload, build_output_path
import config

router = APIRouter(
    prefix="/pdf-to-jpg",
    tags=["PDF to JPG"]
)

TOOL_NAME = "pdf_to_jpg"


@router.post("/")
async def convert_pdf_to_jpg(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Only PDF files allowed."}
        )

    #  Save uploaded PDF
    input_path = save_upload(file, TOOL_NAME)

    # Extract filename without extension to use as base output name
    base_name = Path(file.filename).stem

    # Create output zip filename with counter if needed
    zip_output_path = build_output_path(base_name, ".zip", TOOL_NAME)

    # Temp folder to store multiple JPG pages before zipping
    temp_folder = Path(str(zip_output_path).replace(".zip", ""))
    temp_folder.mkdir(exist_ok=True, parents=True)

    try:
        #  Conversion Logic 
        with fitz.open(input_path) as doc:
            for page_number in range(len(doc)):
                page = doc.load_page(page_number)
                pix = page.get_pixmap(dpi=200)
                output_img = temp_folder / f"page_{page_number + 1}.jpg"
                pix.save(str(output_img))

        # Create ZIP
        shutil.make_archive(str(zip_output_path).replace(".zip", ""), 'zip', temp_folder)

        # Optional: Copy first page into output folder (single JPG preview)
        first_jpg = temp_folder / "page_1.jpg"
        if first_jpg.exists():
            preview_output = build_output_path(base_name, ".jpg", TOOL_NAME)
            shutil.copy(first_jpg, preview_output)

        # Build download URL
        download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{Path(zip_output_path).name}"

        return {
            "status": "success",
            "message": "PDF converted into JPG successfully!",
            "download_link": download_url
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Conversion failed: {str(e)}"}
        )

    finally:
        # Cleanup temp image folder
        if temp_folder.exists():
            shutil.rmtree(temp_folder, ignore_errors=True)


@router.get("/file/{filename}")
def download_converted(filename: str):
    file_path = config.OUTPUT_ROOT / TOOL_NAME / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Return correct MIME based on file type
    mimetype = "application/zip" if file_path.suffix == ".zip" else "image/jpeg"

    return FileResponse(str(file_path), media_type=mimetype, filename=filename)

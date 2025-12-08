
# services/pdf_to_excel.py

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import tabula
import camelot
import pdfplumber
import easyocr
from pdf2image import convert_from_path
from utils.storage_manager import save_upload, build_output_path
import config


router = APIRouter(
    prefix="/pdf-to-excel",
    tags=["PDF to Excel"]
)

TOOL_NAME = "pdf_to_excel"


# ----------------------------------------
# Your Original Hybrid Extraction Function
# ----------------------------------------
def hybrid_pdf_to_excel(pdf_path, output_path):

    reader = easyocr.Reader(["en"], gpu=False)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        # Tabula tables
        try:
            tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)
            if tables:
                for i, table in enumerate(tables):
                    table.to_excel(writer, sheet_name=f"Table_Tabula_{i+1}", index=False)
        except Exception:
            pass

        # Camelot backup extraction
        try:
            cams = camelot.read_pdf(pdf_path, pages="all")
            for i, camtable in enumerate(cams):
                camtable.df.to_excel(writer, sheet_name=f"Table_Camelot_{i+1}", index=False)
        except Exception:
            pass

        # Extract normal text
        text_rows = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    for line in text.split("\n"):
                        text_rows.append([line])

        if text_rows:
            df_text = pd.DataFrame(text_rows, columns=["Extracted_Text"])
            df_text.to_excel(writer, sheet_name="Text_Extracted", index=False)

        # OCR fallback if no text
        if not text_rows:
            images = convert_from_path(pdf_path)
            ocr_lines = []

            for idx, img in enumerate(images):
                temp_img = f"temp_page_{idx}.png"
                img.save(temp_img)

                result = reader.readtext(temp_img, detail=0)
                for line in result:
                    ocr_lines.append([line])

                Path(temp_img).unlink(missing_ok=True)

            df_ocr = pd.DataFrame(ocr_lines, columns=["OCR_Text"])
            df_ocr.to_excel(writer, sheet_name="Text_OCR", index=False)

    return output_path


# ----------------------------------------
# FastAPI Route
# ----------------------------------------
@router.post("/")
async def convert_pdf_to_excel(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        return {"status": "error", "message": "Only PDF files allowed"}

    # Save uploaded file
    input_path = save_upload(file, TOOL_NAME)

    # Create output path
    output_path = build_output_path(input_path.stem, ".xlsx", TOOL_NAME)

    try:
        hybrid_pdf_to_excel(str(input_path), str(output_path))

        download_link = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{output_path.name}"

        return {
            "status": "success",
            "message": "PDF converted to Excel successfully!",
            "download_link": download_link,
            "file_name": output_path.name
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")


# ----------------------------------------
# Download Route
# ----------------------------------------
@router.get("/file/{file_name}")
def download_excel(file_name: str):
    file_path = config.OUTPUT_ROOT / TOOL_NAME / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=file_name
    )

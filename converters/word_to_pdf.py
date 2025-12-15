
# # converters/word_to_pdf.py

# from pathlib import Path
# from fastapi import APIRouter, UploadFile, File, HTTPException
# from fastapi.responses import FileResponse
# import mammoth
# from weasyprint import HTML
# from utils.storage_manager import save_upload, build_output_path
# import config

# router = APIRouter(
#     prefix="/word-to-pdf",
#     tags=["Word to PDF"]
# )

# TOOL_NAME = "word_to_pdf"  


# def convert_word_to_pdf(input_path: Path, output_path: Path):
   
#     try:
#         # Convert DOCX to HTML
#         with open(input_path, "rb") as docx_file:
#             result = mammoth.convert_to_html(docx_file)
#             html_content = result.value or "<p>(No content found)</p>"

#         #  Convert HTML to PDF
#         html_final = f"""
#         <html><head><meta charset='UTF-8'>
#         <style>
#         body {{
#             font-family: 'Times New Roman', serif;
#             margin: 40px;
#             font-size: 14px;
#             line-height: 1.6;
#             color: #000;
#         }}
#         </style></head><body>{html_content}</body></html>
#         """

#         HTML(string=html_final).write_pdf(str(output_path))

#     except Exception as e:
#         if output_path.exists():
#             output_path.unlink()  
#         raise Exception(f"Conversion error: {str(e)}")


# @router.post("/")
# async def word_to_pdf(file: UploadFile = File(...)):
#     """Upload Word → PDF Conversion Route"""

#     # Validate format
#     if not file.filename.lower().endswith((".doc", ".docx")):
#         return {
#             "status": "error",
#             "message": "Only .doc or .docx files allowed"
#         }

#     try:
#         # Save upload
#         input_path = save_upload(file, TOOL_NAME)

#         # Build output path (.pdf)
#         output_path = build_output_path(input_path.stem, ".pdf", TOOL_NAME)

#         #  Convert Word → PDF
#         convert_word_to_pdf(input_path, output_path)

#         # Download link
#         download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{output_path.name}"

#         return {
#             "status": "success",
#             "message": "Converted successfully!",
#             "download_link": download_url,
#             "file_name": output_path.name,
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/file/{file_name}")
# def download_word_to_pdf(file_name: str):
#     """Download converted PDF"""
#     file_path = config.OUTPUT_ROOT / TOOL_NAME / file_name

#     if not file_path.exists():
#         raise HTTPException(status_code=404, detail="File not found")

#     return FileResponse(
#         str(file_path),
#         media_type="application/pdf",
#         filename=file_name
#     )





# this one for get in the table 


# converters/word_to_pdf.py

# from pathlib import Path
# from fastapi import APIRouter, UploadFile, File, HTTPException
# from fastapi.responses import FileResponse
# import mammoth
# from weasyprint import HTML
# from utils.storage_manager import save_upload, build_output_path
# import config

# router = APIRouter(
#     prefix="/word-to-pdf",
#     tags=["Word to PDF"]
# )

# TOOL_NAME = "word_to_pdf"  


# def convert_word_to_pdf(input_path: Path, output_path: Path):
   
#     try:
#         # Convert DOCX to HTML
#         with open(input_path, "rb") as docx_file:
#             result = mammoth.convert_to_html(docx_file)
#             html_content = result.value or "<p>(No content found)</p>"

#         # Convert HTML to PDF with comprehensive table styling
#         html_final = f"""
#         <html>
#             <head>
#                 <meta charset='UTF-8'>
#                 <style>
#                     body {{
#                         font-family: 'Calibri', 'Arial', sans-serif;
#                         margin: 40px;
#                         font-size: 11pt;
#                         line-height: 1.5;
#                         color: #000;
#                     }}
                    
#                     /* Table Styling */
#                     table {{
#                         width: 100%;
#                         border-collapse: collapse;
#                         margin: 15px 0;
#                         page-break-inside: avoid;
#                     }}
                    
#                     table, th, td {{
#                         border: 1px solid #000;
#                     }}
                    
#                     th {{
#                         background-color: #E8E8E8;
#                         font-weight: bold;
#                         padding: 8px;
#                         text-align: left;
#                         vertical-align: middle;
#                     }}
                    
#                     td {{
#                         padding: 8px;
#                         text-align: left;
#                         vertical-align: middle;
#                         word-wrap: break-word;
#                     }}
                    
#                     /* Alternate row coloring for better readability */
#                     tr:nth-child(even) {{
#                         background-color: #F5F5F5;
#                     }}
                    
#                     /* Ensure proper table display */
#                     p {{
#                         margin: 10px 0;
#                     }}
#                 </style>
#             </head>
#             <body>
#                 {html_content}
#             </body>
#         </html>
#         """

#         HTML(string=html_final).write_pdf(str(output_path))

#     except Exception as e:
#         if output_path.exists():
#             output_path.unlink()  
#         raise Exception(f"Conversion error: {str(e)}")


# @router.post("/")
# async def word_to_pdf(file: UploadFile = File(...)):
#     """Upload Word → PDF Conversion Route"""

#     # Validate format
#     if not file.filename.lower().endswith((".doc", ".docx")):
#         return {
#             "status": "error",
#             "message": "Only .doc or .docx files allowed"
#         }

#     try:
#         # Save upload
#         input_path = save_upload(file, TOOL_NAME)

#         # Build output path (.pdf)
#         output_path = build_output_path(input_path.stem, ".pdf", TOOL_NAME)

#         # Convert Word → PDF
#         convert_word_to_pdf(input_path, output_path)

#         # Download link
#         download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{output_path.name}"

#         return {
#             "status": "success",
#             "message": "Converted successfully!",
#             "download_link": download_url,
#             "file_name": output_path.name,
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/file/{file_name}")
# def download_word_to_pdf(file_name: str):
#     """Download converted PDF"""
#     file_path = config.OUTPUT_ROOT / TOOL_NAME / file_name

#     if not file_path.exists():
#         raise HTTPException(status_code=404, detail="File not found")

#     return FileResponse(
#         str(file_path),
#         media_type="application/pdf",
#         filename=file_name
#     )





















# this code is for copying word files same as like in pdf with libreoffice.



# converters/word_to_pdf.py

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import subprocess
import os
import config

router = APIRouter(
    prefix="/word-to-pdf",
    tags=["Word to PDF"]
)

TOOL_NAME = "word_to_pdf"


def convert_word_to_pdf_libreoffice(input_path: Path, output_dir: Path):
    """
    Convert DOCX to PDF using LibreOffice
    Preserves all formatting, colors, fonts, and table layouts
    """
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # LibreOffice command
        command = [
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(output_dir),
            str(input_path)
        ]
        
        # Run conversion
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise Exception(f"LibreOffice conversion failed: {result.stderr}")
            
        # Return the output PDF path
        pdf_filename = input_path.stem + ".pdf"
        return output_dir / pdf_filename
        
    except subprocess.TimeoutExpired:
        raise Exception("Conversion timeout - file too large")
    except Exception as e:
        raise Exception(f"LibreOffice conversion error: {str(e)}")


@router.post("/")
async def word_to_pdf(file: UploadFile = File(...)):
    """Upload Word → PDF Conversion Route"""

    # Validate format
    if not file.filename.lower().endswith((".doc", ".docx")):
        return {
            "status": "error",
            "message": "Only .doc or .docx files allowed"
        }

    try:
        # Save upload
        from utils.storage_manager import save_upload, build_output_path
        input_path = save_upload(file, TOOL_NAME)
        
        # Get output directory
        output_dir = config.OUTPUT_ROOT / TOOL_NAME
        
        # Convert using LibreOffice
        pdf_path = convert_word_to_pdf_libreoffice(input_path, output_dir)
        
        # Download link
        download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{pdf_path.name}"

        return {
            "status": "success",
            "message": "Converted successfully!",
            "download_link": download_url,
            "file_name": pdf_path.name,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{file_name}")
def download_word_to_pdf(file_name: str):
    """Download converted PDF"""
    file_path = config.OUTPUT_ROOT / TOOL_NAME / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        str(file_path),
        media_type="application/pdf",
        filename=file_name
    )

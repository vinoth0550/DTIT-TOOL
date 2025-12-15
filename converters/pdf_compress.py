

# services/pdf_compress.py

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
import os, io, shutil, tempfile, subprocess
from datetime import datetime
from PIL import Image
import pikepdf

from utils.storage_manager import save_upload, build_output_path
import config

router = APIRouter(
    prefix="/pdf-compress",
    tags=["PDF Compress"]
)

TOOL_NAME = "pdf_compress"


# FUNCTIONS 

def compress_with_ghostscript(input_path, output_path, setting="ebook"):
    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.5",
        f"-dPDFSETTINGS=/{setting}",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        "-dDetectDuplicateImages=true",
        "-dCompressFonts=true",
        "-dSubsetFonts=true",
        "-dOptimize=true",
        f"-sOutputFile={output_path}",
        input_path
    ]
    try:
        return subprocess.run(cmd, capture_output=True, timeout=120).returncode == 0
    except:
        return False


def compress_with_ghostscript_aggressive(input_path, output_path):
    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/screen",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        "-dOptimize=true",
        f"-sOutputFile={output_path}",
        input_path
    ]
    try:
        return subprocess.run(cmd, capture_output=True, timeout=120).returncode == 0
    except:
        return False


def compress_image_data(image_bytes, quality=50, max_dimension=800):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = img.size
        if max(w, h) > max_dimension:
            ratio = min(max_dimension / w, max_dimension / h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue(), img.size
    except:
        return None, None


def compress_with_pikepdf(input_path, output_path, quality=45, max_dimension=700):
    try:
        pdf = pikepdf.open(input_path)
        for page in pdf.pages:
            res = page.get("/Resources", {})
            xobjs = res.get("/XObject", {})
            for k in list(xobjs.keys()):
                x = xobjs[k]
                if isinstance(x, pikepdf.Stream) and x.get("/Subtype") == pikepdf.Name.Image:
                    data = x.read_bytes()
                    new_data, size = compress_image_data(data, quality, max_dimension)
                    if new_data:
                        xobjs[k] = pikepdf.Stream(pdf, new_data)
        pdf.save(output_path, compress_streams=True)
        pdf.close()
        return True
    except:
        return False


def compress_pdf(input_path, output_path):
    original = os.path.getsize(input_path)
    tmp = tempfile.mkdtemp()
    try:
        candidates = []
        p1 = Path(tmp) / "gs_ebook.pdf"
        p2 = Path(tmp) / "gs_screen.pdf"
        p3 = Path(tmp) / "pike.pdf"

        if compress_with_ghostscript(input_path, p1):
            candidates.append((p1, p1.stat().st_size))
        if compress_with_ghostscript_aggressive(input_path, p2):
            candidates.append((p2, p2.stat().st_size))
        if compress_with_pikepdf(input_path, p3):
            candidates.append((p3, p3.stat().st_size))

        if not candidates:
            shutil.copy2(input_path, output_path)
            return original, original

        best = min(candidates, key=lambda x: x[1])
        shutil.copy2(best[0], output_path)
        return original, best[1]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def format_size(n):
    return f"{n/1024/1024:.2f} MB" if n > 1024*1024 else f"{n/1024:.2f} KB"


# API ROUTES

@router.post("/")
async def compress_single(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"status": "error", "message": "PDF only"})

    input_path = save_upload(file, TOOL_NAME)
    output_path = build_output_path(Path(file.filename).stem, ".pdf", TOOL_NAME)

    original, compressed = compress_pdf(str(input_path), str(output_path))

    reduction = max(0, (original - compressed) / original * 100)

    return {
        "status": "success",
        "download_link": f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{output_path.name}",
        "details": {
            "original_size": format_size(original),
            "compressed_size": format_size(compressed),
            "reduction": f"{reduction:.1f}%"
        }
    }


@router.post("/batch")
async def compress_multiple(files: list[UploadFile] = File(...)):
    results = []

    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            continue

        ip = save_upload(f, TOOL_NAME)
        op = build_output_path(Path(f.filename).stem, ".pdf", TOOL_NAME)

        o, c = compress_pdf(str(ip), str(op))
        r = max(0, (o - c) / o * 100)

        results.append({
            "file": f.filename,
            "download_link": f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{op.name}",
            "original_size": format_size(o),
            "compressed_size": format_size(c),
            "reduction": f"{r:.1f}%"
        })

    return {"status": "success", "files": results}


@router.get("/file/{filename}")
def download(filename: str):
    path = config.OUTPUT_ROOT / TOOL_NAME / filename
    if not path.exists():
        return JSONResponse(status_code=404, content={"status": "error", "message": "Not found"})
    return FileResponse(str(path), media_type="application/pdf", filename=filename)






# this is working but not compressing as like the fapi it need some work 
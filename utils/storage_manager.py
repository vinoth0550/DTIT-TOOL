
# utils/storage_manager.py

from pathlib import Path
import shutil
from fastapi import UploadFile
from .file_utils import get_unique_filename
import config


def get_tool_dirs(tool_name: str) -> tuple[Path, Path]:
    """
    Returns (upload_dir, output_dir) for given tool_name.
    Example: tool_name = "pdf_to_word"
    upload: storage/uploads/pdf_to_word/
    output: storage/outputs/pdf_to_word/
    """
    upload_dir = config.UPLOAD_ROOT / tool_name
    output_dir = config.OUTPUT_ROOT / tool_name

    upload_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    return upload_dir, output_dir


def save_upload(file: UploadFile, tool_name: str) -> Path:
    """
    Save uploaded file into the tool's upload directory and return the full path.
    """
    upload_dir, _ = get_tool_dirs(tool_name)
    file_path = upload_dir / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path


def build_output_path(original_name: str, extension: str, tool_name: str) -> Path:
    """
    Build a unique output path in the tool's output directory.
    """
    _, output_dir = get_tool_dirs(tool_name)
    filename = get_unique_filename(output_dir, original_name, extension)
    return output_dir / filename

# utils/file_utils.py
from pathlib import Path

def get_unique_filename(directory: Path, base_name: str, extension: str) -> str:
    """
    Generate a unique filename in 'directory' like:
    base_name.ext, base_name(1).ext, base_name(2).ext, ...
    """
    directory.mkdir(parents=True, exist_ok=True)

    filename = f"{base_name}{extension}"
    counter = 1

    while (directory / filename).exists():
        filename = f"{base_name}({counter}){extension}"
        counter += 1

    return filename



# config.py

from pathlib import Path



import shutil


# BASIC APP INFO 
APP_TITLE = "DTIT Tools API"
APP_DESCRIPTION = "API for multiple office/media conversion tools"
APP_VERSION = "1.0.0"

# CORS 
ALLOWED_ORIGINS = [
    "https://python.selfietoons.com",
    "https://tsitfilemanager.in",
    "https://www.tsitfilemanager.in",
    "http://localhost:3000",
    "http://localhost:3001",
]

# PATHS

BASE_DIR = Path(__file__).resolve().parent

STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_ROOT = STORAGE_DIR / "uploads"
OUTPUT_ROOT = STORAGE_DIR / "outputs"

# Create base folders on import

for p in [STORAGE_DIR, UPLOAD_ROOT, OUTPUT_ROOT]:
    p.mkdir(parents=True, exist_ok=True)

# When running on server, set this to your domain
# Example: "https://python.selfietoons.com"

BASE_DOMAIN = "https://python.selfietoons.com"

# Base for static downloads (we'll mount /downloads to OUTPUT_ROOT)

BASE_DOWNLOAD_URL = f"{BASE_DOMAIN}/downloads"


# ---------- GHOSTSCRIPT ----------
GS_BINARY = (
    shutil.which("gs")
    or shutil.which("gswin64c")
    or r"C:\Program Files\gs\gs10.03.0\bin\gswin64c.exe"
)







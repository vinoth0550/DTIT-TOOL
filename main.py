
# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import config
from  converters import pdf_to_word, word_to_pdf, add_pg_no, bg_remove, pdf_to_excel, excel_to_pdf
from converters import text_to_speech, bg_white_adder, jpg_to_pdf, pdf_to_jpg, black_white_converter
from converters import split_pdf, merge_pdf, pdf_to_pptx, pptx_to_pdf


app = FastAPI(
    title=config.APP_TITLE,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# STATIC DOWNLOADS 

app.mount("/downloads", StaticFiles(directory=config.OUTPUT_ROOT), name="downloads")

# ROUTERS (TOOLS) 
app.include_router(pdf_to_word.router)

app.include_router(word_to_pdf.router)

app.include_router(add_pg_no.router)

app.include_router(bg_remove.router)

app.include_router(pdf_to_excel.router)

app.include_router(excel_to_pdf.router)

app.include_router(text_to_speech.router)

app.include_router(bg_white_adder.router)

app.include_router(jpg_to_pdf.router)

app.include_router(pdf_to_jpg.router)

app.include_router(black_white_converter.router)

app.include_router(split_pdf.router)

app.include_router(merge_pdf.router)

app.include_router(pdf_to_pptx.router)

app.include_router(pptx_to_pdf.router)


@app.get("/api/")
def home():
    return {"message": "DTIT Tools API running successfully!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)







# services/text_to_speech.py

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from gtts import gTTS
import langdetect
from pydub import AudioSegment
from gtts.lang import tts_langs
from googletrans import Translator
import nltk

from utils.storage_manager import save_upload, build_output_path
import config

# ------------ INIT -----------------
router = APIRouter(
    prefix="/text-to-speech",
    tags=["Text to Speech"]
)

TOOL_NAME = "text_to_speech"

translator = Translator()
nltk.download("punkt", quiet=True)

# ------------ Original Functions (UNCHANGED) -----------

def detect_language(text):
    try:
        return langdetect.detect(text)
    except:
        return 'en'


def adjust_voice(audio, gender='female'):
    if gender == 'male':
        octaves = -0.2
        new_sample_rate = int(audio.frame_rate * (2.0 ** octaves))
        male_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
        return male_audio.set_frame_rate(audio.frame_rate)
    return audio






def text_to_speech_engine(text, gender='female', language='auto'):
    detected_lang = detect_language(text)

    if language != "auto" and language != detected_lang:
        translated = translator.translate(text, src=detected_lang, dest=language)
        text = translated.text
    elif language == "auto":
        language = detected_lang  

    unique_id = str(uuid.uuid4())
    temp_file = f"temp_{unique_id}.mp3"

    output_filename = f"{unique_id}_{gender}_{language}.mp3"

    # Final output placement
    output_path = build_output_path(unique_id, ".mp3", TOOL_NAME)

    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(temp_file)

    audio = AudioSegment.from_mp3(temp_file)
    modified_audio = adjust_voice(audio, gender)

    modified_audio.export(output_path, format="mp3")
    os.remove(temp_file)

    return output_path.name

# ------------ Response Models ------------

class SuccessResponse(BaseModel):
    status: str = "success"
    download_link: str

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str


# ------------ API Routes ------------------

@router.post("/", response_model=SuccessResponse)
async def api_text_to_speech(
        text: Optional[str] = Form(None),
        file: Optional[UploadFile] = File(None),
        gender: str = Form("female"),
        language: str = Form("auto")
):
    if gender not in ['male', 'female']:
        gender = 'female'

    if (text and text.strip()) and file:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Provide either text OR .txt file — not both."}
        )

    available_languages = tts_langs()
    if language not in available_languages and language != "auto":
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": f"Invalid language code. Supported: {', '.join(available_languages.keys())}"}
        )

    # Extract text
    if text and text.strip():
        text_content = text.strip()

    elif file and file.filename.endswith(".txt"):
        temp_path = save_upload(file, TOOL_NAME)
        text_content = Path(temp_path).read_text("utf-8")
    else:
        raise HTTPException(status_code=400, detail="Provide text or a .txt file.")

    filename = text_to_speech_engine(text_content, gender, language)

    download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{filename}"

    return SuccessResponse(status="success", download_link=download_url)



@router.get("/file/{filename}")
def download_file(filename: str):
    file_path = config.OUTPUT_ROOT / TOOL_NAME / filename
    if file_path.exists():
        return FileResponse(str(file_path), media_type="audio/mpeg", filename=filename)
    raise HTTPException(status_code=404, detail="File not found")


@router.get("/languages")
def get_supported_languages():
    return {"supported_languages": tts_langs()}











# # # above the code is working fine but male voice not audioable like a male so need to fix that with below the code







# # services/text_to_speech.py

# import os
# import uuid
# import shutil
# from pathlib import Path
# from typing import Optional

# from fastapi import APIRouter, UploadFile, File, Form, HTTPException
# from fastapi.responses import FileResponse, JSONResponse
# from pydantic import BaseModel
# from gtts import gTTS
# import langdetect
# from pydub import AudioSegment
# from gtts.lang import tts_langs
# from googletrans import Translator
# import nltk

# from utils.storage_manager import save_upload, build_output_path
# import config








# # ------------ INIT -----------------
# router = APIRouter(
#     prefix="/text-to-speech",
#     tags=["Text to Speech"]
# )

# TOOL_NAME = "text_to_speech"

# translator = Translator()
# nltk.download("punkt", quiet=True)

# # ------------ Original Functions (UNCHANGED) -----------

# def detect_language(text):
#     try:
#         return langdetect.detect(text)
#     except:
#         return 'en'


# # def adjust_voice(audio, gender='female'):
# #     if gender == 'male':
# #         octaves = -0.2
# #         new_sample_rate = int(audio.frame_rate * (2.0 ** octaves))
# #         male_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
# #         return male_audio.set_frame_rate(audio.frame_rate)
# #     return audio






# def adjust_voice(audio, gender='female'):
#     if gender == 'male':
#         # Lower the pitch more dramatically for a deeper male voice
#         octaves = -0.5  # Increased from -0.2 for deeper voice
#         new_sample_rate = int(audio.frame_rate * (2.0 ** octaves))
#         male_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
#         audio = male_audio.set_frame_rate(audio.frame_rate)
        
#         # Add bass boost and compression for strength/boldness
#         audio = audio.low_pass_filter(8000)  # Emphasize lower frequencies
#         audio = audio.apply_gain(2)  # Increase volume slightly for boldness
        
#         return audio
    
#     return audio






# def text_to_speech_engine(text, gender='female', language='auto'):
#     detected_lang = detect_language(text)

#     if language != "auto" and language != detected_lang:
#         translated = translator.translate(text, src=detected_lang, dest=language)
#         text = translated.text
#     elif language == "auto":
#         language = detected_lang  

#     unique_id = str(uuid.uuid4())
#     temp_file = f"temp_{unique_id}.mp3"

#     output_filename = f"{unique_id}_{gender}_{language}.mp3"

#     # Final output placement
#     output_path = build_output_path(unique_id, ".mp3", TOOL_NAME)

#     tts = gTTS(text=text, lang=language, slow=False)
#     tts.save(temp_file)

#     audio = AudioSegment.from_mp3(temp_file)
#     modified_audio = adjust_voice(audio, gender)

#     modified_audio.export(output_path, format="mp3")
#     os.remove(temp_file)

#     return output_path.name

# # ------------ Response Models ------------

# class SuccessResponse(BaseModel):
#     status: str = "success"
#     download_link: str

# class ErrorResponse(BaseModel):
#     status: str = "error"
#     message: str


# # ------------ API Routes ------------------

# @router.post("/", response_model=SuccessResponse)
# async def api_text_to_speech(
#         text: Optional[str] = Form(None),
#         file: Optional[UploadFile] = File(None),
#         gender: str = Form("female"),
#         language: str = Form("auto")
# ):
#     if gender not in ['male', 'female']:
#         gender = 'female'

#     if (text and text.strip()) and file:
#         return JSONResponse(
#             status_code=400,
#             content={"status": "error", "message": "Provide either text OR .txt file — not both."}
#         )

#     available_languages = tts_langs()
#     if language not in available_languages and language != "auto":
#         return JSONResponse(
#             status_code=400,
#             content={"status": "error", "message": f"Invalid language code. Supported: {', '.join(available_languages.keys())}"}
#         )

#     # Extract text
#     if text and text.strip():
#         text_content = text.strip()

#     elif file and file.filename.endswith(".txt"):
#         temp_path = save_upload(file, TOOL_NAME)
#         text_content = Path(temp_path).read_text("utf-8")
#     else:
#         raise HTTPException(status_code=400, detail="Provide text or a .txt file.")

#     filename = text_to_speech_engine(text_content, gender, language)

#     download_url = f"{config.BASE_DOWNLOAD_URL}/{TOOL_NAME}/{filename}"

#     return SuccessResponse(status="success", download_link=download_url)



# @router.get("/file/{filename}")
# def download_file(filename: str):
#     file_path = config.OUTPUT_ROOT / TOOL_NAME / filename
#     if file_path.exists():
#         return FileResponse(str(file_path), media_type="audio/mpeg", filename=filename)
#     raise HTTPException(status_code=404, detail="File not found")


# @router.get("/languages")
# def get_supported_languages():
#     return {"supported_languages": tts_langs()}













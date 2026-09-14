from fastapi import APIRouter, UploadFile, File
from pathlib import Path

from app.services.transcription import transcribe_audio


router = APIRouter(
    prefix="/audio",
    tags=["Audio"]
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):

    file_path = UPLOAD_DIR / file.filename

    contents = await file.read()

    with open(file_path, "wb") as audio_file:
        audio_file.write(contents)

    transcript = transcribe_audio(str(file_path))

    return {
        "message": "Audio uploaded and transcribed successfully",
        "filename": file.filename,
        "size": len(contents),
        "transcript": transcript
    }
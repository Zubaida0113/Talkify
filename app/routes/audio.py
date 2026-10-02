from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.transcription import is_usable_transcript, transcribe_audio
from app.services.task_extractor import extract_tasks, validate_tasks

router = APIRouter(
    prefix="/audio",
    tags=["Audio"]
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class TranscriptRequest(BaseModel):
    transcript: str


def _tasks_from_transcript(transcript: str) -> list[dict]:
    extracted_tasks = extract_tasks(transcript)
    validated_tasks = validate_tasks(extracted_tasks)
    return [task.model_dump(mode="json") for task in validated_tasks]


@router.post("/transcript")
async def process_transcript(payload: TranscriptRequest):
    transcript = payload.transcript.strip()

    if not is_usable_transcript(transcript):
        raise HTTPException(status_code=422, detail="No clear speech was detected.")

    return {
        "message": "Transcript processed successfully",
        "transcript": transcript,
        "tasks": _tasks_from_transcript(transcript),
    }


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    contents = await file.read()

    suffix = Path(file.filename or "").suffix
    with NamedTemporaryFile(dir=UPLOAD_DIR, suffix=suffix, delete=False) as audio_file:
        audio_file.write(contents)
        file_path = Path(audio_file.name)

    try:
        transcript = transcribe_audio(str(file_path))
    finally:
        file_path.unlink(missing_ok=True)

    if not is_usable_transcript(transcript):
        raise HTTPException(
            status_code=422,
            detail="No clear speech was detected. Please record your task again.",
        )

    return {
        "message": "Audio processed successfully",
        "filename": file.filename,
        "transcript": transcript,
        "tasks": _tasks_from_transcript(transcript),
    }
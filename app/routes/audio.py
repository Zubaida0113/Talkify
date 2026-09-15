from fastapi import APIRouter, UploadFile, File
from pathlib import Path

from app.services.transcription import transcribe_audio
from app.services.task_extractor import extract_tasks, validate_tasks

router = APIRouter(
    prefix="/audio",
    tags=["Audio"]
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):

    # 1. Save uploaded audio
    file_path = UPLOAD_DIR / file.filename

    contents = await file.read()

    with open(file_path, "wb") as audio_file:
        audio_file.write(contents)

    # 2. Transcribe audio using Whisper
    transcript = transcribe_audio(str(file_path))

    # 3. Extract tasks from transcript
    extracted_tasks = extract_tasks(transcript)

    # 4. Validate extracted tasks using Pydantic
    validated_tasks = validate_tasks(extracted_tasks)

    # 5. Convert Pydantic objects to JSON-compatible dictionaries
    tasks = [
        task.model_dump(mode="json")
        for task in validated_tasks
    ]

    return {
        "message": "Audio processed successfully",
        "filename": file.filename,
        "transcript": transcript,
        "tasks": tasks
    }
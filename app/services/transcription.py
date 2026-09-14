import whisper 

# Load the Whisper model once when the application starts
model = whisper.load_model("base")


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe an audio file using local Whisper.
    """

    result = model.transcribe(file_path)

    return result["text"].strip()
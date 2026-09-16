import re

import whisper

# Load the Whisper model once when the application starts
model = whisper.load_model("base")


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe an audio file using local Whisper.
    """

    result = model.transcribe(file_path)

    segments = result.get("segments", [])
    speech_segments = [
        segment
        for segment in segments
        if segment.get("no_speech_prob", 1) < 0.75
        and segment.get("avg_logprob", -10) > -2.0
    ]

    if segments and not speech_segments:
        return ""

    return result["text"].strip()


def is_usable_transcript(transcript: str) -> bool:
    """Reject empty, noise-like, and unusably short Whisper output."""
    words = re.findall(r"[A-Za-z]{2,}", transcript or "")
    if len(words) < 2:
        return False

    letters = "".join(words).lower()
    return len(set(letters)) > 2
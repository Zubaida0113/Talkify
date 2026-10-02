import json
import os
import re
import subprocess
import tempfile
import wave

from vosk import KaldiRecognizer, Model

VOSK_MODEL_PATH = os.environ.get("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15")
_model = None


def get_vosk_model():
    global _model

    if _model is None:
        if not os.path.exists(VOSK_MODEL_PATH):
            raise RuntimeError(
                "Vosk model not found. Set VOSK_MODEL_PATH or download the model to "
                f"{VOSK_MODEL_PATH}."
            )
        _model = Model(VOSK_MODEL_PATH)

    return _model


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe audio with Vosk after converting it to 16 kHz mono PCM WAV.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
        wav_path = wav_file.name

    try:
        subprocess.run(
            [
                "ffmpeg", "-nostdin", "-y", "-i", file_path, "-vn",
                "-ac", "1", "-ar", "16000", "-sample_fmt", "s16", wav_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        recognizer = KaldiRecognizer(get_vosk_model(), 16000)
        with wave.open(wav_path, "rb") as audio_file:
            while data := audio_file.readframes(4000):
                recognizer.AcceptWaveform(data)

        result = json.loads(recognizer.FinalResult())
        return result.get("text", "").strip()
    finally:
        os.unlink(wav_path)


def is_usable_transcript(transcript: str) -> bool:
    """Reject empty, noise-like, and unusably short speech transcripts."""
    words = re.findall(r"[A-Za-z]{2,}", transcript or "")
    if not words:
        return False

    letters = "".join(words).lower()
    return len(set(letters)) > 2
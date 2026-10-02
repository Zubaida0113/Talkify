import asyncio
import json
import wave

import pytest
from fastapi import HTTPException

from app.routes import audio
from app.services import transcription


def test_process_transcript_extracts_and_validates_tasks(monkeypatch):
    monkeypatch.setattr(
        audio,
        "extract_tasks",
        lambda transcript: [{"title": "Email the client", "priority": "high"}],
    )

    result = asyncio.run(
        audio.process_transcript(audio.TranscriptRequest(transcript="Email the client urgently"))
    )

    assert result["transcript"] == "Email the client urgently"
    assert result["tasks"] == [
        {
            "title": "Email the client",
            "description": None,
            "due_date": None,
            "priority": "high",
        }
    ]


def test_process_transcript_rejects_unusable_speech():
    with pytest.raises(HTTPException) as error:
        asyncio.run(audio.process_transcript(audio.TranscriptRequest(transcript="   ")))

    assert error.value.status_code == 422


def test_transcribe_audio_reads_vosk_final_result(monkeypatch, tmp_path):
    class FakeRecognizer:
        def __init__(self, model, sample_rate):
            assert sample_rate == 16000

        def AcceptWaveform(self, data):
            return True

        def FinalResult(self):
            return json.dumps({"text": "send email"})

    def fake_ffmpeg(command, **kwargs):
        with wave.open(command[-1], "wb") as audio_file:
            audio_file.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
            audio_file.writeframes(b"\x00\x00" * 32)

    source_path = tmp_path / "recording.webm"
    source_path.write_bytes(b"recording")
    monkeypatch.setattr(transcription.subprocess, "run", fake_ffmpeg)
    monkeypatch.setattr(transcription, "get_vosk_model", lambda: object())
    monkeypatch.setattr(transcription, "KaldiRecognizer", FakeRecognizer)

    assert transcription.transcribe_audio(str(source_path)) == "send email"
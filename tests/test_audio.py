import asyncio

import pytest
from fastapi import HTTPException

from app.routes import audio


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
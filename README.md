<div align="center">

# Talkify

### Speak naturally. Get tasks you can actually use.

**An AI-powered voice task manager that turns messy speech into organized action.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-Structured_AI-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Whisper](https://img.shields.io/badge/Whisper-Local_STT-412991?logo=openai&logoColor=white)](https://github.com/openai/whisper)
[![Tests](https://img.shields.io/badge/tests-2_passing-2ea44f)](tests/)

<br />

`Voice input` &nbsp;->&nbsp; `Whisper transcription` &nbsp;->&nbsp; `Gemini reasoning` &nbsp;->&nbsp; `Validated tasks`

</div>

<br />

## At a glance

| | |
| --- | --- |
| **What it does** | Converts voice notes into reviewable, date-aware tasks |
| **Core challenge** | Understanding intent without treating every `and` as a new task |
| **AI layer** | Local Whisper for speech-to-text + Gemini for structured extraction |
| **Safety model** | Human approval before AI-generated data is persisted |
| **Backend** | FastAPI REST API with SQLite and SQLAlchemy |

## Contents

- [Why Talkify](#why-this-project-stands-out)
- [How it works](#how-it-works)
- [Features](#features)
- [REST API](#rest-api)
- [Architecture decisions](#architecture-decisions)
- [Tech stack](#tech-stack)
- [Run locally](#run-locally)
- [Test it](#test-it)
- [Current status](#current-status)
- [Roadmap](#roadmap)

## Why this project stands out

Most todo apps start with a text box. Talkify starts with how people actually think:

```text
"Remind me to send the proposal tomorrow, and make sure I call the client after lunch."
```

Talkify turns that into a reviewable task preview with:

- Clean, grammatical task titles
- Context-aware task boundaries
- ISO due dates from phrases such as `tomorrow` and `next Friday`
- `low`, `medium`, or `high` priority
- Optional descriptions
- Human confirmation before database insertion

This is a small but complete example of an AI-assisted workflow: unstructured input, model reasoning, schema validation, user review, and durable persistence.

## How it works

### Product flow

```text
Browser microphone
        |
        v
WebM audio upload
        |
        v
Local Whisper transcription
        |
        v
Gemini task understanding
        |
        v
Pydantic validation
        |
        v
Human confirmation modal
        |
        v
FastAPI + SQLite
        |
        v
Task dashboard
```

## Features

### 01 / Voice-first task creation

Record a voice note directly in the browser with the MediaRecorder API. A glass recording overlay with an animated microphone gives immediate feedback while the audio is captured. The recording is uploaded to FastAPI and transcribed locally with Whisper as soon as the user stops.

Talkify also guards the voice pipeline against empty, silent, noisy, or unusable recordings. When no clear speech is detected, the user receives a retry message instead of an empty or misleading task list.

### 02 / Gemini-powered extraction

Gemini acts as the reasoning layer after transcription. It is prompted to return structured JSON containing:

```json
{
  "title": "Send the project proposal",
  "description": "Follow up with the client after sending it.",
  "due_date": "2026-09-17",
  "priority": "high"
}
```

The application normalizes and validates model output before it is shown to the user. If Gemini is unavailable, a local heuristic fallback keeps the basic extraction flow usable.

### 03 / Human-in-the-loop safety

AI-generated tasks are previewed in the browser. The user can cancel them or approve them with **Add All**. The model never writes directly to the database.

### 04 / Task management

- Create tasks manually or by voice
- View, update, and delete tasks
- Mark tasks as completed
- Filter by All, Active, Completed, and Pending
- See overdue incomplete tasks in Pending
- Sort by due date, then priority
- Group tasks into Urgent, Today, Tomorrow, and Later
- Move tasks naturally between date groups as the calendar changes
- Show completed tasks with a muted gray visual state

### 05 / Fast browser experience

- Upload audio immediately after recording stops
- Defer frontend JavaScript so it does not delay the first render
- Compress large FastAPI responses with GZip
- Reuse date-formatting work while rendering task lists
- Keep the initial layout stable with zero observed Cumulative Layout Shift

## REST API

FastAPI exposes interactive documentation at `/docs` and `/redoc`.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Serve the Talkify dashboard |
| `POST` | `/audio/upload` | Transcribe audio and extract tasks |
| `POST` | `/tasks/` | Create a task |
| `GET` | `/tasks/` | List tasks |
| `GET` | `/tasks/{task_id}` | Fetch one task |
| `PUT` | `/tasks/{task_id}` | Update a task |
| `POST` | `/tasks/{task_id}/complete` | Mark a task complete |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

## Architecture decisions

### Why Whisper locally?

Keeping transcription local avoids adding another hosted speech-to-text dependency and makes the pipeline easier to experiment with. It also gives the project a clear separation between local audio processing and cloud-based language understanding.

### Why Gemini?

The task extraction problem is lightweight but context-sensitive. Gemini Flash-Lite is a practical fit for an MVP because it is fast and cost-conscious while still handling grammar, intent, relative dates, and multiple actions in one transcript.

### Why validate model output?

LLM output is not trusted blindly. The extractor normalizes dates and priorities, then Pydantic validates the final task shape before the API returns it. This keeps the probabilistic part of the system behind a predictable application boundary.

### Why guard the audio pipeline?

Speech recognition can return empty text or low-confidence noise when a microphone captures silence, background sounds, or an unclear recording. Talkify checks Whisper output before invoking Gemini, which avoids unnecessary API calls, reduces confusing results, and gives the user a clear recovery path.

### Why optimize the browser path?

The dashboard is designed to feel immediate even though voice processing involves local transcription and a network request. Deferred JavaScript, GZip responses, and reusable date formatting reduce initial render work and transfer size without changing the product flow.

## Tech stack

**Backend**

- Python 3.11+
- FastAPI and Uvicorn
- SQLAlchemy with SQLite
- Pydantic

**AI and language processing**

- OpenAI Whisper for local transcription
- Gemini API through the supported `google-genai` SDK
- `dateparser` for fallback date handling

**Frontend**

- HTML and CSS
- Vanilla JavaScript
- MediaRecorder API
- Fetch API

**Quality and tooling**

- Pytest
- GitHub Codespaces
- FFmpeg

## Project structure

```text
Talkify/
├── app/
│   ├── main.py                 # FastAPI application and dashboard route
│   ├── database.py             # SQLAlchemy engine and sessions
│   ├── models/task.py          # Database model
│   ├── schemas/task.py         # Pydantic request/response schemas
│   ├── routes/
│   │   ├── tasks.py            # Task CRUD and completion endpoints
│   │   └── audio.py            # Audio upload and AI extraction endpoint
│   ├── services/
│   │   ├── transcription.py    # Local Whisper transcription
│   │   ├── task_extractor.py   # Gemini parsing and fallback logic
│   │   └── task_service.py     # Task-related service layer
│   └── static/
│       ├── index.html          # Dashboard markup
│       ├── script.js           # Browser interaction and filters
│       └── style.css           # Dashboard styling
├── tests/
├── uploads/                    # Temporary audio files
├── requirements.txt
└── README.md
```

## Run locally

### 1. Clone and create an environment

```bash
git clone <your-repository-url>
cd Talkify
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```powershell
venv\Scripts\activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

Whisper requires FFmpeg:

```bash
# Ubuntu / GitHub Codespaces
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### 3. Configure Gemini

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Create a key in [Google AI Studio](https://aistudio.google.com/). Keep `.env` private and never commit the key.

### 4. Start the application

For local development:

```bash
uvicorn app.main:app --reload
```

For GitHub Codespaces, bind to all interfaces so the forwarded port is reachable:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open:

- Dashboard: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

In Codespaces, open port `8000` from the Ports panel.

## Test it

Run the focused extractor tests:

```bash
source venv/bin/activate
pytest tests/test_extractor.py -q
```

To test a real Gemini request without printing the API key:

```bash
python -c "from app.services.task_extractor import call_llm_task_parser; print(call_llm_task_parser('Send the report tomorrow with high priority'))"
```

## What I learned building Talkify

Talkify sits at the boundary between flexible human language and strict software contracts. The most valuable engineering challenge was not calling an LLM; it was designing the boundary around it:

1. Keep transcription and reasoning as separate services.
2. Ask the model for a constrained JSON shape.
3. Normalize dates and priority values after the model responds.
4. Validate with Pydantic before data reaches the API or database.
5. Put a human confirmation step between AI output and persistence.
6. Keep a fallback path for missing keys, quota errors, or model failures.

That pattern generalizes well beyond task management: customer support triage, meeting action items, CRM updates, and any workflow that converts messy human input into structured records.

## Current status

- FastAPI REST API is implemented
- SQLite persistence is implemented
- Local Whisper transcription is implemented
- Gemini structured task extraction is implemented
- Relative date and priority inference is implemented
- Human approval before persistence is implemented
- Manual and voice-based task creation are implemented
- Recording overlay with animated microphone feedback is implemented
- Empty and noisy voice guardrails with retry messaging are implemented
- Immediate post-recording upload is implemented
- Pending overdue-task filter is implemented
- Urgent category is displayed before all other task groups
- GZip response compression and deferred frontend loading are implemented
- Extractor regression tests are implemented

## Roadmap

- Add authentication and user-specific task lists
- Store audio-processing status and error details
- Add richer task editing from the dashboard
- Add integration tests for the complete audio pipeline
- Add background processing for longer recordings
- Deploy the API and frontend as a production service

## License

This project is currently intended as a portfolio and learning project. Add a license before distributing it as a reusable library or service.

---

Built to explore a practical question: **what if your todo list could understand you before asking you to format your thoughts?**

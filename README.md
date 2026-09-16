# 🎙️ Talkify — AI-Powered Voice Task Manager

Talkify is a full-stack voice-enabled task management application that allows users to create and manage tasks using natural voice commands.

Instead of manually typing a task, users can simply speak it. Talkify converts the voice input into text using **local Whisper**, extracts structured task information such as **title, due date, and priority**, validates the result, and lets the user review the tasks before saving them to the database.

The project combines **Python, FastAPI, speech-to-text, NLP, Pydantic, SQLite, SQLAlchemy, HTML, CSS, and JavaScript** to demonstrate practical AI automation and full-stack development.

---

## 🚀 Features

### 🎙️ Voice Task Creation

Record a voice command directly from the browser.

Example:

> "I want to update my Aadhaar number tomorrow and go for a driving license renewal on next Tuesday."

A single voice recording can contain multiple tasks.

---

### 🗣️ Local Speech-to-Text

Talkify uses **OpenAI Whisper locally** to convert recorded audio into text.

```text
Voice Input
    ↓
WebM Audio
    ↓
Local Whisper
    ↓
Transcript
```

The application currently uses Whisper locally rather than relying on an external speech-to-text API.

---

### 🧠 Task Extraction

The transcript is processed using Python-based NLP/rule-based logic to identify individual tasks.

The system extracts:

* Task title
* Due date
* Priority
* Description

For example:

```text
Input:
"I need to update my Aadhaar number tomorrow."

Output:
Title: Update my Aadhaar number
Due date: Tomorrow
Priority: Medium
```

---

### 📅 Natural Date Detection

Talkify can recognize natural date expressions such as:

* Today
* Tomorrow
* Monday
* Friday
* Next Tuesday

These expressions are converted into actual dates using `dateparser`.

---

### ⭐ Priority Detection

The system detects priority-related keywords such as:

* Urgent
* ASAP
* Important
* Immediately
* Critical
* High priority
* Low priority
* No rush

Tasks are assigned:

```text
High
Medium
Low
```

Medium is used as the default priority when no priority is specified.

---

### ✅ Pydantic Validation

Extracted task data is validated using Pydantic before being stored.

Current task structure:

```text
title
description
due_date
priority
```

This ensures that the extracted data follows a predictable structure.

---

### 👤 Human-in-the-Loop Confirmation

Talkify does not immediately save AI-generated tasks.

After processing the voice input, the application displays a confirmation modal:

```text
AI Found These Tasks

1. Update my Aadhaar number
   📅 September 16
   ⭐ Medium

2. Driving license renewal
   📅 September 22
   ⭐ Medium

        Cancel       Add All
```

The user can review the extracted tasks and choose whether to add them.

This provides a **human-in-the-loop layer** before AI-generated information is persisted.

---

### 🗄️ SQLite Database

Approved tasks are stored in SQLite using SQLAlchemy.

The application currently supports:

* Create task
* View all tasks
* View individual task
* Update task
* Delete task
* Mark task as completed

---

### 📝 Manual Task Creation

Users can also create tasks manually through the normal Todo interface without using voice input.

---

### 🔍 Task Filtering

Tasks can currently be filtered by:

* All
* Active
* Completed

---

### 📊 Intelligent Task Ordering

Tasks are being organized based on their urgency.

The planned ordering logic is:

```text
Primary → Due Date
Secondary → Priority
```

Tasks with the closest upcoming due date appear first.

For tasks with the same due date:

```text
High
  ↓
Medium
  ↓
Low
```

This allows the application to naturally prioritize tasks that need attention first.

---

# 🏗️ Architecture

```text
                    🎙️ Voice Input
                          │
                          ▼
                 Browser MediaRecorder
                          │
                          ▼
                     WebM Audio
                          │
                          ▼
                 Local Whisper STT
                          │
                          ▼
                    Transcript
                          │
                          ▼
              Python Task Extraction
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
            Due Date            Priority
                │                   │
                └─────────┬─────────┘
                          ▼
                  Pydantic Validation
                          │
                          ▼
                👤 User Confirmation
                          │
                          ▼
                    FastAPI API
                          │
                          ▼
                  SQLite Database
                          │
                          ▼
                    Todo Dashboard
```

---

# 🛠️ Tech Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic

## AI / NLP

* OpenAI Whisper
* `dateparser`
* Python-based rule extraction

## Frontend

* HTML
* CSS
* JavaScript
* MediaRecorder API
* Fetch API

## Development Tools

* Git
* GitHub
* GitHub Codespaces
* FFmpeg
* Pytest

---

# 📁 Project Structure

```text
Talkify/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_service.py
│   │   ├── transcription.py
│   │   └── task_extractor.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   └── audio.py
│   │
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── script.js
│
├── tests/
│
├── uploads/
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# 🔄 Application Flow

### Normal Task

```text
User enters task
       ↓
FastAPI
       ↓
Pydantic Validation
       ↓
SQLite
       ↓
Task Dashboard
```

### Voice Task

```text
User speaks
       ↓
Browser records audio
       ↓
Audio uploaded to FastAPI
       ↓
Whisper generates transcript
       ↓
Task extractor identifies tasks
       ↓
Due date + priority extracted
       ↓
Pydantic validates output
       ↓
User reviews AI-generated tasks
       ↓
User clicks "Add All"
       ↓
Tasks saved to SQLite
       ↓
Dashboard refreshed
```

---

# 🧪 Example

### Voice Input

```text
"I want to update my Aadhaar number tomorrow
and go for a driving license renewal on next Tuesday."
```

### Whisper Transcript

```text
I want to update my Aadhaar number tomorrow
and go for a driving license renewal on next Tuesday.
```

### Extracted Tasks

```json
[
  {
    "title": "update my Aadhaar number",
    "description": null,
    "due_date": "2026-09-16",
    "priority": "medium"
  },
  {
    "title": "go for a driving license renewal",
    "description": null,
    "due_date": "2026-09-22",
    "priority": "medium"
  }
]
```

### User Confirmation

The extracted tasks are shown to the user before they are added to the database.

---

# 🔮 Future Enhancements

## 🤖 LLM-Based Post-Processing

A future version will introduce an LLM after Whisper:

```text
Voice
  ↓
Whisper
  ↓
Raw Transcript
  ↓
LLM
  ↓
Corrected + Structured Tasks
  ↓
Pydantic Validation
  ↓
Human Confirmation
  ↓
SQLite
```

The LLM will help with:

* Noisy or inaccurate transcripts
* Accent-related transcription errors
* Context understanding
* Better task titles
* Natural language date interpretation
* Priority inference
* Multiple tasks in complex sentences
* Removing unnecessary words
* Ambiguous user instructions

For example:

```text
Whisper:
"update my Adharkar number"

        ↓

LLM:
"Update my Aadhaar number"
```

The LLM will act as a **post-processing and reasoning layer**, while Whisper remains responsible for speech-to-text.

---

## 🧪 Testing

Planned improvements include automated tests for:

* Task extraction
* Date detection
* Priority detection
* Pydantic validation
* API endpoints
* Database operations
* Voice-processing pipeline

---

# 🎯 Project Goals

Talkify is being developed to demonstrate practical experience with:

* Python
* FastAPI
* REST APIs
* Full-stack development
* SQL databases
* SQLAlchemy
* Pydantic
* Speech-to-text AI
* NLP
* AI automation
* Structured AI outputs
* Human-in-the-loop systems
* API integration
* Error handling
* Testing

---

# 📌 Current Status

### Completed ✅

* [x] FastAPI backend
* [x] SQLite database
* [x] SQLAlchemy models
* [x] Pydantic schemas
* [x] CRUD task APIs
* [x] Manual task creation
* [x] Task completion
* [x] Task deletion
* [x] Task filtering
* [x] Browser voice recording
* [x] WebM audio upload
* [x] Local Whisper transcription
* [x] Natural date extraction
* [x] Priority extraction
* [x] Multiple task extraction from one voice command
* [x] Pydantic validation of extracted tasks
* [x] AI task confirmation modal
* [x] Human approval before database insertion
* [x] Saving extracted tasks to SQLite
* [x] Refreshing the Todo dashboard after voice task creation

### In Progress 🚧

* [ ] Due-date + priority display on task cards
* [ ] Automatic task ordering by due date
* [ ] Priority ordering for tasks with the same due date
* [ ] Improved natural-language extraction

### Planned 🔮

* [ ] LLM-based transcript correction
* [ ] LLM-based structured task extraction
* [ ] Better handling of accents and noisy speech
* [ ] Improved natural-language understanding
* [ ] Automated tests
* [ ] Production-oriented error handling
* [ ] Final documentation and deployment

---

# 👩‍💻 Project Motivation

Talkify was built to explore how **AI can automate everyday productivity workflows** rather than simply acting as a chatbot.

The project focuses on a practical pipeline where AI takes unstructured human input — **voice** — and converts it into structured, validated, user-approved actions that can be persisted and managed by a traditional software system.

This makes Talkify a combination of:

**AI + Automation + Backend Engineering + Full-Stack Development.**

# ⚙️ Setup & Run

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd Talkify
```

If you are using **GitHub Codespaces**, you can open the repository directly in a Codespace instead.

---

## 2. Create a Virtual Environment

Create a Python virtual environment:

```bash
python3 -m venv venv
```

Activate it:

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

The project uses packages including:

* FastAPI
* Uvicorn
* SQLAlchemy
* Pydantic
* `openai-whisper`
* `dateparser`
* `python-multipart`
* Pytest

---

## 4. Install FFmpeg

Whisper requires **FFmpeg** to process audio formats such as WebM.

### macOS

If you use Homebrew:

```bash
brew install ffmpeg
```

Verify the installation:

```bash
ffmpeg -version
```

### Ubuntu / GitHub Codespaces

```bash
sudo apt update
sudo apt install ffmpeg
```

Verify:

```bash
ffmpeg -version
```

> FFmpeg must be available in your system PATH for Whisper to process uploaded audio.

---

## 5. Create the Upload Directory

The application stores temporary voice recordings in the `uploads` directory.

```bash
mkdir -p uploads
```

The directory is automatically created by the application if it does not already exist, but creating it manually is also fine.

---

## 6. Start the FastAPI Server

Run:

```bash
uvicorn app.main:app --reload
```

You should see something similar to:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

## 7. Open Talkify

Open the application in your browser:

```text
http://127.0.0.1:8000
```

If you are using **GitHub Codespaces**, open the forwarded port from the **Ports** panel and launch the application using the generated URL.

---

## 8. Test the API

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

From Swagger UI you can test endpoints such as:

```text
POST /tasks/
GET  /tasks/
GET  /tasks/{task_id}
PUT  /tasks/{task_id}
DELETE /tasks/{task_id}
POST /tasks/{task_id}/complete
POST /audio/upload
```

---

## 9. Test Voice Task Creation

Open the Talkify dashboard and click:

```text
🎙️ Record
```

Speak a command such as:

> "I want to update my Aadhaar number tomorrow and call my friend on Friday."

Click **Stop**.

The application will:

```text
Voice Recording
      ↓
Audio Upload
      ↓
Whisper Transcription
      ↓
Task Extraction
      ↓
Due Date + Priority Detection
      ↓
Pydantic Validation
      ↓
AI Confirmation Modal
```

Review the extracted tasks and click:

```text
Add All
```

The tasks will then be saved to the SQLite database and displayed in the Todo list.

---

## 🔐 Environment Variables

The current version of Talkify uses **local Whisper** and does not require an OpenAI API key for speech-to-text.

If API keys or other environment-specific configuration are added in future versions, they should be stored in a `.env` file and excluded from Git using `.gitignore`.

Example:

```text
.env
```

---

## 🗄️ Database

Talkify uses SQLite.

The database file is created automatically when the application starts:

```text
voicetask.db
```

The database contains the application's task records.

No separate database server is required for local development.

---

## 🛑 Stop the Server

To stop the FastAPI development server:

```text
Ctrl + C
```

---

## 🔄 Development Workflow

For development, the recommended workflow is:

```bash
source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

Changes to the Python backend will automatically reload because the server is running with `--reload`.


# Extra Notes
```python
routes/       → receives HTTP requests
services/     → application logic / AI logic
schemas/      → defines valid input/output
models/       → database structure
tests/        → tests
main.py       → starts the application
```
This is what task looks like in our database.
```python
Task
│
├── id
├── title
├── description
├── due_date
├── priority
└── completed
```
>**create_engine**: Manages the actual connection bridge between Python and your database (like SQLite or PostgreSQL). It handles the low-level communication and maintains a pool of reusable connections to keep the app fast.

>**sessionmaker**: Acts as a factory that generates Session objects. A session is your workspace for database queries—it tracks changes, lets you add or delete items, and commits those changes to the database when you are done.

Once you build the engine and session, your app can:

- Create tables
- Insert tasks
- Read tasks
- Update tasks
- Delete tasks

Tasks are grouped into:
- Today
- Tomorrow
- Later
- Urgent
```python
High-priority tasks appear under Urgent.
Tasks without dates appear under Later.
Each section shows its task count.
Existing All, Active, and Completed filters still work.
```
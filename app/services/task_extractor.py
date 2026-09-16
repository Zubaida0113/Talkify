import json
import os
import re
from datetime import date, datetime

from google import genai
from dateparser.search import search_dates
from dotenv import load_dotenv

from app.schemas.task import ExtractedTask

load_dotenv()


def extract_priority(text: str) -> str:
    """Determine task priority from keywords."""
    text = (text or "").lower()

    high_keywords = [
        "urgent",
        "urgently",
        "asap",
        "important",
        "immediately",
        "critical",
        "high priority",
        "must do",
        "top priority",
    ]

    low_keywords = [
        "low priority",
        "whenever possible",
        "not urgent",
        "when possible",
        "no rush",
        "later",
    ]

    for keyword in high_keywords:
        if keyword in text:
            return "high"

    for keyword in low_keywords:
        if keyword in text:
            return "low"

    return "medium"


def _parse_date_value(value):
    """Normalize ISO strings, datetime objects, and natural language dates."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None

    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        pass

    matches = search_dates(text, settings={"PREFER_DATES_FROM": "future"})
    if matches:
        return matches[0][1].date()

    return None


def extract_due_date(text: str):
    """Extract a date from natural language text."""
    return _parse_date_value(text)


def clean_title(text: str) -> str:
    """Remove priority and date phrases from the task title."""
    text = re.sub(
        r"\b(urgently|urgent|asap|immediately|critical|important|"
        r"high priority|must do|top priority|low priority|"
        r"whenever possible|not urgent|when possible|no rush)\b",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\b(by\s+)?(today|tomorrow|monday|tuesday|wednesday|"
        r"thursday|friday|saturday|sunday)\b",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^(i\s+need\s+to|i\s+have\s+to|i\s+should|i\s+want\s+to)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(r"\s+", " ", text).strip(" -:;,. ")
    return text.strip()


def _normalize_task_object(task: dict) -> dict | None:
    if not isinstance(task, dict):
        return None

    title = str(task.get("title") or task.get("name") or "").strip()
    description = task.get("description")
    if description is not None:
        description = str(description).strip() or None

    if not title:
        return None

    due_date = _parse_date_value(task.get("due_date") or task.get("date") or task.get("due"))
    priority = str(task.get("priority") or "medium").strip().lower()
    if priority not in {"low", "medium", "high"}:
        priority = extract_priority(f"{title} {description or ''}")

    return {
        "title": title,
        "description": description,
        "due_date": due_date,
        "priority": priority,
    }


def call_llm_task_parser(transcript: str) -> list[dict]:
    """Send the transcript to Gemini and ask it to return structured tasks."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY is not configured")

    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    client = genai.Client(api_key=api_key)
    today = date.today().isoformat()

    prompt = f"""
You are a task extraction assistant.
Convert the spoken transcript into a clean list of action items.

Rules:
- Return only valid JSON.
- Each task must have: title, description, due_date, priority.
- focus on action items, not narration or filler words.
- fix grammar and phrasing so each task reads naturally.
- infer the date in ISO format like 2026-09-20 or null if no date is mentioned.
- Today is {today}. Resolve relative dates such as "today", "tomorrow", and "next Friday" from this date.
- Return due_date as an ISO date based on that reference date.
- infer priority as low, medium, or high.
- do not split a single action item into multiple tasks just because the sentence says "and".
- if there are multiple tasks, return a JSON array.

Transcript:
{transcript}
"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "temperature": 0.2,
            "response_mime_type": "application/json",
        },
    )

    content = getattr(response, "text", "")
    if not content:
        raise RuntimeError("Gemini returned an empty response")

    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)
    data = json.loads(cleaned)

    if isinstance(data, dict) and "tasks" in data:
        data = data["tasks"]

    if not isinstance(data, list):
        raise ValueError("Gemini response was not a list of tasks")

    parsed_tasks = []
    for item in data:
        normalized = _normalize_task_object(item)
        if normalized:
            parsed_tasks.append(normalized)

    return parsed_tasks


def _fallback_extract_tasks(transcript: str) -> list[dict]:
    """Heuristic parser that avoids brittle splitting on 'and'."""
    chunks = re.split(r"(?<=[.!?])\s+|\s*;\s*|\s*\.\s*\n", transcript.strip())
    task_candidates = []

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        for separator in [" and ", " also "]:
            if separator in chunk.lower():
                nested = [part.strip() for part in re.split(rf"\s*{re.escape(separator)}\s*", chunk, flags=re.IGNORECASE)]
                task_candidates.extend(part for part in nested if part)
                break
        else:
            task_candidates.append(chunk)

    tasks = []
    for part in task_candidates:
        part = part.strip(" -:;,. ")
        if not part:
            continue

        priority = extract_priority(part)
        due_date = _parse_date_value(part)
        title = clean_title(part)
        if title:
            tasks.append({
                "title": title,
                "description": None,
                "due_date": due_date,
                "priority": priority,
            })

    return tasks


def extract_tasks(transcript: str) -> list[dict]:
    """Convert a voice transcript into structured tasks using an LLM when available."""
    if transcript is None:
        return []

    transcript = transcript.strip()
    if not transcript:
        return []

    try:
        llm_parser = globals().get("call_llm_task_parser")
        if llm_parser is not None:
            parsed_tasks = llm_parser(transcript)
            if parsed_tasks:
                normalized = []
                for task in parsed_tasks:
                    normalized_task = _normalize_task_object(task)
                    if normalized_task:
                        normalized.append(normalized_task)
                if normalized:
                    return normalized
    except Exception:
        pass

    fallback_tasks = _fallback_extract_tasks(transcript)
    normalized = []
    for task in fallback_tasks:
        normalized_task = _normalize_task_object(task)
        if normalized_task:
            normalized.append(normalized_task)
    return normalized


def validate_tasks(tasks: list[dict]) -> list[ExtractedTask]:
    """Validate extracted tasks using Pydantic."""
    validated_tasks = []

    for task in tasks:
        validated_task = ExtractedTask(**task)
        validated_tasks.append(validated_task)

    return validated_tasks

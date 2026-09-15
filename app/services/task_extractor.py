import re
from dateparser.search import search_dates
from app.schemas.task import ExtractedTask

def extract_priority(text: str) -> str:
    """
    Determine task priority from keywords.
    """

    text = text.lower()

    high_keywords = [
        "urgent",
        "urgently",
        "asap",
        "important",
        "immediately",
        "critical",
        "high priority",
        "must do",
        "top priority"
    ]

    low_keywords = [
        "low priority",
        "whenever possible",
        "not urgent",
        "when possible",
        "no rush",
        "later"
    ]

    for keyword in high_keywords:
        if keyword in text:
            return "high"

    for keyword in low_keywords:
        if keyword in text:
            return "low"

    return "medium"


def extract_due_date(text: str):
    """
    Extract a date from natural language text.
    """

    matches = search_dates(
        text,
        settings={
            "PREFER_DATES_FROM": "future"
        }
    )

    if matches:
        return matches[0][1].date()

    return None


def clean_title(text: str) -> str:
    """
    Remove priority and date phrases from the task title.
    """

    # Remove priority phrases
    text = re.sub(
        r"\b(urgently|urgent|asap|immediately|critical|important|"
        r"high priority|must do|top priority|low priority|"
        r"whenever possible|not urgent|when possible|no rush)\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove date phrases
    text = re.sub(
        r"\b(by\s+)?(today|tomorrow|monday|tuesday|wednesday|"
        r"thursday|friday|saturday|sunday)\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_tasks(transcript: str) -> list[dict]:
    """
    Convert a voice transcript into structured tasks.
    """

    # Split into separate tasks.
    # Keep the spaces around "and".
    parts = re.split(
        r",\s*|\s+and\s+",
        transcript,
        flags=re.IGNORECASE
    )

    tasks = []

    for part in parts:

        part = part.strip()

        if not part:
            continue

        priority = extract_priority(part)
        due_date = extract_due_date(part)

        # Remove common introductory phrases
        part = re.sub(
            r"^(i\s+need\s+to|i\s+have\s+to|i\s+should|i\s+want\s+to)\s+",
            "",
            part,
            flags=re.IGNORECASE
        )

        # Remove priority/date information from title
        title = clean_title(part)

        if title:
            tasks.append({
                "title": title,
                "description": None,
                "due_date": due_date,
                "priority": priority
            })

    return tasks

def validate_tasks(tasks: list[dict]) -> list[ExtractedTask]:
    """
    Validate extracted tasks using Pydantic.
    """

    validated_tasks = []

    for task in tasks:
        validated_task = ExtractedTask(**task)
        validated_tasks.append(validated_task)

    return validated_tasks
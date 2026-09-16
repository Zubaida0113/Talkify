from app.services.task_extractor import extract_tasks


def test_extract_tasks_uses_llm_when_available(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    def fake_llm_parser(transcript: str):
        assert "project update" in transcript.lower()
        return [
            {
                "title": "Send project update email",
                "description": "Follow up with the client about the proposal.",
                "due_date": "2026-09-20",
                "priority": "high",
            }
        ]

    monkeypatch.setattr("app.services.task_extractor.call_llm_task_parser", fake_llm_parser)

    tasks = extract_tasks("Send project update email by September 20 and call the client urgently")

    assert len(tasks) == 1
    assert tasks[0]["title"] == "Send project update email"
    assert tasks[0]["priority"] == "high"
    assert str(tasks[0]["due_date"]) == "2026-09-20"


def test_extract_tasks_falls_back_to_heuristics_when_llm_unavailable(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("app.services.task_extractor.call_llm_task_parser", None)

    tasks = extract_tasks("Finish the sprint plan by Friday. Email the client tomorrow.")

    assert len(tasks) >= 2
    titles = {task["title"].lower() for task in tasks}
    assert any("sprint" in title for title in titles)
    assert any("email" in title for title in titles)

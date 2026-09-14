from datetime import date
from pydantic import BaseModel

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: date | None = None
    priority: str = "medium"

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    due_date: date | None
    priority: str
    completed: bool

    class Config:
        from_attributes = True
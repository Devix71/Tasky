from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional

class TaskReminderBase(BaseModel):
    """Base model with shared attributes."""
    time_to_run: datetime = Field(..., example="2025-12-31T23:59:59Z")
    assignee: str = Field(..., max_length=100, example="john.doe@example.com")
    task_content: str = Field(..., example="Submit the quarterly report.")
    reminder_type: Literal['Email', 'Slack'] = Field(..., example="Email")

class TaskReminderCreate(TaskReminderBase):
    """Model for creating a new task."""
    created_by: str = Field(..., max_length=100, example="jane.doe@example.com")

class TaskReminderUpdate(BaseModel):
    """Model for updating a task. All fields are optional."""
    time_to_run: Optional[datetime] = Field(None, example="2026-01-15T10:00:00Z")
    assignee: Optional[str] = Field(None, max_length=100, example="new.assignee@example.com")
    task_content: Optional[str] = Field(None, example="Update the quarterly report with new figures.")
    reminder_type: Optional[Literal['Email', 'Slack']] = Field(None, example="Slack")
    modified_by: str = Field(..., max_length=100, example="admin.user@example.com")

class TaskReminder(TaskReminderBase):
    """Model for reading task data from the API."""
    id: int
    created_at: datetime
    modified_at: datetime
    created_by: str
    modified_by: Optional[str] = None

    class Config:
        from_attributes = True
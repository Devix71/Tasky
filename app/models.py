import enum
from datetime import datetime
from typing import Optional

from sqlmodel import Field as SQLModelField, SQLModel
from pydantic import BaseModel, Field as PydanticField

class ReminderType(str, enum.Enum):
    EMAIL = "Email"
    SLACK = "Slack"


# --- DATABASE MODEL ---
class TaskReminder(SQLModel, table=True):
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    time_to_run: datetime
    assignee: str = SQLModelField(max_length=100)
    task_content: str
    reminder_type: ReminderType
    created_at: datetime = SQLModelField(default_factory=datetime.utcnow, nullable=False)
    modified_at: datetime = SQLModelField(default_factory=datetime.utcnow, nullable=False)
    created_by: str = SQLModelField(max_length=100)
    modified_by: Optional[str] = SQLModelField(default=None, max_length=100)


# --- API MODELS ---
# MUST use PydanticField.

class TaskReminderBase(BaseModel):
    """Base model with shared attributes and API examples."""
    time_to_run: datetime = PydanticField(..., example="2025-12-31T23:59:59Z")
    assignee: str = PydanticField(..., max_length=100, example="john.doe@example.com")
    task_content: str = PydanticField(..., example="Submit the quarterly report.")
    reminder_type: ReminderType = PydanticField(..., example=ReminderType.EMAIL)

class TaskReminderCreate(TaskReminderBase):
    """Model for creating a new task (API input)."""
    created_by: str = PydanticField(..., max_length=100, example="jane.doe@example.com")

class TaskReminderUpdate(BaseModel):
    """Model for updating a task (API input). All fields are optional."""
    time_to_run: Optional[datetime] = PydanticField(None, example="2026-01-15T10:00:00Z")
    assignee: Optional[str] = PydanticField(None, max_length=100, example="new.assignee@example.com")
    task_content: Optional[str] = PydanticField(None, example="Update the quarterly report with new figures.")
    reminder_type: Optional[ReminderType] = PydanticField(None, example=ReminderType.SLACK)
    modified_by: str = PydanticField(..., max_length=100, example="admin.user@example.com")

class TaskReminderRead(TaskReminderBase):
    """Model for reading task data from the API (API output)."""
    id: int
    created_at: datetime
    modified_at: datetime
    created_by: str
    modified_by: Optional[str] = None

    class Config:
        from_attributes = True
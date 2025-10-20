import enum
from datetime import datetime, timezone
from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel, Field as PydanticField


class ReminderType(str, enum.Enum):
    EMAIL = "Email"
    SLACK = "Slack"


# --- DATABASE MODELS ---

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str
    
class TaskReminder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    time_to_run: datetime
    assignee: str = Field(max_length=100)
    task_content: str
    reminder_type: ReminderType

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    
    created_by: str = Field(max_length=100)
    modified_by: Optional[str] = Field(default=None, max_length=100)


# --- API MODELS ---

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class TaskReminderBase(BaseModel):
    time_to_run: datetime = PydanticField(..., example="2025-12-31T23:59:59Z")
    assignee: str = PydanticField(..., max_length=100, example="john.doe@example.com")
    task_content: str = PydanticField(..., example="Submit the quarterly report.")
    reminder_type: ReminderType = PydanticField(..., example=ReminderType.EMAIL)

class TaskReminderCreate(TaskReminderBase):
    created_by: str = PydanticField(..., max_length=100, example="jane.doe@example.com")

class TaskReminderUpdate(BaseModel):
    time_to_run: Optional[datetime] = PydanticField(None, example="2026-01-15T10:00:00Z")
    assignee: Optional[str] = PydanticField(None, max_length=100, example="new.assignee@example.com")
    task_content: Optional[str] = PydanticField(None, example="Update the quarterly report with new figures.")
    reminder_type: Optional[ReminderType] = PydanticField(None, example=ReminderType.SLACK)

class TaskReminderRead(TaskReminderBase):
    id: int
    created_at: datetime
    modified_at: datetime
    created_by: str
    modified_by: Optional[str] = None

    class Config:
        from_attributes = True
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from typing import List
from sqlmodel import Session, select
from datetime import datetime, timezone

from .models import TaskReminder, TaskReminderCreate, TaskReminderUpdate, TaskReminderRead
from .database import create_db_and_tables, get_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Creating database and tables...")
    create_db_and_tables()
    yield
    print("Application shutdown.")

# --- FastAPI App Definition ---

app = FastAPI(
    title="Task Reminder API",
    description="A containerized API to manage task reminders.",
    version="1.0.0",
    lifespan=lifespan
)

# --- API Endpoints (No changes needed here) ---

@app.post("/tasks/", response_model=TaskReminderRead, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task_reminder(task_data: TaskReminderCreate, session: Session = Depends(get_session)):
    db_task = TaskReminder.model_validate(task_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=List[TaskReminderRead], tags=["Tasks"])
def list_task_reminders(session: Session = Depends(get_session)):
    tasks = session.exec(select(TaskReminder)).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskReminderRead, tags=["Tasks"])
def show_task_reminder(task_id: int, session: Session = Depends(get_session)):
    task = session.get(TaskReminder, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskReminderRead, tags=["Tasks"])
def adjust_task_reminder(task_id: int, task_update_data: TaskReminderUpdate, session: Session = Depends(get_session)):
    task = session.get(TaskReminder, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    update_data = task_update_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    task.modified_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task_reminder(task_id: int, session: Session = Depends(get_session)):
    task = session.get(TaskReminder, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    session.delete(task)
    session.commit()
    return None
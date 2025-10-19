from fastapi import FastAPI, HTTPException, status
from typing import List, Dict
from datetime import datetime, timezone

from .schemas import TaskReminder, TaskReminderCreate, TaskReminderUpdate

app = FastAPI(
    title="Task Reminder API",
    description="A fully functional API to manage task reminders.",
    version="1.0.0"
)

# --- In-Memory Database ---
fake_db: Dict[int, TaskReminder] = {}
task_id_counter = 0

# --- API Endpoints ---

@app.post("/tasks/", response_model=TaskReminder, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task_reminder(task_data: TaskReminderCreate):
    """
    Create a new task reminder.
    """
    global task_id_counter
    task_id_counter += 1
    task_id = task_id_counter
    now = datetime.now(timezone.utc)

    new_task = TaskReminder(
        id=task_id,
        created_at=now,
        modified_at=now,
        **task_data.model_dump() 
    )
    fake_db[task_id] = new_task
    return new_task

@app.get("/tasks/", response_model=List[TaskReminder], tags=["Tasks"])
def list_task_reminders():
    """
    List all existing task reminders.
    """
    return list(fake_db.values())

@app.get("/tasks/{task_id}", response_model=TaskReminder, tags=["Tasks"])
def show_task_reminder(task_id: int):
    """
    Show details of a specific task reminder by its ID.
    """
    task = fake_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskReminder, tags=["Tasks"])
def adjust_task_reminder(task_id: int, task_update_data: TaskReminderUpdate):
    """
    Adjust an existing task reminder.
    """
    task = fake_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    update_data = task_update_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    task.modified_at = datetime.now(timezone.utc)
    fake_db[task_id] = task
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task_reminder(task_id: int):
    """
    Delete an existing task reminder by its ID.
    """
    if task_id not in fake_db:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    
    del fake_db[task_id]
    return None
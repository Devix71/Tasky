from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import List, Annotated

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlmodel import Session, select

from . import security
from .models import (
    User, UserCreate, UserRead,
    TaskReminder, TaskReminderCreate, TaskReminderUpdate, TaskReminderRead
)
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

# --- SECURITY SETUP ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- DEPENDENCY for getting the current user ---

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

# --- Create a reusable dependency for getting the current user ---
CurrentUser = Annotated[User, Depends(get_current_user)]


# --- AUTHENTICATION ENDPOINTS ---

@app.post("/token", tags=["Authentication"])
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=UserRead, tags=["Authentication"])
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    hashed_password = security.get_password_hash(user_data.password)
    db_user = User(username=user_data.username, hashed_password=hashed_password)
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
    except Exception:
        raise HTTPException(status_code=400, detail="Username already registered")
    return db_user


# --- PROTECTED TASK ENDPOINTS ---

@app.post("/tasks/", response_model=TaskReminderRead, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task_reminder(task_data: TaskReminderCreate, current_user: CurrentUser, session: Session = Depends(get_session)):

    if task_data.created_by != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create a task for another user.")
    
    db_task = TaskReminder.model_validate(task_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=List[TaskReminderRead], tags=["Tasks"])
def list_task_reminders(current_user: CurrentUser, session: Session = Depends(get_session)):

    tasks = session.exec(select(TaskReminder).where(TaskReminder.created_by == current_user.username)).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskReminderRead, tags=["Tasks"])
def show_task_reminder(task_id: int, current_user: CurrentUser, session: Session = Depends(get_session)):
    task = session.get(TaskReminder, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found")

    if task.created_by != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    return task

@app.put("/tasks/{task_id}", response_model=TaskReminderRead, tags=["Tasks"])
def adjust_task_reminder(task_id: int, task_update_data: TaskReminderUpdate, current_user: CurrentUser, session: Session = Depends(get_session)):
    task = session.get(TaskReminder, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found")

    if task.created_by != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")
        
    update_data = task_update_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
        
    task.modified_at = datetime.now(timezone.utc)
    task.modified_by = current_user.username
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task_reminder(task_id: int, current_user: CurrentUser, session: Session = Depends(get_session)):
    task = session.get(TaskReminder, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found")

    if task.created_by != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
        
    session.delete(task)
    session.commit()
    return None
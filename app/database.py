import os
from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = None

if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    # Case 1: Running in a local Docker container.
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
elif DATABASE_URL:
    # Case 2: Running in Azure.
    conn_str = f"mssql+pyodbc:///?odbc_connect={DATABASE_URL}"
    engine = create_engine(conn_str, echo=False)
else:
    # Case 3: Running locally without Docker (e.g., `poetry run uvicorn`).
    engine = create_engine(
        "sqlite:///database.db",
        connect_args={"check_same_thread": False}
    )


def create_db_and_tables():
    """
    Initializes the database by creating all tables defined by SQLModel models.
    This function is called once on application startup.
    """
    if engine:
        SQLModel.metadata.create_all(engine)

def get_session():
    """
    A FastAPI dependency that yields a new database session for each request.
    It ensures the session is always closed after the request is complete.
    """
    if engine:
        with Session(engine) as session:
            yield session
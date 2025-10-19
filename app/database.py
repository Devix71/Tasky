from sqlmodel import create_engine, SQLModel, Session

# For local development.
# The file will be created in the project root directory.
DATABASE_URL = "sqlite:///database.db"

engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """
    Initializes the database and creates all tables based on SQLModel models.
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency that provides a database session to API endpoints.
    It ensures the session is properly closed after the request is finished.
    """
    with Session(engine) as session:
        yield session
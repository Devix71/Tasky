import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from datetime import datetime, timezone
import uuid

from app.main import app, get_session

@pytest.fixture(name="client")
def client_fixture():
    # 1. Use an in-memory SQLite database for testing.
    connection = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}).connect()
    
    # 2. Create the tables in the in-memory database.
    SQLModel.metadata.create_all(connection)

    # 3. Define the dependency override.
    def override_get_session():
        with Session(connection) as session:
            yield session

    # 4. Apply the override to the FastAPI app.
    app.dependency_overrides[get_session] = override_get_session

    # 5. Yield the TestClient to the test function.
    yield TestClient(app)

    # 6. Remove the dependency override to clean up the app object.
    app.dependency_overrides.clear()
    
    # 7. Drop all tables.
    SQLModel.metadata.drop_all(connection)
    
    # 8. Close the connection.
    connection.close()


# --- The Test Function ---

def test_full_user_and_task_lifecycle(client: TestClient):
    """
    Tests the complete workflow:
    1. Create a user (with a unique ID).
    2. Log in to get a token.
    3. Create a task for that user.
    4. Update the task.
    5. Delete the task.
    6. Verify the task is gone.
    """
    unique_id = str(uuid.uuid4())[:8]
    test_username = f"tester_{unique_id}"
    test_password = "testpassword"

    # --- 1. User Creation ---
    response = client.post(
        "/users/",
        json={"username": test_username, "password": test_password},
    )
    assert response.status_code == 200, f"Failed to create user. Response: {response.text}"
    user_data = response.json()
    assert user_data["username"] == test_username

    # --- 2. User Login ---
    response = client.post(
        "/token",
        data={"username": test_username, "password": test_password},
    )
    assert response.status_code == 200, f"Failed to log in. Response: {response.text}"
    token_data = response.json()
    access_token = token_data["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # --- 3. Create Task ---
    response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "time_to_run": datetime.now(timezone.utc).isoformat(),
            "assignee": f"{test_username}@example.com",
            "task_content": "My first test task",
            "reminder_type": "Email",
            "created_by": test_username,
        },
    )
    assert response.status_code == 201, f"Failed to create task. Response: {response.text}"
    task_data = response.json()
    task_id = task_data["id"]

    # --- 4. Update Task ---
    updated_task_content = "This task has been updated"
    response = client.put(
        f"/tasks/{task_id}",
        headers=auth_headers,
        json={"task_content": updated_task_content},
    )
    assert response.status_code == 200, f"Failed to update task. Response: {response.text}"
    updated_task_data = response.json()
    assert updated_task_data["task_content"] == updated_task_content
    assert updated_task_data["modified_by"] == test_username

    # --- 5. Delete Task ---
    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204

    # --- 6. Verify Deletion ---
    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 404
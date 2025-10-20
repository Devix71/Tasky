# Task Reminder API

This repository contains a secure, containerized REST API for managing task reminders. The application is built with Python using the FastAPI framework and is designed for cloud deployment on Microsoft Azure.

The infrastructure is defined declaratively using Bicep, and the entire testing, build, and deployment process is automated with a CI/CD pipeline powered by GitHub Actions.

## ✨ Features

*   **Full CRUD Operations**: Create, Read, Update, and Delete task reminders.
*   **Secure**: Endpoints are protected using OAuth2 with JWT Bearer Tokens. Users can only access their own tasks.
*   **Database-backed**: Uses SQLModel for ORM and persists data in an Azure SQL Database.
*   **Infrastructure as Code (IaC)**: All required Azure resources are defined in Bicep for repeatable, automated deployments.
*   **Containerized**: The application is packaged as a Docker container for portability and consistency.
*   **Automated CI/CD**: A GitHub Actions workflow automatically tests, builds, and deploys the application on every push to the main branch.

## 🛠️ Tech Stack

*   **Backend**: Python 3.10, FastAPI, SQLModel
*   **Dependency Management**: Poetry
*   **Testing**: Pytest
*   **Cloud Platform**: Microsoft Azure
*   **Infrastructure**: Bicep, Azure CLI
*   **Containerization**: Docker, Azure Container Registry, Azure Container Instances
*   **CI/CD**: GitHub Actions

## 🚀 Getting Started

### Prerequisites

*   Python 3.10+
*   Poetry
*   Docker Desktop
*   Azure CLI
*   An active Azure Subscription

### Local Development and Testing

These steps allow you to run the application and the test suite on your local machine using a temporary SQLite database.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/<your-username>/<your-repo-name>.git
    cd <your-repo-name>
    ```

2.  **Install dependencies:**
    Poetry will create a virtual environment and install all required packages.
    ```bash
    poetry install
    ```

3.  **Run the tests:**
    To ensure everything is working correctly, run the automated test suite.
    ```bash
    poetry run pytest
    ```

4.  **Run the local server:**
    This will start the FastAPI application on `http://127.0.0.1:8000`. The server will automatically reload when you make code changes.
    ```bash
    poetry run uvicorn app.main:app --reload
    ```

5.  **Access the API documentation:**
    Open your browser and navigate to `http://127.0.0.1:8000/docs`.

## ☁️ Azure Deployment

The deployment is fully automated via the GitHub Actions CI/CD pipeline. To set it up for the first time, you need to configure your GitHub repository with secrets that allow it to authenticate with Azure.

### One-Time Setup for CI/CD

1.  **Log in to Azure CLI:**
    ```bash
    az login
    ```

2.  **Create a Service Principal:**
    This creates a dedicated identity for GitHub Actions to use. Replace `<SUBSCRIPTION_ID>` with your actual Azure Subscription ID.
    ```bash
    az ad sp create-for-rbac --name "GitHubActions-TaskReminder" --role contributor --scopes /subscriptions/<SUBSCRIPTION_ID> --sdk-auth
    ```

3.  **Configure GitHub Secrets:**
    In your GitHub repository, go to `Settings > Secrets and variables > Actions`. Create the following repository secrets:

    *   `AZURE_CREDENTIALS`: Paste the entire JSON output from the service principal command.
    *   `ACR_NAME`: The name of the Azure Container Registry that will be created (e.g., `cr` followed by a unique string). You can pre-determine this or add it after the first deployment.
    *   `AZURE_SQL_PASSWORD`: A strong password for your Azure SQL database.
    *   `JWT_SECRET_KEY`: A long, random string for signing JWTs. You can generate one with `python -c "import secrets; print(secrets.token_hex(32))"`.
    *   `RESOURCE_GROUP_NAME`: The name of the Azure Resource Group where resources will be deployed (e.g., `TaskReminderRG`).

Once these secrets are configured, any push to the `main` branch will automatically trigger the workflow to test, build, and deploy the application.

## 🎤 How to Invoke the Server

After deployment, the API is available at the FQDN provided as an output of the deployment. You can find this in the GitHub Actions log or in the Azure Portal on the Container Instance's overview page.

**Base URL:** `http://<placeholder>.azurecontainer.io:8000`

    
# Task Reminder API

This repository contains a secure, containerized REST API for managing task reminders. The application is built with Python using the FastAPI framework and is designed for cloud deployment on Microsoft Azure.

The infrastructure is defined declaratively using Bicep, and the entire testing, build, and deployment process is automated with a CI/CD pipeline powered by GitHub Actions.

## ✨ Features

*   **Full CRUD Operations:** Create, Read, Update, and Delete task reminders.
*   **Secure:** Endpoints are protected using OAuth2 with JWT Bearer Tokens. Users can only access their own tasks.
*   **Database-backed:** Uses SQLModel for ORM and persists data in an Azure SQL Database.
*   **Infrastructure as Code (IaC):** All required Azure resources are defined in Bicep for repeatable, automated deployments.
*   **Containerized:** The application is packaged as a Docker container for portability and consistency.
*   **Automated CI/CD:** A GitHub Actions workflow automatically tests, builds, and deploys the application on every push to the `main` branch.

## 🛠️ Tech Stack

*   **Backend:** Python 3.10, FastAPI, SQLModel
*   **Dependency Management:** Poetry
*   **Testing:** Pytest
*   **Cloud Platform:** Microsoft Azure
*   **Infrastructure:** Bicep, Azure CLI
*   **Containerization:** Docker, Azure Container Registry, Azure Container Instances
*   **CI/CD:** GitHub Actions

## 🚀 Getting Started

### Prerequisites

*   [Python 3.10+](https://www.python.org/)
*   [Poetry](https://python-poetry.org/)
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
*   An active Azure Subscription

### Local Development and Testing

These steps allow you to run the application and the test suite on your local machine using a temporary SQLite database.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/<your-username>/<your-repo-name>.git
    cd <your-repo-name>
    ```

2.  **Install dependencies:**
    Poetry will create a virtual environment and install all required packages.
    ```bash
    poetry install
    ```

3.  **Run the tests:**
    To ensure everything is working correctly, run the automated test suite.
    ```bash
    poetry run pytest
    ```

4.  **Run the local server:**
    This will start the FastAPI application on `http://127.0.0.1:8000`. The server will automatically reload when you make code changes.
    ```bash
    poetry run uvicorn app.main:app --reload
    ```

5.  **Access the API documentation:**
    Open your browser and navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## ☁️ Azure Deployment

The deployment is fully automated via the GitHub Actions CI/CD pipeline. To set it up for the first time, you need to configure your GitHub repository with secrets that allow it to authenticate with Azure.

### One-Time Setup for CI/CD

1.  **Log in to Azure CLI:**
    ```bash
    az login
    ```

2.  **Create a Service Principal:**
    This creates a dedicated identity for GitHub Actions to use. Replace `<SUBSCRIPTION_ID>` with your actual Azure Subscription ID.
    ```bash
    az ad sp create-for-rbac --name "GitHubActions-TaskReminder" --role contributor --scopes /subscriptions/<SUBSCRIPTION_ID> --sdk-auth
    ```

3.  **Configure GitHub Secrets:**
    In your GitHub repository, go to `Settings > Secrets and variables > Actions`. Create the following repository secrets:
    *   `AZURE_CREDENTIALS`: Paste the entire JSON output from the service principal command.
    *   `ACR_NAME`: The name of the Azure Container Registry that will be created by Bicep.
    *   `ACI_NAME`: The name of the Azure Container Instance that will be created by Bicep.
    *   `AZURE_SQL_PASSWORD`: A strong password for your Azure SQL database.
    *   `JWT_SECRET_KEY`: A long, random string for signing JWTs. You can generate one with `python -c "import secrets; print(secrets.token_hex(32))"`.
    *   `RESOURCE_GROUP_NAME`: The name of the Azure Resource Group where resources will be deployed (e.g., `TaskReminderRG`).

Once these secrets are configured, any push to the `main` branch will automatically trigger the workflow to test, build, and deploy the application.

---

## 🎤 How to Invoke the Server

After deployment, the API is available at the FQDN provided as an output of the deployment. You can find this in the GitHub Actions log or in the Azure Portal on the Container Instance's overview page.

**Base URL:** `http://<your-fqdn>.azurecontainer.io:8000`

### Authentication Workflow

All task-related endpoints are protected. You must first create a user and then obtain an authentication token.

#### 1. Create a User

Send a `POST` request to the `/users/` endpoint.

**Example using `curl`:**
```bash
curl -X 'POST' \
  'http://<your-fqdn>.azurecontainer.io:8000/users/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "myuser",
  "password": "mysecretpassword"
}'
```
**Expected Response (`200 OK`):**
```json
{
  "id": 1,
  "username": "myuser"
}
```

#### 2. Get an Access Token

Send a `POST` request to the `/token` endpoint using form data.

**Example using `curl`:**
```bash
curl -X 'POST' \
  'http://<your-fqdn>.azurecontainer.io:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=myuser&password=mysecretpassword'
```
**Expected Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}```
Copy the `access_token` value. You will need it for all subsequent requests.

---

### API Endpoint Reference

All endpoints listed below require an `Authorization: Bearer <your_access_token>` header.

#### `POST /tasks/` - Create a Task Reminder

**Example using `curl`:**
```bash
curl -X 'POST' \
  'http://<your-fqdn>.azurecontainer.io:8000/tasks/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <your_access_token>' \
  -H 'Content-Type: application/json' \
  -d '{
  "time_to_run": "2025-12-31T23:59:59Z",
  "assignee": "project.manager@example.com",
  "task_content": "Finalize Q4 report.",
  "reminder_type": "Slack",
  "created_by": "myuser"
}'
```
**Expected Response (`201 Created`):** Returns the full task object that was created.

#### `GET /tasks/` - List All Task Reminders

Retrieves a list of all task reminders created by the authenticated user.

**Example using `curl`:**
```bash
curl -X 'GET' \
  'http://<your-fqdn>.azurecontainer.io:8000/tasks/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <your_access_token>'
```

**Expected Response (`200 OK`):**
```json
[
  {
    "time_to_run": "2025-12-31T23:59:59Z",
    "assignee": "project.manager@example.com",
    "task_content": "Finalize Q4 report.",
    "reminder_type": "Slack",
    "id": 1,
    "created_at": "2025-10-20T21:30:00Z",
    "modified_at": "2025-10-20T21:30:00Z",
    "created_by": "myuser",
    "modified_by": null
  }
]
```

#### `GET /tasks/{task_id}` - Show Details of a Specific Task

Retrieves the details of a single task reminder by its unique ID. You can only retrieve tasks that you have created.

**Example using `curl`:**
```bash
curl -X 'GET' \
  'http://<your-fqdn>.azurecontainer.io:8000/tasks/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <your_access_token>'
```

**Expected Response (`200 OK`):**
```json
{
  "time_to_run": "2025-12-31T23:59:59Z",
  "assignee": "project.manager@example.com",
  "task_content": "Finalize Q4 report.",
  "reminder_type": "Slack",
  "id": 1,
  "created_at": "2025-10-20T21:30:00Z",
  "modified_at": "2025-10-20T21:30:00Z",
  "created_by": "myuser",
  "modified_by": null
}
```
**Error Response (`404 Not Found`):** If the task does not exist or does not belong to you.

#### `PUT /tasks/{task_id}` - Adjust an Existing Task Reminder

Updates the details of an existing task reminder. All fields in the request body are optional.

**Example using `curl` (updating only the content and assignee):**
```bash
curl -X 'PUT' \
  'http://<your-fqdn>.azurecontainer.io:8000/tasks/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <your_access_token>' \
  -H 'Content-Type: application/json' \
  -d '{
  "task_content": "Finalize Q4 report with new sales data.",
  "assignee": "finance.dept@example.com"
}'
```

**Expected Response (`200 OK`):** The full, updated task object.
```json
{
  "time_to_run": "2025-12-31T23:59:59Z",
  "assignee": "finance.dept@example.com",
  "task_content": "Finalize Q4 report with new sales data.",
  "reminder_type": "Slack",
  "id": 1,
  "created_at": "2025-10-20T21:30:00Z",
  "modified_at": "2025-10-20T21:45:10Z",
  "created_by": "myuser",
  "modified_by": "myuser"
}
```

#### `DELETE /tasks/{task_id}` - Delete an Existing Task Reminder

Permanently removes a task reminder from the system.

**Example using `curl`:**
```bash
curl -X 'DELETE' \
  'http://<your-fqdn>.azurecontainer.io:8000/tasks/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <your_access_token>'
```

**Expected Response (`204 No Content`):** An empty response body.
# Dockerfile

# 1. Use an official Python runtime as a parent image
FROM python:3.10-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Install system dependencies required by the SQL Server driver
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc-dev \
    # Clean up apt cache to keep the image small
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft repository for ODBC Driver using the secure method
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    # Clean up apt cache again
    && rm -rf /var/lib/apt/lists/*


# 4. Install Poetry
RUN pip install poetry

# 5. Copy only the dependency definition files
COPY poetry.lock pyproject.toml ./

# 6. Install project dependencies (without creating a venv)
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

# 7. Copy the rest of the application source code
COPY ./app ./app

# 8. Expose the port the app will run on
EXPOSE 8000

# 9. Define the command to run the app using gunicorn for production
# Added --preload to prevent worker race conditions on database initialization
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--preload", "-b", "0.0.0.0:8000", "app.main:app"]
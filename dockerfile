# 1. Base Image
FROM python:3.10-slim

# 2. Set WORKDIR
WORKDIR /app

# 3. System Dependencies (ODBC Driver, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# 4. Install a modern version of Poetry
RUN pip install "poetry>=1.2.0"

# 5. Copy dependency files
COPY poetry.lock pyproject.toml ./

# 6. Install dependencies using Poetry.
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

# 7. Correct the bcrypt installation once poetry is done.
RUN pip uninstall -y py-bcrypt bcrypt
RUN pip install "passlib>=1.7.4" "bcrypt==4.1.2" # Lock to a specific, known-good version

# 8. Copy application code
COPY ./app ./app

# 9. Expose Port
EXPOSE 8000

# 10. CMD
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--preload", "-b", "0.0.0.0:8000", "app.main:app"]
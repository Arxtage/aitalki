# backend/Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Set the working directory for the backend
WORKDIR /backend

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt ./

# Install dependencies with retries
RUN pip install --no-cache-dir pip setuptools wheel && \
    for i in {1..3}; do \
        pip install --no-cache-dir -r requirements.txt && break || sleep 15; \
    done

# Copy the backend code
COPY app ./app

# Copy the .env file into the container
COPY .env ./
COPY google-service-account-key.json ./

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

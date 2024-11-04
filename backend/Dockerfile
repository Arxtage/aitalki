# backend/Dockerfile
FROM python:3.12-slim

# Set the working directory for the backend
WORKDIR /backend

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY app ./app

# Copy the .env file into the container
COPY .env ./
COPY google-service-account-key.json ./

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

# Use a multi-stage build to first build the React app
FROM node:16 AS build

# Set the working directory for the frontend
WORKDIR /frontend

# Copy the package.json and package-lock.json
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY frontend/ .

# Build the React app
RUN npm run build

# Now, create the backend image
FROM python:3.12-slim

# Set the working directory for the backend
WORKDIR /backend

# Copy the requirements file and install dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/app ./app

# Copy the .env file into the container
COPY backend/.env ./
COPY backend/google-service-account-key.json ./

# Copy the built React app from the previous stage
COPY --from=build /frontend/build ./frontend/build

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

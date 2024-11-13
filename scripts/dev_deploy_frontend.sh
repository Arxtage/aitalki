#!/bin/bash

# Stop and remove any existing frontend containers
docker-compose down frontend

# Start only the frontend service without dependencies
docker-compose up frontend --no-deps

# Optional: Tail the logs for the frontend service
docker-compose logs -f frontend

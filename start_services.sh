#!/bin/bash

# Install Poetry globally
pip install poetry
poetry config virtualenvs.create false

# Set up the backend
echo "Setting up the backend..."
cd /code/backend
poetry install --no-interaction --no-ansi
poetry run uvicorn app.server:app --host 0.0.0.0 --port 8000 &

# Set up the frontend
echo "Setting up the frontend..."
cd /code/frontend
npm install
npm start &

# Keep the script running
wait

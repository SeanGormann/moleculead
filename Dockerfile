# Use the official Python image as the base image
FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Create directories for the frontend and backend
WORKDIR /code
RUN mkdir /code/frontend /code/backend

# Copy backend and frontend code into the container
COPY ./app /code/backend/app
COPY ./pyproject.toml ./poetry.lock* /code/backend/
COPY ./frontend_demo /code/frontend

# Copy the startup script into the container
COPY start_services.sh /code/

# Make the startup script executable
RUN chmod +x /code/start_services.sh

# Set the working directory to /code
WORKDIR /code

# Expose ports for backend and frontend
EXPOSE 8000 4444

# Run the startup script to install dependencies and start services
CMD ["/code/start_services.sh"]
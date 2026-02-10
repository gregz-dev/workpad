# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV WORKPAD_DATA_PATH=/data
ENV WORKPAD_STORAGE_TYPE=json

# Set work directory
WORKDIR /app

# Install system dependencies if any (none needed for basic flask/sqlite)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Copy requirements/setup (utilizing pip cache)
COPY pyproject.toml .
# Create a dummy setup.py if not exists, but we have one.
COPY setup.py .
COPY README.md .
COPY MANIFEST.in .

# Install dependencies (only)
# We install the package in editable mode or just dependencies?
# Let's install dependencies first for caching.
# But pyproject.toml requires full install usually.
# Simple approach: copy everything and install.
COPY workpad/ workpad/

# Install the package
RUN pip install .

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 5000

# Run commands
# We use flask run. In production use gunicorn.
# For this phase, flask run is fine or gunicorn if added to Deps.
# Let's stick to flask run as per docs "Flask setup".
CMD ["flask", "--app", "workpad.api:create_app", "run", "--host=0.0.0.0"]

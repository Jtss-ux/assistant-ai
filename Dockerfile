# Use official Python slim base image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source (includes pre-built frontend/dist)
COPY . .

# Render injects PORT at runtime (defaults to 10000); do NOT hardcode it here.
EXPOSE 10000
ENV PYTHONUNBUFFERED=1

# Start the FastAPI server
CMD ["python", "main.py"]

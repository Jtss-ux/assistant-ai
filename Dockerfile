# Use official Python slim base image
FROM python:3.11-slim

# Create a non-root user (Hugging Face specifically requires UID 1000)
RUN useradd -m -u 1000 user

# Set environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

# Create workdir and give ownership to the non-root user BEFORE switching
RUN mkdir -p $HOME/app && chown -R user:user $HOME
WORKDIR $HOME/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and change ownership to 'user' so SQLite DB can be written
COPY --chown=user:user . .

# Switch to the non-root user to avoid permission crashes on Serverless platforms
USER user

# Platform Port Configurations (Render defaults to 10000, HF defaults to 7860)
EXPOSE 10000
EXPOSE 7860

# Start the unified backend
CMD ["python", "main.py"]

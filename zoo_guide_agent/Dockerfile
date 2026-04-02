FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (none for now)

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ADK web UI usually runs on port 8000 or 8080 depending on --service_port
EXPOSE 8080

# Environment variables for the agent
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Command to run the ADK agent as a web service
# In Task 5, they use 'adk web' locally, but for Cloud Run it's usually the runner entry point
CMD ["python", "agent.py"]

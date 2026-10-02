FROM python:3.11-slim

# Install FFmpeg and required utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl unzip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Download Vosk model
RUN mkdir -p models && \
    curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip \
    -o /tmp/vosk-model.zip && \
    unzip -q /tmp/vosk-model.zip -d models && \
    rm /tmp/vosk-model.zip

# Render provides the PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
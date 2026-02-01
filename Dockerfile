FROM python:3.11-slim

WORKDIR /app

# Install git (needed for auto-detection)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY sync_stars.py .
COPY mcp_server.py .

# Create volume for output
VOLUME /app/output

# Run sync script by default
CMD ["python", "sync_stars.py"]

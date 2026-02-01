FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY sync_stars.py .
COPY mcp_server.py .

# Run sync script by default
CMD ["python", "sync_stars.py"]

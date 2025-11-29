FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=30s --retries=3 \
  CMD python -c "from detection import detector; print('Detector loaded:', detector is not None)" || exit 1

# Run the Slack bot
CMD ["python", "app.py"]

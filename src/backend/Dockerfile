FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (required for some Python packages like sentence-transformers)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# We don't copy the app code here because we will mount it as a volume for hot-reloading

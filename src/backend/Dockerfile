FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (required for some Python packages like sentence-transformers)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --default-timeout=1000 --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy the entire backend application code
COPY . /app

# Expose FastAPI application port
EXPOSE 8000

# Default startup command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

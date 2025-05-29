FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create virtual environment
RUN python -m venv /app/venv

# Activate virtual environment and upgrade pip
RUN /app/venv/bin/pip install --upgrade pip

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies in virtual environment
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data/resumes /app/data/faiss_index

# Set environment variables
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command (will use venv python)
CMD ["python", "app.py"]

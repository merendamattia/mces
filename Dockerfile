# Multi-stage Dockerfile for MCES application
# Stage 1: Base Python image with dependencies
FROM python:3.11-slim AS backend

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Set Python path
ENV PYTHONPATH=/app/backend

# Expose backend port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/api/generate', json={'num_nodes': 2, 'num_edges': 1})" || exit 1

# Run the Flask application
CMD ["python", "backend/app.py"]

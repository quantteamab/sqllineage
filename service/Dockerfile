# Multi-stage Dockerfile for SQLLineage FastAPI service

# Stage 1: Builder - Install dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - Create minimal image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Create app user (optional, for better security)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app/ /app/app/

# Note: sqllineage is installed from parent directory during build
# For standalone deployment, add sqllineage to requirements.txt
# For local development with source, build from parent directory with:
# docker build -f service/Dockerfile -t sqllineage-api .

# If building from parent directory, copy and install sqllineage source
COPY sqllineage/ /app/sqllineage_src/sqllineage/
COPY pyproject.toml /app/sqllineage_src/
RUN cd /app/sqllineage_src && pip install --no-cache-dir -e .

# Switch to app user
USER appuser

# Expose port (default 8000, configurable via environment)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${SERVICE_PORT:-8000}/health').raise_for_status()"

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

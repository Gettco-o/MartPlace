# Multi-stage Dockerfile for MartPlace

# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system build dependencies required for C extensions/drivers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final Runtime ---
FROM python:3.11-slim AS runner

WORKDIR /martplace

# Install runtime system libraries and healthcheck dependency
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=50055

# Create non-root user and set directory write permissions for SQLite journal files and logs
RUN groupadd -r appgroup && useradd -r -g appgroup -d /martplace appuser && \
    mkdir -p /martplace/logs && \
    chmod -R 777 /martplace

# Copy application source code with proper ownership
COPY --chown=appuser:appgroup . /martplace

# Switch to security-hardened non-root user
USER appuser

EXPOSE 50055

# Container health check monitoring the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:50055/health || exit 1

# Default command: run database migrations and start the Quart server
CMD ["sh", "-c", "alembic upgrade head && python main.py serve"]
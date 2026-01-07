# ============================================
# TRAVEL PLATFORM - DOCKER MULTI-STAGE BUILDER
# ============================================

# ------------- Stage 1: Base -------------
FROM python:3.10-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.6.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# ------------- Stage 2: Dependencies -------------
FROM base AS dependencies

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-dev --no-root

# ------------- Stage 3: Development -------------
FROM base AS development

# Install development dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/tmp

# Set permissions
RUN chmod +x /app/scripts/*.sh

# Expose ports
EXPOSE 8000 5678

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ------------- Stage 4: Builder -------------
FROM dependencies AS builder

# Copy application code
COPY . .

# Run tests (optional, can be skipped in CI)
# RUN pytest

# ------------- Stage 5: Production -------------
FROM python:3.10-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=builder /app /app

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/tmp \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables for production
ENV APP_ENV=production \
    PYTHONPATH=/app/src \
    PORT=8000 \
    GUNICORN_WORKERS=4 \
    GUNICORN_THREADS=2 \
    GUNICORN_TIMEOUT=120 \
    GUNICORN_GRACEFUL_TIMEOUT=30 \
    GUNICORN_KEEPALIVE=5

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with gunicorn in production
CMD ["gunicorn", "src.main:app", \
     "--workers", "4", \
     "--threads", "2", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]

# ------------- Stage 6: Bot Service -------------
FROM production AS bot

# Set environment variables for bot
ENV SERVICE_TYPE=bot \
    PYTHONPATH=/app/src

# Override command for bot service
CMD ["python", "-m", "src.bot.main"]

# ------------- Stage 7: Worker Service -------------
FROM production AS worker

# Set environment variables for worker
ENV SERVICE_TYPE=worker \
    PYTHONPATH=/app/src

# Override command for celery worker
CMD ["celery", "-A", "src.workers.celery:celery_app", "worker", \
     "--loglevel=info", \
     "--concurrency=4", \
     "--hostname=worker@%h"]

# ------------- Stage 8: Beat Service -------------
FROM production AS beat

# Set environment variables for beat
ENV SERVICE_TYPE=beat \
    PYTHONPATH=/app/src

# Override command for celery beat
CMD ["celery", "-A", "src.workers.celery:celery_app", "beat", \
     "--loglevel=info", \
     "--scheduler=celery.beat.PersistentScheduler"]

# ------------- Stage 9: Flower Service -------------
FROM production AS flower

# Install flower
RUN pip install flower

# Set environment variables for flower
ENV SERVICE_TYPE=flower \
    PYTHONPATH=/app/src

# Expose flower port
EXPOSE 5555

# Override command for flower
CMD ["celery", "-A", "src.workers.celery:celery_app", "flower", \
     "--port=5555", \
     "--broker=${CELERY_BROKER_URL}", \
     "--basic_auth=admin:admin123"]

# ------------- Stage 10: CI/CD -------------
FROM base AS ci

# Install CI dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

# Copy application code
COPY . .

# Create test directories
RUN mkdir -p /app/test-reports /app/coverage

# Run tests and generate reports
CMD ["pytest", \
     "--junitxml=/app/test-reports/junit.xml", \
     "--cov=src", \
     "--cov-report=xml:/app/coverage/coverage.xml", \
     "--cov-report=html:/app/coverage/html"]

# ------------- Labels -------------
LABEL maintainer="Travel Platform Team <dev@travelplatform.com>" \
      version="1.0.0" \
      description="Enterprise Telegram travel search & booking platform" \
      org.label-schema.schema-version="1.0" \
      org.label-schema.name="travel-platform" \
      org.label-schema.description="Travel Platform Application" \
      org.label-schema.vendor="Travel Platform" \
      org.label-schema.url="https://travelplatform.com" \
      org.label-schema.vcs-url="https://github.com/travel-platform/travel-platform"

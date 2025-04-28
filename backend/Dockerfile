# Multi-stage Dockerfile for Budget Buddy

# Base image with common setup
FROM python:3.13-slim AS base
WORKDIR /app
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Install uv package manager
RUN pip install --upgrade pip && \
    pip install uv

# Stage for generating requirements.txt
FROM base AS requirements
WORKDIR /app
COPY backend/pyproject.toml .
# Generate requirements.txt using uv
RUN uv pip compile pyproject.toml --output-file requirements.txt

# Stage for installing dependencies
FROM base AS deps
WORKDIR /app
COPY --from=requirements /app/requirements.txt .
RUN pip install -r requirements.txt

# Production build
FROM deps AS production
WORKDIR /app
# Copy src folder and alembic config
COPY backend/src ./src
COPY backend/alembic.ini .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development build
FROM base AS development
WORKDIR /app
COPY backend/pyproject.toml .
ENV UV_NO_CACHE=1
ENV PYTHONDONTWRITEBYTECODE=1
# Install in dev mode with uv
RUN uv sync
# Copy src folder and alembic config
COPY backend/src ./src
COPY backend/alembic.ini .
EXPOSE 8000

CMD ["uv", "run", "src/main.py"]

# Subscriber build for RabbitMQ event processing
FROM deps AS subscriber
WORKDIR /app
# Copy src folder and alembic config
COPY backend/src ./src
COPY backend/alembic.ini .
# Run the subscriber main script
CMD ["python", "-m", "src.subscriber_main"]

# Celery worker build
FROM deps AS celeryworker
WORKDIR /app
# Copy src folder and alembic config
COPY backend/src ./src
COPY backend/alembic.ini .
# Run celery worker for budget_buddy_tasks
CMD ["celery", "-A", "src.celery_app.app", "flower", "--port=5555"]

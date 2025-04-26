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
RUN uv pip install -r requirements.txt

# Production build
FROM deps AS production
WORKDIR /app
# Copy only src folder
COPY backend/src ./src
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development build
FROM base AS development
WORKDIR /app
COPY backend/pyproject.toml .
# Install in dev mode with uv
RUN uv pip install -e .
# Copy only src folder
COPY backend/src ./src
EXPOSE 8000
CMD ["uv", "run", "src/main.py"]

# Subscriber build
FROM deps AS subscriber
WORKDIR /app
# Copy only src folder
COPY backend/src ./src
# Placeholder for subscriber script that doesn't exist yet
CMD ["echo", "Subscriber service would run here"]

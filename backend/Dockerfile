# syntax=docker/dockerfile:1.7
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ── Dependencies ──────────────────────────────────────────────────────────────
FROM base AS deps
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install ".[dev]"

# ── Development image ─────────────────────────────────────────────────────────
FROM deps AS development
COPY . .
EXPOSE 8000
CMD ["uvicorn", "asgi:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── Production image ──────────────────────────────────────────────────────────
FROM base AS production
COPY pyproject.toml .
RUN pip install --upgrade pip && pip install "."
COPY . .

# Non-root user for security
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "asgi:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

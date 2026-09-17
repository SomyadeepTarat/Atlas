# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:0.8.22 AS uv


FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=uv /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync \
    --frozen \
    --no-dev \
    --no-install-project


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

ENV PYTHONPATH=/app/src

RUN groupadd \
        --system \
        atlas \
    && useradd \
        --system \
        --gid atlas \
        --create-home \
        atlas

COPY --from=builder \
    /app/.venv \
    /app/.venv

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./
COPY pyproject.toml ./
COPY docker/backend-entrypoint.sh \
    /usr/local/bin/atlas-entrypoint
COPY docker/healthcheck.py \
    /app/docker/healthcheck.py

RUN chmod +x \
        /usr/local/bin/atlas-entrypoint \
    && chown -R atlas:atlas /app

USER atlas

EXPOSE 8000

ENTRYPOINT ["atlas-entrypoint"]

CMD ["uvicorn", "atlas.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
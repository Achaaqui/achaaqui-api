FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

# Keep dependencies outside /app so the source bind mount doesn't hide them.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY alembic.ini Makefile ./
COPY alembic ./alembic
COPY src ./src

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]

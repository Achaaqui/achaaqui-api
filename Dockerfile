FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Keep dependencies outside /app so the source bind mount doesn't hide them.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY src ./src

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "fastapi", "dev", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]

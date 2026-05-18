# syntax=docker/dockerfile:1.7
# ---------------------------------------------------------------------------
# Builder: resolve and install the locked environment with uv.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Layer 1: dependencies only (cached unless the lock changes).
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# ---------------------------------------------------------------------------
# Runtime: minimal, non-root, no build toolchain.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

RUN groupadd --system app && useradd --system --gid app --create-home app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PP_CONFIGS_DIR=/app/configs

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY configs ./configs

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import urllib.request as u,sys; sys.exit(0 if u.urlopen('http://localhost:8000/health').status==200 else 1)"]

CMD ["uvicorn", "price_predictor.serving.asgi:get_app", "--factory", \
     "--host", "0.0.0.0", "--port", "8000"]

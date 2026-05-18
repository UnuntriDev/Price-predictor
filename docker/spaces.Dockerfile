# syntax=docker/dockerfile:1.7
# ---------------------------------------------------------------------------
# Hugging Face Spaces (Docker SDK) image.
# One container, two processes via supervisord:
#   - Streamlit on :7860  (the public HF port)
#   - FastAPI   on :8000  (internal; Streamlit calls it over localhost)
# Postgres / MLflow / Prometheus / Grafana are NOT in this image - they
# only exist in docker-compose.yml for local runs (see README + ADR 0004).
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim AS runtime

RUN apt-get update \
    && apt-get install --no-install-recommends -y supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --create-home app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PP_CONFIGS_DIR=/app/configs \
    PP_API__PORT=8000 \
    PP_API__STREAMLIT_PORT=7860

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src ./src
COPY configs ./configs
COPY docker/supervisord.conf /etc/supervisor/conf.d/price-predictor.conf

RUN chown -R app:app /app
USER app
EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
    CMD ["python", "-c", "import urllib.request as u,sys; sys.exit(0 if u.urlopen('http://localhost:7860/_stcore/health').status==200 else 1)"]

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/price-predictor.conf"]

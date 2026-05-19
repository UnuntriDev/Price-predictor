.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help install browsers lint format type test check pre-commit \
        up down serve ui train scrape drift clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Create the locked virtual environment
	uv sync

browsers: ## Install the Chromium browser for the scraper (Playwright)
	uv run playwright install chromium

lint: ## Ruff lint
	uv run ruff check .

format: ## Ruff auto-format
	uv run ruff format .

type: ## mypy --strict on the package
	uv run mypy src/

test: ## Run the test suite
	uv run pytest

pre-commit: ## Run every pre-commit hook
	uv run pre-commit run --all-files

check: lint type test pre-commit ## Full local quality gate
	uv run ruff format --check .

up: ## Start the full local stack (pg/mlflow/prometheus/grafana/api/ui)
	docker compose up -d --build

down: ## Stop the local stack and drop volumes
	docker compose down -v

serve: ## Run the FastAPI service with autoreload
	uv run uvicorn price_predictor.serving.asgi:get_app --factory \
		--reload --host 0.0.0.0 --port 8000

ui: ## Run the Streamlit demo
	uv run streamlit run src/price_predictor/ui/streamlit_app.py \
		--server.port 7860

train: ## Train+register a model from the listings in Postgres
	uv run python scripts/train.py

scrape: browsers ## Run the Otodom crawl (needs Chromium via `make browsers`)
	uv run python scripts/scrape.py

drift: ## Drift gate + Evidently HTML report from Postgres listings
	uv run python -m price_predictor.monitoring.job

clean: ## Remove caches and build artifacts
	rm -rf .ruff_cache .mypy_cache .pytest_cache htmlcov .coverage \
		dist build **/__pycache__

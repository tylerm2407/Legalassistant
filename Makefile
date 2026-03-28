.PHONY: dev backend frontend install test lint format typecheck verify seed clean

## ─── Start ────────────────────────────────────────────────────────────────

# Start backend (port 8000)
dev:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Start FastAPI backend only (port 8000)
backend:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Start Next.js frontend only (port 3000)
frontend:
	cd web && npm run dev

## ─── Install ──────────────────────────────────────────────────────────────

# Install all dependencies
install:
	pip install -e ".[dev]"
	cd web && npm install

## ─── Quality gates ────────────────────────────────────────────────────────

# Run full test suite with coverage
test:
	python -m pytest tests/ -v --tb=short --cov=backend --cov-report=term-missing

# Run linters
lint:
	ruff check backend/ tests/
	ruff format --check backend/ tests/

# Auto-fix lint issues + format code
format:
	ruff check --fix backend/ tests/
	ruff format backend/ tests/

# Run type checkers
typecheck:
	uv run mypy backend/

# Run ALL quality gates — required before every commit
verify: lint test
	@echo ""
	@echo "All checks passed. Ready to commit."

## ─── Utilities ────────────────────────────────────────────────────────────

# Seed demo profile (Sarah Chen)
seed:
	python scripts/seed_demo.py

# Remove all build artifacts and caches
clean:
	find . -type d -name __pycache__ | xargs rm -rf
	find . -type d -name .pytest_cache | xargs rm -rf
	find . -type d -name .mypy_cache | xargs rm -rf
	find . -name "*.pyc" -delete
	find . -name ".ruff_cache" -type d | xargs rm -rf

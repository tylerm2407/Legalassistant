.PHONY: dev test lint verify seed format install

dev:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

test:
	python -m pytest tests/ -v --tb=short --cov=backend --cov-report=term-missing

lint:
	ruff check backend/ tests/
	ruff format --check backend/ tests/

format:
	ruff check --fix backend/ tests/
	ruff format backend/ tests/

verify: lint test
	@echo "All checks passed."

seed:
	python scripts/seed_demo.py

install:
	pip install -e ".[dev]"

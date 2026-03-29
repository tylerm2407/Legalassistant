.PHONY: dev backend frontend install test lint format typecheck verify seed clean docker-build docker-up docker-down deploy-staging

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
	cd mobile && npm install

## ─── Quality gates ────────────────────────────────────────────────────────

# Run full test suite with coverage
test:
	python -m pytest tests/ -v --tb=short --cov=backend --cov-report=term-missing

# Run frontend tests
test-web:
	cd web && npm test -- --coverage --ci

# Run all tests (backend + frontend)
test-all: test test-web

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
	mypy backend/

# Run ALL quality gates — required before every commit
verify: lint test
	@echo ""
	@echo "All checks passed. Ready to commit."

## ─── Docker ─────────────────────────────────────────────────────────────

# Build all Docker images
docker-build:
	docker compose build

# Start all services (backend + redis + web)
docker-up:
	docker compose up -d
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Redis: localhost:6379"

# Stop all services
docker-down:
	docker compose down

## ─── Deployment ─────────────────────────────────────────────────────────

# Deploy backend to Railway (requires RAILWAY_TOKEN)
deploy-backend:
	railway up --service casemate-backend --detach

# Deploy frontend to Vercel (requires VERCEL_TOKEN)
deploy-frontend:
	cd web && vercel --prod

# Deploy mobile builds via EAS
deploy-mobile:
	cd mobile && eas build --platform all --profile production --non-interactive

# Full deployment (backend + frontend)
deploy: deploy-backend deploy-frontend
	@echo "Deployment complete."

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

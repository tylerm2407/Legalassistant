# Dockerfile — Production-grade CaseMate backend image
#
# Multi-stage build:
#   Stage 1 (builder): installs Python deps into a virtual env
#   Stage 2 (runtime): copies only the venv + app code, runs as non-root
#
# Build:  docker build -t casemate-backend .
# Run:    docker run -p 8000:8000 --env-file .env casemate-backend

# ---------------------------------------------------------------------------
# Stage 1: Builder — install dependencies
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build tools needed for some Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment so we can copy it cleanly to runtime
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies first (cache-friendly layer ordering)
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# ---------------------------------------------------------------------------
# Stage 2: Runtime — lean production image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 1000 casemate && \
    useradd --uid 1000 --gid casemate --shell /bin/bash --create-home casemate

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the application code (no dev files, no tests)
COPY backend/ backend/
COPY pyproject.toml .

# Switch to non-root user
USER casemate

EXPOSE 8000

# Healthcheck — verifies the /health endpoint responds
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run uvicorn with 2 workers for concurrency, proper signal handling
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

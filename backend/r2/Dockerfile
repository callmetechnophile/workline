# ==============================================================================
# Workline R2 AI, Agents & Research Microservice
# Production Slim Docker Container
# ==============================================================================

FROM python:3.12-slim

# Prevent bytecode generation and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=10002

WORKDIR /app

# Install security certificates & networking tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install isolated R2 dependencies first for layer caching
COPY backend/r2/requirements.txt /app/backend/r2/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/r2/requirements.txt

# Copy application source tree
COPY backend /app/backend
COPY packages /app/packages

# Create non-root unprivileged runtime user
RUN useradd -m -u 1000 workline && \
    chown -R workline:workline /app

USER workline

EXPOSE 10002

# Startup command for R2 internal worker
CMD ["sh", "-c", "uvicorn backend.r2.main:app --host 0.0.0.0 --port ${PORT:-10002}"]

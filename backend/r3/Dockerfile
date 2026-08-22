# ==============================================================================
# Workline R3 Knowledge Infrastructure & Database Service
# Production Slim Docker Container
# ==============================================================================

FROM python:3.12-slim

# Prevent bytecode generation and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=10003

WORKDIR /app

# Install security certificates & networking tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install isolated R3 dependencies first for layer caching
COPY backend/r3/requirements.txt /app/backend/r3/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/r3/requirements.txt

# Copy application source tree
COPY backend /app/backend
COPY packages /app/packages
COPY cli /app/cli

# Create non-root unprivileged runtime user
RUN useradd -m -u 1000 workline && \
    chown -R workline:workline /app

USER workline

EXPOSE 10003

# Startup command for R3 internal knowledge worker
CMD ["sh", "-c", "uvicorn backend.r3.main:app --host 0.0.0.0 --port ${PORT:-10003}"]

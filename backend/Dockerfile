# ==============================================================================
# Workline R1 Core Gateway & Lifecycle Orchestrator
# Production Docker Container
# ==============================================================================

FROM python:3.12-slim

# Prevent generation of .pyc files and enable unbuffered streaming stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=10000

WORKDIR /app

# Install security certificates & system prerequisites
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for optimal layer caching
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application source trees
COPY backend /app/backend
COPY cli /app/cli
COPY packages /app/packages

# Create unprivileged non-root runtime user for security compliance
RUN useradd -m -u 1000 workline && \
    chown -R workline:workline /app

USER workline

EXPOSE 10000

# Start R1 Core Gateway using dynamic $PORT injected by Render or default 10000
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]

# ---------- Builder stage ----------
FROM python:3.11 AS builder
WORKDIR /app

# Install build dependencies only once to leverage Docker layer caching
COPY ../requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application source
COPY .. .

# ---------- Runtime stage ----------
FROM python:3.11-slim AS runtime

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy installed site-packages from the builder layer
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:$PATH"

# Copy application code
COPY .. .

# Default command starts the core API; can be overridden via docker-compose "command:"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8008"]


EXPOSE 8008 8001

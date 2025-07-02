# ---------- Builder stage ----------
FROM python:3.12-slim AS builder
WORKDIR /app

# Installera systempaket för kompilering av dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installera Python-paket i virtuell miljö
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Kopiera bara requirements.txt först för att utnyttja Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------- Runtime stage ----------
FROM python:3.12-slim AS runtime

# Förhindra Python från att skriva .pyc filer och buffra stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Kopiera virtualenv från builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Kopiera applikationskod
COPY app/ ./app/
COPY data/ ./data/
COPY tests/ ./tests/
COPY scripts/ ./scripts/
COPY alembic/ ./alembic/
COPY alembic.ini .env.example README.md ./

# Skapa mapp för loggar med korrekta rättigheter
RUN mkdir -p logs && chmod 777 logs

# Healthcheck som körs var 30e sekund
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8008/ping || exit 1

# Standardkommando som startar core API; kan överridas via docker-compose "command:"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8008"]

# Exponera portar för både core API och pipeline server
EXPOSE 8008 8001

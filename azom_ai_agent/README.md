# AZOM AI Agent

**AZOM AI Agent** is a sophisticated containerized solution built with FastAPI, designed for real-time updated knowledge base integration and Large Language Model (LLM) capabilities. This project aims to provide advanced pipeline processing for installation guidance and product recommendations, specifically tailored for automotive contexts like AZOM installations in vehicles.

## Key Features

- **FastAPI Server**: Provides robust API endpoints for health checks, pipeline processing, and administrative tasks.
- **Pipeline Processing**: Includes orchestration, RAG- **Vector-store RAG (FAISS + MiniLM)** for context retrieval.
- **Knowledge, memory, and safety services** for full-stack installation guidance.
- **Frontend UI**: Modern React 18 + TypeScript + Vite dashboard with Tailwind CSS and shadcn/ui components.
- **Swedish NLP**: Custom utilities for processing Swedish language inputs to extract relevant information like car models.
- **OpenWebUI / Ollama Integration** with `/chat/azom` endpoint and optional Groq fallback.

## Project Structure

```
azom_ai_agent/
├── app/
│   ├── pipelineserver/
│   │   ├── pipeline_app/
│   │   │   ├── services/              # Core services for orchestration, RAG, knowledge, etc.
│   │   │   ├── models/                # Pydantic models for data validation
│   │   │   └── utils/                 # Utilities for Swedish NLP and caching
│   │   └── tests/                     # Test suite for the pipeline server
├── data/
│   ├── knowledge_base/                # Storage for knowledge base files
│   ├── embeddings/                    # Pre-computed embeddings for RAG
│   └── prompts/                       # Prompt templates for LLM interactions
├── docker/                            # Docker configuration for containerization
├── scripts/                           # Utility scripts for automation and testing
└── tests/                             # Additional test suites
```

## Services

This repository contains two FastAPI applications:

| Service | Module | Purpose | Default Port |
|---------|--------|---------|--------------|
| **Core API** | `app.main:app` | Public endpoints for health-checks, diagnosis and knowledge management | **8000** |
| **Pipeline Server** | `app.pipelineserver.pipeline_app.main:app` | Installation, RAG chat & admin endpoints | **8001** |

Run them locally in separate shells (or via Docker-compose):

```bash
# Core API
uvicorn app.main:app --reload            # http://localhost:8000

# Pipeline server
uvicorn app.pipelineserver.pipeline_app.main:app --port 8001 --reload   # http://localhost:8001
```

## Modes: Light vs Full

The agent supports two runtime modes that are propagated end-to-end via the `X-AZOM-Mode` header (or `?mode=` query param):

- **Light mode**
  - RAG/embeddings disabled → system prompt only (`app/core/feature_flags.py: rag_enabled`, `allow_embeddings`).
  - External LLMs disabled; backend forced to OpenWebUI/Ollama (`get_llm_client()` in `app/pipelineserver/pipeline_app/services/llm_client.py`).
  - LLM timeout: 10s (`llm_timeout_seconds`).
  - Payload cap: 8 KB for chat message (`payload_cap_bytes`) enforced in `chat_with_azom()` (`app/pipelineserver/pipeline_app/main.py`).
  - Response echoes mode header `X-AZOM-Mode` (see `app/middlewares/mode.py`).

- **Full mode** (default)
  - RAG enabled; embeddings allowed.
  - External LLMs allowed (e.g., Groq) if configured.
  - LLM timeout: 30s. Payload cap: 32 KB.

How mode is set/flowing:

- Frontend stores current mode and attaches `X-AZOM-Mode` in all requests via `getModeHeaders()` (`frontend/src/lib/mode.ts`) used by `frontend/src/services/api.ts`.
- Backend `ModeMiddleware` resolves mode from header or `?mode=` and sets `request.state.mode`, and echoes it back (`app/middlewares/mode.py`).
- Observability: request logs include mode (`app/middlewares/request_logging.py`), chat endpoint logs payload caps and RAG gating (`app/pipelineserver/pipeline_app/main.py`), and LLM backend selection/timeouts are logged (`llm_client.py`).

Example (curl):

```bash
curl -X POST http://localhost:8001/chat/azom \
  -H "Content-Type: application/json" \
  -H "X-AZOM-Mode: light" \
  -d '{"message":"Hur installerar jag AZOM?","car_model":"Volvo"}'
```

## Example requests:

```bash
curl http://localhost:8000/ping
curl -X POST http://localhost:8001/pipeline/install \
     -H "Content-Type: application/json" \
     -d '{"user_input":"Install antenna","car_model":"Volvo XC60"}'

# Chat endpoint
curl -X POST http://localhost:8001/chat/azom \
     -H "Content-Type: application/json" \
     -d '{"message": "Hur installerar jag AZOM?", "car_model": "Volvo"}'
```

## Quickstart

### Prerequisites  
* Python 3.12  
* Node 18+ / LTS (20) recommended (frontend)  
* Docker (optional for containerised run)

### 1. Clone & setup Python
```bash
git clone https://github.com/your-org/azom-ai-agent.git
cd azom-ai-agent
python -m venv .venv && . .venv/Scripts/activate
pip install -r requirements.txt
```

### 2. Environment
Copy `.env.example` → `.env` and adjust keys, ports and tokens. Viktiga variabler:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENWEBUI_API_URL` | `http://localhost:3000/api` | Base-URL till OpenWebUI/Ollama |
| `OPENWEBUI_API_KEY` | (empty) | Token om instansen är säkrad |
| `DATABASE_URL` | `sqlite:///./azom.db` | SQL-alchemy connection |
| `PROJECT_NAME` | `AZOM AI Agent` | Visas i OpenAPI |
| `LOG_LEVEL` | `INFO` | Root log level |
| `CORE_API_PORT` | `8000` | Port för core-api |
| `PIPELINE_API_PORT` | `8001` | Port för pipeline-server |

Extra RAG-beroenden:
```bash
pip install sentence-transformers faiss-cpu   # faiss-gpu om du har CUDA
```
Första starten kan ta ~30s när embeddings indexeras.

### 3. Start backend
```bash
uvicorn app.pipelineserver.pipeline_app.main:app --port 8001 --reload
```

### 4. Start frontend
```bash
cd azom_ai_agent/frontend
npm install
npm run dev         # http://localhost:5173 (dev proxy → 8001)

# Production build
npm run build       # Build to dist/
npm run preview     # Local preview på http://localhost:4173
```

### 5. Docker-compose (all-in-one)
```bash
docker compose up --build -d
```
Komponenter som startas:
* core-api (port 8000)
* pipeline-server (8001)
* frontend Vite preview (5173)
* valfri Postgres (5432) – aktivera i `docker/docker-compose.yml` via env-flag.

## Development

Refer to `coding-guidelines.md` för kodstandard. Viktiga kommandon:
```bash
ruff format .
ruff check .
mypy --strict
```
Kör DB-migrationer (om Postgres):
```bash
alembic upgrade head
```

## Testing

### Backend
```bash
pytest -q               # snabb
pytest --cov            # coverage-rapport
```
### Frontend
```bash
npm run test            # Vitest
```
Install pre-commit hooks:
```bash
pre-commit install
```
Hooks kör `ruff`, `mypy --strict`, format och tester.

## Contributing

1. Skapa `feature/<kort-beskrivning>`-branch.
2. Följ Conventional Commits (`feat:`, `fix:` …).
3. Öka test-coverage om du ändrar logik.
4. Öppna PR mot `main` – en review krävs.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

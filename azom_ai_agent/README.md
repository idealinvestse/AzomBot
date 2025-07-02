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

Example requests:

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
* Node 18+ (frontend)  
* Docker (optional for containerised run)

### 1. Clone & setup Python
```bash
git clone https://github.com/your-org/azom-ai-agent.git
cd azom-ai-agent
python -m venv .venv && . .venv/Scripts/activate
pip install -r requirements.txt
```

### 2. Environment
Copy `.env.example` → `.env` and adjust keys, ports and tokens.

Install extra RAG dependencies:
```bash
pip install sentence-transformers faiss-cpu
```

### 3. Start backend
```bash
uvicorn app.pipelineserver.pipeline_app.main:app --port 8001 --reload
```

### 4. Start frontend
```bash
cd azom_ai_agent/frontend
npm install
npm run dev   # http://localhost:5173
```

### 5. Docker-compose (all-in-one)
```bash
docker compose up --build -d
```

## Development

Refer to `coding-guidelines.md` for code standards. The full system specification is located in `docs/SystemSpecification.md`. Use `ruff`, `mypy --strict`, and Vitest/Pytest for test coverage (>80 %).

## Testing

Automated testing for all functions and endpoints is implemented. For more information on running tests, see the test documentation in the respective directories.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

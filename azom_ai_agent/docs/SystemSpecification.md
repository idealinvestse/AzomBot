# AZOM AI Agent – System Specification

_Last updated: 2025-06-25_

## 1 Overview
AZOM AI Agent är ett containeriserat fler-tjänst-system som erbjuder:
* **Core API** (FastAPI) för hälsokontroll, diagnostik och kunskapshantering.
* **Pipeline Server** (FastAPI) för installations- och supportflöden inklusive admin-gränssnitt.
* **Admin-front-end** (valfritt, Vite/React) för produkthantering och FAQ-underhåll.

Systemet är skrivet i Python 3.12, använder Pydantic v2, SQLAlchemy 2 och Uvicorn som ASGI-server. All logik täcks av >40 automatiska Pytest-tester.


## 2 High-level architecture
```
┌────────────┐   HTTP    ┌────────────┐      Async calls     ┌─────────────────┐
│  Clients   │◀────────▶│ Core API   │◀────────────────────▶│  Services layer │
└────────────┘           └────────────┘                      ├─ Knowledge      │
                        :8008                               ├─ RAG            │
                                                             ├─ Memory         │
┌────────────┐   HTTP    └─────────────────┘                 └─────────────────┘
│  Admin UI  │◀────────▶│ Pipeline Server │
└────────────┘           └───────────────┘
                        :8001
```

### 2.1 Containers
| Container            | Image (multi-stage) | Ports | Purpose                             |
|----------------------|---------------------|-------|-------------------------------------|
| **core_api**         | `azom_ai_agent`     | 8008  | Hälsokoll + kunskapsendpoints       |
| **pipeline_server**  | `azom_ai_agent`     | 8001  | Installations- & supportflöden      |

### 2.2 Packages & runtimes
* **Python** 3.12 slim-runtime
* **Node 18+** (vid front-end)
* **SQLite** (default) – replacable med Postgres.


## 3 Source tree
```
azom_ai_agent
├── app/                      # Core-API + utils
│   ├── api/                  # Routers (diagnose, health, knowledge)
│   ├── services/             # Knowledge, prompt utils, etc.
│   ├── main.py               # Core FastAPI entry
│   └── config.py             # BaseSettings (.env-driven)
│
├── app/pipelineserver/
│   ├── pipeline_app/
│   │   ├── main.py           # Pipeline FastAPI entry
│   │   ├── services/         # Orchestration, RAG, support
│   │   ├── models/           # Pydantic & ORM models
│   │   └── admin/            # Products/FAQ routers + FE
│   └── tests/                # 30+ pytest cases
│
├── data/                     # Embeddings, knowledge base
├── docker/                   # Dockerfile & compose
├── scripts/                  # Alembic, init-data
└── docs/                     # ← detta dokument
```

## 4 Configuration
Konfiguration läses av **pydantic-settings** från `.env`.

| Key                      | Default              | Beskrivning                                    |
|--------------------------|----------------------|------------------------------------------------|
| `APP_NAME`               | AZOM AI Agent        | Titel för core-API                             |
| `PORT` (core)            | 8008                 | Lyssningsport för Core API                     |
| `PORT` (pipeline)        | 8001                 | Lyssningsport för Pipeline Server              |
| `DEBUG`                  | false                | Aktiverar debug-läge                           |
| `OPENWEBUI_URL`          | http://localhost:3000| Bas-URL till OpenWebUI/Ollama                  |
| `OPENWEBUI_API_TOKEN`    | –                    | Bearer-token till OpenWebUI                    |
| `LLM_BACKEND`            | openwebui            | Välj backend (`openwebui`, `groq`, `openai`)   |
| `GROQ_API_KEY`           | –                    | API-nyckel för Groq (vid Full mode)            |
| `OPENAI_API_KEY`         | –                    | API-nyckel för OpenAI (vid Full mode)          |
| `OPENAI_BASE_URL`        | https://api.openai.com/v1 | Bas-URL (kan peka på kompatibel gateway) |
| `TARGET_MODEL`           | azom-se-general      | Standardmodell                                 |
| `CACHE_TTL_SECONDS`      | 3600                 | Generell cache-TTL                             |

För kompletta exempel se `.env.example`.


## 5 Build & Deployment
### 5.1 Docker Compose
```bash
# build & start båda API-tjänsterna
$ docker compose up --build -d
```
* Automatic health-checks via Compose.
* Konfigurerar volym `./data` i containrar.

### 5.2 CI/CD
Förslag: GitHub Actions-workflow som kör
```yaml
- uses: actions/checkout@v4
- name: Test
  run: pytest
- name: Build image
  run: docker build -t azom_ai_agent .
```


## 6 Runtime behaviour
* **Health** `/health` – returns `{status: "healthy"}`.
* **/ping** – core uptime & version.
* **/pipeline/install** – POST body `{user_input, car_model, user_experience}` → installations-rekommendation.
* **/api/v1/support** – support-Q&A.
* **/chat/azom** – (Pipeline Server) POST body `{message, car_model?}` → chat med RAG beroende på mode.
* **/api/v1/chat/azom** – (Core API) POST body `{prompt}` → generisk chat.
* **Admin endpoints (planerade)** `/admin/products`, `/admin/faq`, `/admin/troubleshooting` (CRUD) – ej implementerade i nuläget.

### 6.1 Modes: Light vs Full

Systemet stödjer två körlägen som styrs via headern `X-AZOM-Mode` (alternativt query `?mode=`). Båda apparna (Core API och Pipeline Server) registrerar `ModeMiddleware` (`app/middlewares/mode.py`) som läser in läget, sätter `request.state.mode` och ekar tillbaka `X-AZOM-Mode` i respons.

- **Light**
  - RAG/embeddings av (centralt via `app/core/feature_flags.py: rag_enabled/allow_embeddings`).
  - Externa LLM-backends av – fabriken `get_llm_client()` forcerar OpenWebUI/Ollama.
  - Striktare timeout till LLM: 10s (`llm_timeout_seconds`).
  - Mindre payload-tak för chat: 8 KB (`payload_cap_bytes`), 413 returneras om överskrids. Enforceras i `app/pipelineserver/pipeline_app/main.py`.

- **Full** (default)
  - RAG på; embeddings tillåtna.
  - Externa LLM-backends tillåtna (Groq och OpenAI) om konfigurerade.
  - Timeout till LLM: 30s. Payload cap: 32 KB.

Stödda LLM-backends:

- `openwebui` (default i Light; OpenAI-kompatibelt API mot OpenWebUI/Ollama)
- `groq` (Groq Cloud – OpenAI-kompatibel endpoint)
- `openai` (OpenAI – `https://api.openai.com/v1` eller kompatibel gateway via `OPENAI_BASE_URL`)

Exempel:

```bash
curl -X POST http://localhost:8001/chat/azom \
  -H "Content-Type: application/json" \
  -H "X-AZOM-Mode: light" \
  -d '{"message":"Hur installerar jag AZOM?","car_model":"Volvo"}'
```


## 7 Database
Default: SQLite-fil `azom_pipelines.db` skapas automatiskt.
Alembic migrering kan köras manuellt:
```bash
alembic upgrade head
```


## 8 Testing
```bash
pytest           # 40 tests, 100 % pass
pytest --cov=app --cov-report=html
```
Inkluderar asynkrona tester med `pytest-asyncio`.


## 9 Security & Best Practices
* Ruff (lint/format), Mypy (strict typing) och Bandit i dev-deps och pre-commit.
* CORS är globalt öppet – stäng till i prod.
* Tokens läses från miljö, aldrig hårdkodade.


## 10 Future work
* Postgres-service i Compose.
* Kubernetes Helm-chart.
* Full CI/CD-pipeline.
* E2E-tester mot admin-frontend.

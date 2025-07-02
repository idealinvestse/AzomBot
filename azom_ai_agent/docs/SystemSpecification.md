# AZOM AI Agent – System Specification

_Last updated: 2025-06-25_

## 1 Overview
AZOM AI Agent är ett containeriserat fler-tjänst-system som erbjuder:
* **Core API** (FastAPI) för hälsokontroll, diagnostik och kunskapshantering.
* **Pipeline Server** (FastAPI) för installations- och supportflöden inklusive admin-gränssnitt.
* **Admin-front-end** (valfritt, Vite/React) för produkthantering och FAQ-underhåll.

Systemet är skrivet i Python 3.11, använder Pydantic v2, SQLAlchemy 2 och Uvicorn som ASGI-server. All logik täcks av >40 automatiska Pytest-tester.


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
* **Python** 3.11 slim-runtime
* **Node 16+** (vid front-end)
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
├── run.sh / run.bat          # Dev helpers
└── docs/                     # ← detta dokument
```

## 4 Configuration
Konfiguration läses av **pydantic-settings** från `.env`.

| Key                      | Default | Beskrivning                          |
|--------------------------|---------|--------------------------------------|
| `APP_NAME`               | AZOM AI Agent | Titel för core-API               |
| `PORT` / `PIPELINE_PORT` | 8008 / 8001 | Lyssningsportar                  |
| `DEBUG`                  | false   | Aktiverar debug-läge                |
| `OPENWEBUI_API_TOKEN`    | –       | Token till OpenWebUI                 |
| `TARGET_MODEL`           | azom-se-general | LLM-modell                      |
| `CACHE_TTL_SECONDS`      | 3600    | Generell cache-TTL                   |

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
* **Admin endpoints** `/admin/products`, `/admin/faq`, `/admin/troubleshooting` (CRUD).


## 7 Database
Default: SQLite-fil `azom_pipelines.db` skapas automatiskt.
Alembic migrering körs automatiskt av `run.sh` eller kan köras manuellt:
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
* Bandit, Flake8 och Black i dev-deps.
* CORS är globalt öppet – stäng till i prod.
* Tokens läses från miljö, aldrig hårdkodade.


## 10 Future work
* Postgres-service i Compose.
* Kubernetes Helm-chart.
* Full CI/CD-pipeline.
* E2E-tester mot admin-frontend.

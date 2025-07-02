# AZOM AI Agent – Coding Guidelines

These guidelines define architecture, code style, tooling, and QA requirements for the AZOM AI-agent code-base. Follow them strictly — PRs that violate these rules will be rejected.

## 1. Architecture & Code Style

* **Modular design** – Clean / Hexagonal separation between domain, infrastructure and presentation layers.
* **LLM Back-end** – Default to local OpenWebUI/Ollama; optional Groq fallback enabled via settings.
* **Python 3.12+** – Use `match`, PEP 695 typing, and Pydantic v2.
* **Async-first** – All IO logic (FastAPI endpoints, DB, HTTP) **must** be `async def`.
* **Formatting & linting** – `ruff format` replaces Black; `ruff` + `mypy --strict` run in pre-commit & CI.
* **Type coverage** – 100 % with generics when useful.
* **Security scans** – `bandit`, `safety`, Dependabot; block CVSS ≥ 7.

## 2. Project Structure
```
app/        → Backend (FastAPI)
frontend/   → React 18 + TypeScript 5 + Vite UI
data/       → Knowledge files (CSV/MD/JSON)
docker/     → Containerisation
scripts/    → Setup, deploy & maintenance
tests/      → Pytest & Vitest suites
logs/       → Rotating logs & audit trails
```
Structure changes require an architecture review PR.

## 3. Git Flow
* `main` is always deployable; development on `feature/<short-desc>`.
* Mandatory PR review + automated tests.
* Conventional commits (`feat:`, `fix:`, `docs:` …).
* Squash commits on merge; releases tagged `vX.Y.Z`.

## 4. Docs & API Spec
* Docstrings on all public symbols.
* Endpoints documented via FastAPI & Pydantic models (auto OpenAPI).
* Model changes logged in `CHANGELOG.md`.
* Each module has a README.

## 5. Testing
* **Coverage ≥ 80 %** via Pytest & Vitest.
* Test pyramid – unit → integration → E2E.
* Edge-case & perf tests (`locust`).
* Failing tests block CI.

## 6. Knowledge Base
* Auto-discover files in `data/knowledge_base/` at start-up.
* Watchdog reloads on change; files > 10 MB are rejected.
* CSV validated against schema; in-memory cache with TTL.

## 7. LLM Prompting
* Single source of truth: `prompts/azom_system_prompt.txt`.
* Prompt files version-controlled; A/B testing supported.

## 8. Security
* Secrets only in `.env` / secret manager.
* Rate-limit 100 req/h/IP.
* Never expose stack-traces.
* Audit logs for security events.

## 9. CI/CD
* Pipeline: build → test → security scan → deploy.
* Docker scan must be green.
* Blue/green deployment & automatic rollback.

## 10. Monitoring & Agile
* 1-week sprints; each PR ties to KPI.
* Structured logging & metrics with alerts.

## 11. Frontend (React 18 + TS 5 + Vite)
* Strict TS (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `strictNullChecks`).
* Hooks-only components; state via Context/Zustand.
* Tailwind CSS + CSS variables; shadcn/ui primitives in `src/components/ui/`.
* Vitest + React Testing Library; ≥ 80 % coverage.
* ESLint + Prettier + Tailwind plugin; ARIA compliance.
* Storybook docs built in CI.

---
**Mantra:** _“Secure code first, fast code second, clean code always.”_

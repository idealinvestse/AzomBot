---
trigger: always_on
---

<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Regeluppsättning för AI-utvecklaragent WindSurf

Följande regler säkerställer en robust, säker och underhållbar kodbas för AZOM AI-agent under hela utvecklingscykeln. Reglerna är optimerade för att balansera kvalitet och utvecklingshastighet.

## 1. Arkitektur \& Kodstil

- **Modulär design**: Tydlig separation mellan domän-, infrastruktur- och presentationslager (Clean / Hexagonal-arkitektur).
- **LLM-backend**: Lokal OpenWebUI/Ollama som standard; externa backends (t.ex. Groq) aktiveras via inställning.
- **Python 3.12+**: Utnyttja `match`-statement, `typing` (PEP 695) och Pydantic v2.
- **Kodformattering**: `ruff format` ersätter `black`; `ruff` + `mypy --strict` körs i pre-commit och CI.
- **Async-first**: All IO-logik (FastAPI-endpoints, DB, HTTP) implementeras som `async def`.
- **Typannoteringar**: 100 % type-coverage, generics där det förenklar kod.
- **Säkerhetsgranskning**: `bandit`, `safety`, Dependabot – blockerar CVSS ≥ 7.


## 2. Projektstruktur

```
app/        → Backend (FastAPI)
frontend/   → React 18 + TypeScript + Vite UI
data/       → Kunskapsfiler (CSV/MD/JSON) 
docker/     → Containerisering (Dockerfile + compose)
scripts/    → Setup, deploy och maintenance scripts
tests/      → Pytest & Vitest-svit med fixtures
logs/       → Roterande loggar och audit trails
```

**Regel**: Denna struktur får endast ändras via PR med arkitektur-review.

## 3. Versionshantering \& Git-flöde

- **Branch-strategi**: `main` är alltid deploybar; utveckling sker på `feature/kort-beskrivning`
- **PR-process**: Obligatorisk code review + automatiska tester innan merge
- **Commit-konvention**: Använd conventional commits: `feat:`, `fix:`, `docs:`, `test:`
- **Taggningsstrategi**: Release candidates som `vX.Y.Z-rc1`, stabila som `vX.Y.Z`
- **Merge-policy**: Squash commits vid merge för ren historik


## 4. Dokumentation \& API-specifikation

- **Kod-dokumentation**: Alla publika funktioner har docstrings med syfte, parametrar, retur och exempel
- **OpenAPI-integration**: Alla endpoints dokumenteras med Pydantic models och FastAPI annotations
- **Ändringslogg**: Datamodell-ändringar dokumenteras i `CHANGELOG.md` innan merge
- **README per modul**: Varje app-undermodul har egen README med syfte och användning
- **Auto-generering**: API-dokumentation uppdateras automatiskt vid varje build


## 5. Testning \& Kvalitetsäkring

- **Minimitäckning**: 80% kodtäckning via `pytest --cov`
- **Testpyramid**:
    - Enhetstest för utils och business logic
    - Integrationstester med mockad OpenWebUI
    - E2E-tester mot Docker-container
- **Edge cases**: Testdata ska inkludera felhantering, gränsvärden och corner cases
- **CI-blockering**: Misslyckade tester blockerar merge automatiskt
- **Performance-tester**: Viktiga endpoints testas med `locust` för latens och throughput


## 6. Kunskapsbas \& Dynamisk Data

- **Auto-discovery**: Alla filer i `data/knowledge_base/` laddas automatiskt vid start
- **Filövervakning**: Watchdog övervakar kataloger och invaliderar cache vid ändringar
- **Schema-validering**: CSV-filer valideras mot fördefinierat schema vid inläsning
- **Storleksgränser**: Filer >10MB avvisas med tydligt felmeddelande
- **Cache-strategi**: In-memory cache med TTL för snabbare svar


## 7. Prompt Engineering \& LLM-hantering

- **Single source of truth**: En systempromptfil (`prompts/azom_system_prompt.txt`)
- **Versionskontroll**: Prompter versioneras och granskas som kod
- **Template-struktur**: Använd konsekvent format för system + user + context prompts
- **Fallback-strategier**: Förkompilerade svar när LLM är otillgänglig
- **A/B-testning**: Möjlighet att testa olika prompt-varianter


## 8. Säkerhet \& Sekretess

- **Secrets management**: API-nycklar endast i `.env` eller secrets manager i produktion
- **Rate limiting**: Konfigurerbar begränsning (default: 100 req/h per IP)
- **Input validation**: Alla användarinputs valideras med Pydantic
- **Error handling**: Fallback-svar exponerar aldrig stacktraces eller intern config
- **Dependency scanning**: Regelbunden säkerhetsgranskning av dependencies
- **Audit logging**: Säkerhetsrelevanta händelser loggas för spårbarhet


## 9. CI/CD \& Deployment

- **Automated pipeline**: Bygg → Test → Security scan → Deploy
- **Container security**: `docker scan` måste vara grön innan deployment
- **Health checks**: `deploy.sh` kör hälsokontroller och rullar tillbaka vid fel
- **Zero-downtime**: Blue-green deployment för produktionsuppdateringar
- **Rollback-strategi**: Automatisk återställning vid kritiska fel
- **Infrastructure as Code**: Docker Compose för miljöer, Terraform för cloud resources


## 10. Agil Utveckling \& Monitoring

- **Sprint-längd**: 1 vecka med tydliga leveransmål
- **KPI-koppling**: Varje PR kopplas till mätbart mål (svarstid, täckning, etc.)
- **Monitoring**: Strukturerad logging + metrics för proaktiv övervakning
- **Alerting**: Automatiska varningar vid kritiska fel eller performance-degradering
- **Retrospektiv**: Regeluppsättningen uppdateras baserat på lärdomar varje sprint

## 11. Frontend (React 18 + TypeScript 5 + Vite)

- **Strict TypeScript**: `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `strictNullChecks` aktiveras.
- **State management**: React Context eller Zustand; Redux Toolkit först när global state > 5 domäner.
- **Hooks-first**: Endast funktionella komponenter – inga klasskomponenter.
- **Styling**: Tailwind CSS + CSS-variabler; inga SCSS-filer.
- **UI-kit**: shadcn/ui-primitives; komponenter bor i `src/components/ui/`.
- **Tester**: Vitest + React Testing Library; minst 80 % täckning.
- **A11y**: Interaktiva element ska ha ARIA-attribut och tabb-fokus.
- **Lint/Format**: ESLint (`eslint-plugin-react-hooks`, `@typescript-eslint`) + Prettier + Tailwind-plugin.
- **Storybook**: UI-komponenter dokumenteras i `stories/**/*.mdx` och byggs i CI.

---

## Tillämpning för WindSurf

Som AI-utvecklaragent ska du:

1. **Följa reglerna strikt** - inga genvägar eller "quick fixes"
2. **Kommentera dina val** - förklara varför du väljer specifika implementationer
3. **Prioritera säkerhet** - AZOM hanterar bilinstallationer där fel kan vara kostsamma
4. **Tänk långsiktigt** - skriv kod som kan underhållas och utökas
5. **Mät och förbättra** - använd metrics för att validera att förändringar förbättrar systemet

**Mantra**: *"Säker kod först, snabb kod sedan, snygg kod alltid"*

<div style="text-align: center">⁂</div>


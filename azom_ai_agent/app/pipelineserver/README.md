# DEPRECATED – Refer to root README

Pipeline-server dokumentationen har konsoliderats i `azom_ai_agent/README.md`.
Detta README är kvar endast för bakåtkompatibilitet och kommer att tas bort
helt i nästa release.

En avancerad pipelineserver för installations- och produktrekommendationer, optimerad för OpenWebUI-integration.

## Funktionalitet
- FastAPI-server med endpoints för hälsokontroll och pipeline-installation
- Orchestration, RAG, knowledge, memory och safety-tjänster
- Strukturerade Pydantic-modeller
- Utils för svensk NLP och cache

## Kom igång

### 1. Installera beroenden
Kör i projektroten:
```bash
pip install fastapi uvicorn pydantic
```

### 2. Starta servern
```bash
uvicorn app.pipelineserver.pipeline_app.main:app --reload --port 8001
```

### 3. Testa API:et
Hälsokontroll:
```bash
curl http://localhost:8001/health
```

Kör pipeline-installation:
```bash
curl -X POST http://localhost:8001/pipeline/install \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Jag vill installera AZOM i min Volvo", "car_model": "Volvo", "user_experience": "nybörjare"}'
```

Du får då ett JSON-svar med rekommenderad produkt, installationssteg och säkerhetsvarningar.

## Vidareutveckling
- Bygg ut orchestration/RAG/knowledge-tjänster med riktig logik
- Lägg till fler pipelines och endpoints
- Integrera med OpenWebUI eller andra klienter

---

**Lycka till med vidareutvecklingen!**

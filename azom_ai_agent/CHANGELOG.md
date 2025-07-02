# Ändringslogg

Alla viktiga ändringar i detta projekt dokumenteras i denna fil.

Formatet baseras på [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
och projektet följer [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Tillagt
- SafetyService med innehållsvalidering och sanering
- Readme-filer för varje app-undermodul
- Pre-commit hooks för kvalitetssäkring

### Ändrat
- Förbättrad felhantering i RAGService

### Åtgärdat
- Korrigerat typannoteringar för Python 3.12-kompabilitet
- Åtgärdat säkerhetsrisker i middleware

## [1.0.0] - 2025-07-01

### Tillagt
- Initialt API med FastAPI-backend
- Pipeline-server för installationsguider
- React frontend med TypeScript och Tailwind
- Retrieval-Augmented Generation (RAG) med FAISS och MiniLM
- OpenWebUI/Ollama-integration med Groq fallback
- Docker-containerisering
- Dokumentation för API och deployment

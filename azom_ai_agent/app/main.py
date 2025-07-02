from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings
from .logger import get_logger, init_logging
from .api.v1 import diagnose, health, knowledge_management
import uvicorn
from .middlewares import RequestLoggingMiddleware, RateLimitingMiddleware
from .exceptions import add_exception_handlers

# Skapa och ladda applikationsinställningar
settings = Settings()

# Initialisera loggning för hela applikationen
init_logging(level="DEBUG" if settings.DEBUG else str(settings.LOG_LEVEL.value))
logger = get_logger(__name__)

# Skapa FastAPI-applikation med metadata från settings
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    description="AZOM AI Agent API för integration med installationsguider och support."
)

# Registrera API-routes
app.include_router(diagnose.router)
app.include_router(health.router)
app.include_router(knowledge_management.router)

# Lägg till CORS-middleware om konfigurerad
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Lägg till custom middleware för loggning och rate-limiting
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitingMiddleware, settings=settings)

# Konfigurera globala exception handlers
add_exception_handlers(app)

# Logga uppstartsmeddelande
logger.info(
    f"Startar {settings.APP_NAME} v{settings.APP_VERSION}", 
    extra={"mode": "DEBUG" if settings.DEBUG else "PRODUCTION"}
)

@app.get("/ping")
def ping():
    return {"status": "ok", "version": settings.APP_VERSION}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)

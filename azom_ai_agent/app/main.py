from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings, FrontendSettings, update_runtime_settings, get_current_config
from .logger import get_logger, init_logging
from app.api.v1.health import router as health_router
from app.api.v1.diagnose import router as diagnose_router
from app.api.v1.knowledge_management import router as knowledge_router
from app.api.v1.chat import router as chat_router
from fastapi import Response, status, Depends
import uvicorn
from .middlewares import RequestLoggingMiddleware, RateLimitingMiddleware
from .exceptions import add_exception_handlers

# Skapa och ladda applikationsinställningar
settings = Settings()

# Initialisera loggning för hela applikationen
init_logging(level=settings.LOG_LEVEL.value)
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
app.include_router(health_router)
app.include_router(diagnose_router)
app.include_router(knowledge_router)
app.include_router(chat_router)

@app.post("/api/v1/settings", status_code=status.HTTP_204_NO_CONTENT)
def configure_runtime_settings(frontend_settings: FrontendSettings):
    """
    Endpoint to update runtime settings from the frontend.
    """
    update_runtime_settings(frontend_settings)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

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
app.add_middleware(RateLimitingMiddleware)

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

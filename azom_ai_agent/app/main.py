from fastapi import FastAPI
from .config import Settings
from .logger import get_logger, init_logging
from .api.v1 import diagnose, health, knowledge_management
import uvicorn
from .middleware import RequestLoggingMiddleware
from .exceptions import add_exception_handlers

settings = Settings()
# Initialise logging once for the whole application
init_logging(level="DEBUG" if settings.DEBUG else "INFO")
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.include_router(diagnose.router)
app.include_router(health.router)
app.include_router(knowledge_management.router)

# Attach middleware and global exception handlers
app.add_middleware(RequestLoggingMiddleware)
add_exception_handlers(app)

@app.get("/ping")
def ping():
    return {"status": "ok", "version": settings.APP_VERSION}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)

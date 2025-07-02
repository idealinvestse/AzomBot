from fastapi import FastAPI
from .endpoints import router

app = FastAPI(
    title="AZOM AI ToolServer",
    version="1.0.0",
    description="Toolserver för avancerade agentfunktioner med LLM och memory"
)
app.include_router(router, prefix="/tool")

@app.get("/ping")
async def ping():
    return {"status": "ok"}

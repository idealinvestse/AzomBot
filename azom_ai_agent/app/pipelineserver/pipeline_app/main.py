from app.logger import get_logger, init_logging
from fastapi import FastAPI, Request, HTTPException, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.middleware import RequestLoggingMiddleware
from app.exceptions import add_exception_handlers
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .pipelines.azom_installation_pipeline import AZOMInstallationPipeline
from .pipelines.support_pipeline import SupportPipeline
from .services.llm_client import get_llm_client, LLMServiceProtocol
from .services.rag_service import RAGService


init_logging()  # root logging
logger = get_logger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Add middleware & exception handlers
app.add_middleware(RequestLoggingMiddleware)
add_exception_handlers(app)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = AZOMInstallationPipeline()
support_pipeline = SupportPipeline()
rag_service = RAGService()


class PipelineInstallRequest(BaseModel):
    user_input: str
    car_model: str = None
    user_experience: str = None

class SupportRequest(BaseModel):
    question: str

class ChatRequest(BaseModel):
    message: str
    car_model: str | None = None

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/pipeline/install")
async def install_pipeline(request: PipelineInstallRequest):
    """ Kör installations-pipelinen och returnerar rekommendationer. """
    try:
        # Validera indata
        if not request.user_input or not request.user_input.strip():
            raise HTTPException(status_code=400, detail="Ange en beskrivning av ditt ärende")
            
        if not request.car_model or not request.car_model.strip():
            raise HTTPException(status_code=400, detail="Ange bilmodell")
            
        # Kör pipelinen
        result = await pipeline.run_installation(
            user_input=request.user_input,
            car_model=request.car_model,
            user_experience=request.user_experience or "nybörjare"
        )
        return {"result": result}
        
    except HTTPException:
        # Skicka vidare HTTP-undantag oförändrade
        raise
        
    except ValueError as e:
        # Hantera valideringsfel med 400 Bad Request
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Logga oväntade fel och returnera 500
        logger.exception("Oväntat fel i installationspipelinen")
        raise HTTPException(
            status_code=500, 
            detail="Ett internt fel inträffade. Vänligen försök igen senare."
        )

@app.post("/chat/azom")
async def chat_with_azom(request: ChatRequest, llm_client: LLMServiceProtocol = Depends(get_llm_client)):
    """Free-form chat endpoint that augments user query with RAG context and calls local OpenWebUI/Ollama via LLMClient."""
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=422, detail="Message is required")
    # 1. Fetch context via simple keyword search RAG
    context_items = await rag_service.search(f"{request.car_model or ''} {request.message}", top_k=3)
    context_snippets = "\n".join([f"- {c['content']}" for c in context_items])

    system_prompt = (
        "Du är AZOM Installations-Expert, en hjälpsam AI som svarar på svenska. "
        "Använd installations- och felsökningskontexten nedan om relevant."
    )
    if context_snippets:
        system_prompt += f"\n\nRelevant kontext:\n{context_snippets}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.message.strip()},
    ]
    try:
        assistant_reply = await llm_client.chat(messages)
        return {"assistant": assistant_reply, "context_used": context_items}
    except Exception as e:
        logger.exception("LLM chat failed")
        raise HTTPException(status_code=500, detail="LLM error: " + str(e))


@app.post("/api/v1/support")
async def get_support(request: SupportRequest):
    """Get support for a specific question."""
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=422, detail="Question is required")
            
        # Get support response
        result = await support_pipeline.run_support(request.question)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in support endpoint")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        )

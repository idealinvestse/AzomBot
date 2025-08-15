from fastapi import APIRouter, Depends, HTTPException
from app.services.ai_service import AIService
from app.models import GeneralQuery, TroubleshootRequest, ChatResponse
from app.pipelineserver.pipeline_app.services.llm_client import get_llm_client, LLMServiceProtocol

router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)

def get_ai_service(llm_client: LLMServiceProtocol = Depends(get_llm_client)) -> AIService:
    """Dependency to create and return an AIService instance."""
    return AIService(llm_client=llm_client)

@router.post("/support", response_model=ChatResponse)
async def troubleshoot_pipeline(request: TroubleshootRequest, ai_service: AIService = Depends(get_ai_service)):
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    response_text = await ai_service.query(request.prompt, context=request.model_dump())
    return ChatResponse(response=response_text)

@router.post("/chat/azom", response_model=ChatResponse)
async def general_query(request: GeneralQuery, ai_service: AIService = Depends(get_ai_service)):
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    response_text = await ai_service.query(request.prompt, context=request.model_dump())
    return ChatResponse(response=response_text)

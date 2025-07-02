import os
from app.services.llm_service import LLMService
from app.config import Settings

settings = Settings()
llm = LLMService({
    "backend": os.getenv("LLM_BACKEND", "openwebui")
})  # Dynamically selects backend


def llm_diagnose(user_prompt: str, context: dict) -> str:
    return llm.query(user_prompt, context)

def llm_lookup(user_prompt: str, context: dict) -> str:
    # T.ex. används för lookup mot kunskapsbasen enligt prompt (kan utvecklas/förtydligas)
    return llm.query(f"Sök i kunskapsbas: {user_prompt}", context)

def llm_update_knowledge(data: dict) -> str:
    # Skapa logik för att trigga reload/service etc
    # Kan extenda med dynamisk reload, filadd etc.
    return "Kunskapsbasen är planerad att uppdateras (dummy-funktion i demo)"

def llm_savememory(session_id: str, memory: str) -> str:
    # Här skulle man t.ex. kunna spara ner till lokal DB eller fil
    # För demo, dummy response
    return f"Session {session_id} har sparats"

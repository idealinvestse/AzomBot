from fastapi import APIRouter

router = APIRouter(prefix="/diagnose", tags=["diagnose"])

@router.get("")
def diagnose_info():
    return {"diagnose": "Tjänsten är igång. Beskriv felkod eller bilmodell för felsökning."}

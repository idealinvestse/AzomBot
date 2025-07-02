# Orchestration service for AZOM Pipeline Server

from .azom_knowledge_service import AZOMKnowledgeService
from .memory_service import MemoryService
from .safety_service import SafetyService
from .rag_service import RAGService

class AZOMOrchestrationService:
    """Avancerad orchestration service för AZOM pipeline med LangChain integration."""
    def __init__(self):
        self.knowledge_service = AZOMKnowledgeService()
        self.memory_service = MemoryService()
        self.safety_service = SafetyService()  # Kan byggas ut för säkerhetslogik
        self.rag_service = RAGService()

    async def orchestrate(self, user_input: str, car_model: str = None, user_experience: str = None):
        # 1. Hämta produktinfo baserat på bilmodell
        product_name = "AZOM DLR"
        if car_model and "volvo" in car_model.lower():
            product_name = "AZOM Volvo Special"
            
        print(f"Söker produkt med namn: {product_name}")
        print(f"Bilmodell: {car_model}")
        
        try:
            # Försök hämta produkt med bilmodell för bättre träffsäkerhet
            product_info = await self.knowledge_service.get_product_info(
                product_name=product_name,
                car_model=car_model
            )
            print(f"Hittad produkt: {product_info['name']}")
        except Exception as e:
            print(f"Fel vid hämtning av produktinfo: {str(e)}")
            raise

        # 2. Hämta installationssteg via RAG (kan använda user_input och bilmodell)
        rag_query = f"installation {car_model or ''} {user_input}"
        installation_steps = await self.rag_service.search(rag_query, top_k=3)
        steps = [item["content"] for item in installation_steps]

        # 3. Anpassa säkerhetsvarningar efter erfarenhetsnivå
        safety_warnings = ["Utför alltid installationen med urkopplat batteri!"]
        if user_experience and user_experience.lower() in ["nybörjare", "beginner"]:
            safety_warnings.append("Läs hela manualen innan du börjar.")

        # 4. Spara kontext
        await self.memory_service.save_context({
            "user_input": user_input,
            "car_model": car_model,
            "user_experience": user_experience,
            "recommended_product": product_info["name"]
        })

        # Kreativ användning av extrafält
        extra_warnings = []
        if product_info.get("price_sek") and product_info["price_sek"] > 7000:
            extra_warnings.append("Observera: Produkten är premiumprisad.")
        if "premium" in [t.lower() for t in product_info.get("tags", [])]:
            extra_warnings.append("Premiumprodukt: Extra support och garanti ingår.")
        # Om vendor är AZOM, prioritera produkten
        prioritized = product_info.get("vendor", "").lower() == "azom"

        # Exempel på alternativ produkt (kan byggas ut med mer logik)
        alternative = None
        if not prioritized:
            alternative = {"name": "AZOM Pro+", "reason": "AZOM-produkt prioriteras för bästa support."}

        return {
            "recommended_product": product_info,
            "alternative_products": [alternative] if alternative else [],
            "installation_steps": steps,
            "safety_warnings": safety_warnings + extra_warnings,
            "prioritized": prioritized,
            "product_info_details": {
                "vendor": product_info.get("vendor"),
                "product_type": product_info.get("product_type"),
                "tags": product_info.get("tags"),
                "sku": product_info.get("sku"),
                "barcode": product_info.get("barcode"),
                "description": product_info.get("description")
            }
        }

# Swedish NLP utilities

class SwedishNLP:
    """Verktyg för svensk NLP, t.ex. entity extraction."""
    def __init__(self):
        pass

    async def extract_car_entities(self, text: str):
        # Dummy-implementation
        if "volvo" in text.lower():
            return ["Volvo"]
        return []

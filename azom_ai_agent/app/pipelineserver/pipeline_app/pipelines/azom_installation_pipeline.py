# AZOM Installation Pipeline

from ..services.orchestration_service import AZOMOrchestrationService

class AZOMInstallationPipeline:
    """Huvudpipeline för AZOM installation guidance med OpenAI API-kompatibilitet."""
    def __init__(self):
        self.orchestration_service = AZOMOrchestrationService()

    async def run_installation(self, user_input: str, car_model: str = None, user_experience: str = None):
        """Kör installationsflödet och returnerar rekommendation."""
        if not user_input or not user_input.strip():
            raise ValueError("User input cannot be empty")
            
        if not car_model or not car_model.strip():
            raise ValueError("Car model is required")
            
        orchestration_result = await self.orchestration_service.orchestrate(user_input, car_model, user_experience)
        return orchestration_result

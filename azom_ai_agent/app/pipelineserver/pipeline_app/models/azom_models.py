from pydantic import BaseModel
from typing import List, Optional

class AZOMProduct(BaseModel):
    name: str
    price_sek: int
    success_rate: int
    installation_time: str
    canbus_required: bool

class InstallationRecommendation(BaseModel):
    recommended_product: AZOMProduct
    alternative_products: List[AZOMProduct] = []
    installation_steps: List[str] = []
    safety_warnings: List[str] = []

class PipelineInstallRequest(BaseModel):
    user_input: str
    car_model: Optional[str] = None
    user_experience: Optional[str] = None

class PipelineInstallResponse(BaseModel):
    result: InstallationRecommendation

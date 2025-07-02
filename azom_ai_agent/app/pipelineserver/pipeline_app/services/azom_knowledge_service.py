# AZOM Knowledge Service

import json
import os

class AZOMKnowledgeService:
    """Service för hantering av AZOM:s kunskapsbas."""
    def __init__(self):
        self.products_path = os.path.join(os.path.dirname(__file__), '../../data/products.json')

    async def get_product_info(self, product_name: str = None, car_model: str = None):
        print(f"AZOMKnowledgeService.get_product_info anropad med: product_name='{product_name}', car_model='{car_model}'")
        try:
            with open(self.products_path, encoding='utf-8') as f:
                products = json.load(f)
            print(f"Laddade {len(products)} produkter från {self.products_path}")
            
            # Sök på namn först
            if product_name:
                print(f"Söker produkt med namn: {product_name}")
                for p in products:
                    if p.get('name') and p['name'].lower() == product_name.lower():
                        print(f"Hittad produkt på namn: {p['name']}")
                        return self._format_product(p)
            
            # Annars sök på kompatibel bilmodell
            if car_model:
                print(f"Söker produkt för bilmodell: {car_model}")
                car_model_lower = car_model.strip().lower()
                for p in products:
                    if p.get('compatible_models'):
                        # Convert all compatible models to lowercase for case-insensitive comparison
                        compatible_models_lower = [m.strip().lower() for m in p['compatible_models']]
                        if car_model_lower in compatible_models_lower:
                            print(f"Hittad produkt för bilmodell {car_model}: {p.get('name')}")
                            return self._format_product(p)
            
            error_msg = f"Ingen produkt hittades för namn '{product_name}' eller bilmodell '{car_model}'"
            print(error_msg)
            raise ValueError(error_msg)
            
        except Exception as e:
            print(f"Fel i get_product_info: {str(e)}")
            raise

    def _format_product(self, p):
        # Returnera alla fält, hantera None snyggt
        return {
            "name": p.get("name"),
            "description": p.get("description", ""),
            "price_sek": p.get("price_sek"),
            "vendor": p.get("vendor", ""),
            "product_type": p.get("product_type", ""),
            "tags": p.get("tags", []),
            "sku": p.get("sku", ""),
            "barcode": p.get("barcode", ""),
            "compatible_models": p.get("compatible_models", []),
            # Fält för framtida användning:
            "success_rate": p.get("success_rate"),
            "installation_time": p.get("installation_time"),
            "canbus_required": p.get("canbus_required")
        }

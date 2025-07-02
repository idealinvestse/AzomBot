import os
import json
from pipeline_app.services.orchestration_service import AZOMOrchestrationService

class TroubleshootingPipeline:
    """Pipeline för felsökning av installationer och produkter."""
    def __init__(self):
        self.orchestration_service = AZOMOrchestrationService()
        # Ladda all felsökningsdata från troubleshooting.json och alla relevanta other_*.json
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
        self.troubleshooting_data = []
        # Standarddata
        try:
            with open(os.path.join(data_dir, 'troubleshooting.json'), encoding='utf-8') as f:
                self.troubleshooting_data += json.load(f)
        except Exception:
            pass
        # Andra guider
        for fname in os.listdir(data_dir):
            if fname.startswith('other_') and ('troubleshooting' in fname or 'errors' in fname):
                try:
                    with open(os.path.join(data_dir, fname), encoding='utf-8') as f:
                        self.troubleshooting_data += json.load(f)
                except Exception:
                    pass

    async def run_troubleshooting(self, user_input: str, car_model: str = None):
        # Sök i all felsökningsdata
        matches = []
        query = (car_model or '') + ' ' + (user_input or '')
        query = query.lower()
        for item in self.troubleshooting_data:
            model = (item.get('model') or '').lower()
            keywords = [k.lower() for k in item.get('issue_keywords', [])]
            if (car_model and car_model.lower() in model) or any(k in query for k in keywords):
                matches.append(item)
        if not matches:
            return {"steps": ["Ingen felsökningsguide hittades för din fråga. Kontrollera stavning eller kontakta support."]}
        # Slå ihop och prioritera steg
        all_steps = []
        for m in matches:
            all_steps += m.get('steps', [])
        # Ta bort dubbletter och sortera
        all_steps = list(dict.fromkeys(all_steps))
        return {"steps": all_steps}

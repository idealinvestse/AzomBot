# Memory service for pipeline server

import json
import os
from datetime import datetime

class MemoryService:
    """Service för hantering av minne och kontext."""
    def __init__(self):
        self.history_path = os.path.join(os.path.dirname(__file__), '../../data/user_history.json')

    async def save_context(self, context: dict, user_id: str = "default"):
        # Spara historik per användare
        try:
            if os.path.exists(self.history_path):
                with open(self.history_path, encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = {}
            if user_id not in history:
                history[user_id] = []
            context["timestamp"] = datetime.now().isoformat()
            history[user_id].append(context)
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            return {"status": "context saved"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_history(self, user_id: str = "default"):
        if not os.path.exists(self.history_path):
            return []
        with open(self.history_path, encoding='utf-8') as f:
            history = json.load(f)
        return history.get(user_id, [])

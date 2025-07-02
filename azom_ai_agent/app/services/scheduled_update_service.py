import threading
import time
from app.services.knowledge_service import KnowledgeService

class ScheduledUpdateService:
    def __init__(self, knowledge_service: KnowledgeService, interval: int = 3600):
        self.interval = interval
        self.knowledge_service = knowledge_service
        self._stop_event = threading.Event()

    def start(self):
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def _run(self):
        while not self._stop_event.is_set():
            print("Schemalagd cache-reload av kunskap...")
            self.knowledge_service.load_knowledge()
            time.sleep(self.interval)

    def stop(self):
        self._stop_event.set()

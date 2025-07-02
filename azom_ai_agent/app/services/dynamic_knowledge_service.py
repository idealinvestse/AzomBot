from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from pathlib import Path
import threading
from app.services.knowledge_service import KnowledgeService

class DynamicKnowledgeService(FileSystemEventHandler):
    def __init__(self, data_dir: Path, knowledge_service: KnowledgeService, valid_exts=None):
        self.data_dir = data_dir
        self.knowledge_service = knowledge_service
        self.valid_exts = valid_exts if valid_exts else ['.md', '.csv', '.json']
        self.observer = Observer()

    def start(self):
        self.observer.schedule(self, path=str(self.data_dir), recursive=True)
        t = threading.Thread(target=self.observer.start)
        t.daemon = True
        t.start()

    def on_modified(self, event):
        # Endast ladda om om man faktiskt ändrat en datafil
        if (
            isinstance(event, FileModifiedEvent) and
            event.src_path.endswith(tuple(self.valid_exts)) and
            Path(event.src_path).is_file()
        ):
            print(f"Knowledge file updated: {event.src_path}. In-memory cache reloadas.")
            self.knowledge_service.load_knowledge()

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()

from pathlib import Path
import time
from threading import Lock
import json
import csv
from typing import Dict, Any, Optional
from app.logger import get_logger

logger = get_logger(__name__)

class KnowledgeService:
    def __init__(self, data_path: Path, ttl: int = 3600):
        self.data_path = data_path / "knowledge_base"
        self.ttl = ttl
        self.cache = {}
        self.category_meta = {}
        self.cache_timestamp = 0.0
        self.lock = Lock()

    def load_knowledge(self):
        if self.lock.locked():
            # Undvik parallella reloads
            return
        with self.lock:
            cache = {}
            for cat_dir in self.data_path.glob('*'):
                if not cat_dir.is_dir():
                    continue
                cache[cat_dir.name] = {}
                for f in cat_dir.glob('*'):
                    try:
                        if f.suffix.lower() == '.md':
                            with open(f, encoding='utf-8') as fin:
                                cache[cat_dir.name][f.name] = {"type": "md", "content": fin.read()}
                        elif f.suffix.lower() == '.csv':
                            with open(f, encoding='utf-8') as fin:
                                reader = csv.reader(fin)
                                cache[cat_dir.name][f.name] = {"type": "csv", "content": list(reader)}
                        elif f.suffix.lower() == '.json':
                            with open(f, encoding='utf-8') as fin:
                                cache[cat_dir.name][f.name] = {"type": "json", "content": json.load(fin)}
                    except Exception as e:
                        logger.warning(f"Misslyckades läsa {f.name} i {cat_dir.name}: {e}")
                        continue
            self.cache = cache
            self.cache_timestamp = time.time()

    def get_knowledge(self, category: Optional[str] = None):
        if time.time() - self.cache_timestamp > self.ttl or not self.cache:
            self.load_knowledge()
        if category:
            return self.cache.get(category, {})
        return self.cache

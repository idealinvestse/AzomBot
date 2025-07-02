from app.services.knowledge_service import KnowledgeService
from app.services.scheduled_update_service import ScheduledUpdateService
from app.services.dynamic_knowledge_service import DynamicKnowledgeService
from pathlib import Path
import os
import time

def test_knowledge_reload_and_race(tmp_path):
    # Skapa dummydata för knowledge_base
    kb_dir = tmp_path / 'knowledge_base' / 'testcat'
    kb_dir.mkdir(parents=True)
    with open(kb_dir / 'test.md', 'w', encoding='utf-8') as f:
        f.write('En instruktion')
    ks = KnowledgeService(tmp_path, ttl=1)
    ks.load_knowledge()
    # Tryck på reload två gånger (race)
    ks.load_knowledge()
    out = ks.get_knowledge('testcat')
    assert 'test.md' in out

def test_scheduled_update_stop(tmp_path):
    ks = KnowledgeService(tmp_path)
    su = ScheduledUpdateService(ks, interval=1)
    su.start()
    time.sleep(1)
    su.stop()
    assert su._stop_event.is_set()

def test_dynamic_service_stop(tmp_path):
    ks = KnowledgeService(tmp_path)
    ds = DynamicKnowledgeService(tmp_path, ks)
    ds.start()
    ds.stop()
    assert hasattr(ds, 'observer')

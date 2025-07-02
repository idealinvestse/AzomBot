# Cache manager utilities

class CacheManager:
    """Hantering av cache för pipelineservern."""
    def __init__(self):
        self._cache = {}

    def get_cache(self, key):
        return self._cache.get(key)

    def set_cache(self, key, value):
        self._cache[key] = value

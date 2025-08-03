import pytest
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.pipelineserver.pipeline_app.utils.cache_manager import CacheManager


@pytest.mark.asyncio
async def test_cache_manager_initialization():
    """Test CacheManager initialization."""
    cache = CacheManager()
    assert cache is not None


@pytest.mark.asyncio
async def test_cache_set_and_get():
    """Test setting and getting a value from the cache."""
    cache = CacheManager()
    await cache.set_cache('key', 'value')
    assert await cache.get_cache('key') == 'value'


@pytest.mark.asyncio
async def test_cache_get_nonexistent_key():
    """Test getting a value from the cache with a nonexistent key."""
    cache = CacheManager()
    assert await cache.get_cache('nonexistent') is None


@pytest.mark.asyncio
async def test_cache_clear_all():
    """Test clearing all values from the cache."""
    cache = CacheManager()
    await cache.set_cache('key1', 'value1')
    await cache.set_cache('key2', 'value2')
    await cache.clear_all()
    assert await cache.get_cache('key1') is None
    assert await cache.get_cache('key2') is None


@pytest.mark.asyncio
async def test_cache_set_none_value():
    """Test setting a None value in the cache."""
    cache = CacheManager()
    await cache.set_cache('key', None)
    assert await cache.get_cache('key') is None


@pytest.mark.asyncio
async def test_cache_set_overwrite():
    """Test overwriting an existing value in the cache."""
    cache = CacheManager()
    await cache.set_cache('key', 'value1')
    await cache.set_cache('key', 'value2')
    assert await cache.get_cache('key') == 'value2'

@pytest.mark.asyncio
async def test_cache_item_expires(monkeypatch):
    """Test that a cached item expires after its TTL."""
    cache = CacheManager(default_ttl=10)
    await cache.set_cache('key', 'value')

    # Simulate time passing
    current_time = time.time()
    monkeypatch.setattr(time, 'time', lambda: current_time + 11)

    assert await cache.get_cache('key') is None

@pytest.mark.asyncio
async def test_delete_cache_item():
    """Test deleting an item from the cache."""
    cache = CacheManager()
    await cache.set_cache('key', 'value')
    assert await cache.delete_cache('key') is True
    assert await cache.get_cache('key') is None
    assert await cache.delete_cache('nonexistent') is False

@pytest.mark.asyncio
async def test_cleanup_expired_items(monkeypatch):
    """Test the cleanup of expired items."""
    cache = CacheManager(default_ttl=10)
    await cache.set_cache('expired_key', 'value1', ttl=5)
    await cache.set_cache('valid_key', 'value2', ttl=20)

    # Simulate time passing so one key expires
    current_time = time.time()
    monkeypatch.setattr(time, 'time', lambda: current_time + 6)

    cleaned_count = await cache.cleanup_expired()
    assert cleaned_count == 1
    assert await cache.get_cache('expired_key') is None
    assert await cache.get_cache('valid_key') == 'value2'

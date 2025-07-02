import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.pipelineserver.pipeline_app.utils.cache_manager import CacheManager


def test_cache_manager_initialization():
    """Test CacheManager initialization."""
    cache = CacheManager()
    assert cache is not None


def test_cache_set_and_get():
    """Test setting and getting a value from the cache."""
    cache = CacheManager()
    cache.set_cache('key', 'value')
    assert cache.get_cache('key') == 'value'


def test_cache_get_nonexistent_key():
    """Test getting a value from the cache with a nonexistent key."""
    cache = CacheManager()
    assert cache.get_cache('nonexistent') is None


def test_cache_clear_all():
    """Test clearing all values from the cache."""
    cache = CacheManager()
    cache.set_cache('key1', 'value1')
    cache.set_cache('key2', 'value2')
    cache.clear_all()
    assert cache.get_cache('key1') is None
    assert cache.get_cache('key2') is None


def test_cache_set_none_value():
    """Test setting a None value in the cache."""
    cache = CacheManager()
    cache.set_cache('key', None)
    assert cache.get_cache('key') is None


def test_cache_set_overwrite():
    """Test overwriting an existing value in the cache."""
    cache = CacheManager()
    cache.set_cache('key', 'value1')
    cache.set_cache('key', 'value2')
    assert cache.get_cache('key') == 'value2'

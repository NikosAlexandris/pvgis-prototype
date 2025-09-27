"""
Redis caching module for PVGIS Web API.
Provides thread-safe, multi-worker compatible caching using Redis as backend,
with fallback to local LRU cache when Redis is disabled.
"""

import functools
import asyncio
from typing import Any, Callable, TypeVar

from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer

from pvgisprototype.log import logger
from pvgisprototype.web_api.cache.hashing import generate_compact_cache_key
from pvgisprototype.web_api.cache.redis import (
    USE_REDIS_CACHE,
    REDIS_CONFIG,
)


F = TypeVar('F', bound=Callable[..., Any])

# Global cache registry
PVGIS_INTERNAL_CACHE_REGISTRY = []


def register_cache(cache, registry=PVGIS_INTERNAL_CACHE_REGISTRY):
    """Register a cache memory in the global cache registry."""
    if cache not in registry:
        registry.append(cache)
        logger.debug(f"Cache {cache} registered.")
    else:
        logger.debug(f"Cache {cache} already registered.")


def inspect_cache_registry(registry=PVGIS_INTERNAL_CACHE_REGISTRY):
    """
    Inspect the content of all cache memories in a cache registry.
    Returns a dictionary representation of the cache states.
    """
    cache_states = {}
    for index, cache in enumerate(registry):
        if hasattr(cache, '__len__') and len(cache):
            cache_states[f"cache_{index}"] = list(cache.items()) if hasattr(cache, 'items') else str(cache)
        else:
            cache_states[f"cache_{index}"] = "Cache is empty"
    return cache_states


async def clear_cache_registry(registry=PVGIS_INTERNAL_CACHE_REGISTRY):
    """Clear all registered caches."""
    for cache in registry:
        if hasattr(cache, 'clear'):
            if asyncio.iscoroutinefunction(cache.clear):
                await cache.clear()
            else:
                cache.clear()
    logger.debug(
        "Cache registry cleared.",
        alt="[bold yellow]Cache registry cleared.[/bold yellow]",
    )


def custom_cached(func):
    """
    Redis-only cache decorator - no LRU fallback.
    """
    @functools.wraps(func)
    async def redis_only_wrapper(*args, **kwargs):
        if not USE_REDIS_CACHE:
            logger.warning(f"⚠️ Redis not enabled, running {func.__name__} without caching")
            return await func(*args, **kwargs)
        
        logger.debug(f"🔍 Using Redis cache for {func.__name__}")
        
        # Generate cache key
        # custom_hashkey = generate_custom_hashkey(*args, **kwargs)
        custom_hashkey = generate_compact_cache_key(*args, **kwargs)
        cache_key = f"pvgis:{func.__name__}:{custom_hashkey}"
        
        @cached(
            ttl=REDIS_CONFIG.get('ttl', 3600),
            cache=Cache.REDIS,
            key=cache_key,
            serializer=PickleSerializer(),
            endpoint=REDIS_CONFIG.get('endpoint', '127.0.0.1'),
            port=REDIS_CONFIG.get('port', 6379),
            db=REDIS_CONFIG.get('db', 0)
        )
        async def redis_cached_func():
            return await func(*args, **kwargs)
        
        return await redis_cached_func()
    
    return redis_only_wrapper


def set_cache_backend(use_redis: bool = False, redis_config: dict = None):
    """
    Configure the cache backend to use Redis or LRU cache.
    
    Args:
        use_redis: Whether to use Redis caching
        redis_config: Optional Redis configuration overrides
    """
    global USE_REDIS_CACHE, REDIS_CONFIG
    
    USE_REDIS_CACHE = use_redis
    
    if redis_config:
        REDIS_CONFIG.update(redis_config)
    
    cache_type = "Redis" if use_redis else "LRU"
    logger.info(f"Cache backend set to: {cache_type}")

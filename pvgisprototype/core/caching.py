#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import threading
import os
from functools import wraps
from cachetools import LRUCache
from cachetools.keys import hashkey
from pandas import Timestamp, DatetimeIndex, Index
from numpy import ndarray
from xarray import DataArray
from pvgisprototype.log import logger
from math import floor
import time


CACHE_MAXSIZE = 24

# TTL in seconds : configurable via environment or default to 30s
DEFAULT_TTL_SECONDS = int(os.getenv("PVGIS_CACHE_TTL_SECONDS", "30"))


def _ttl_hash_gen(seconds: int):
    """Generate TTL hash that changes every 'seconds' interval"""
    start_time = time.time()
    while True:
        yield floor((time.time() - start_time) / seconds)


# Thread-local storage for per-request cache registries
_thread_local_storage = threading.local()


def generate_request_id():
    return str(os.getpid()) + "-" + str(threading.get_ident())


def get_request_id(request_id: str = 'request_id'):
    return getattr(_thread_local_storage, request_id, 'unknown')


def get_request_cache_registry():
    """Get or create the current request's cache registry"""
    if not hasattr(_thread_local_storage, 'cache_registry'):
        _thread_local_storage.cache_registry = []
        _thread_local_storage.request_id = generate_request_id()
        logger.debug(f"Created new request cache registry for {_thread_local_storage.request_id}")
    return _thread_local_storage.cache_registry


def register_cache(cache, registry=None):
    """Register a cache memory in the thread-local cache registry"""
    if registry is None:
        registry = get_request_cache_registry()

    if cache not in registry:
        registry.append(cache)
        request_id = get_request_id()
        logger.debug(f"Cache registered for request {request_id} (registry size: {len(registry)})")
    return cache


def inspect_cache_registry(registry=None):
    """Inspect the content of all cache memories in a cache registry"""
    if registry is None:
        registry = get_request_cache_registry()
    
    cache_states = {}
    for index, cache_func in enumerate(registry):
        try:
            if hasattr(cache_func, 'cache_info'):
                info = cache_func.cache_info()
                cache_states[f"cache_{index}"] = {
                    "function": info.get('function', 'unknown'),
                    "hits": info['lru_info'].hits,
                    "misses": info['lru_info'].misses,
                    "currsize": info['lru_info'].currsize,
                    "maxsize": info.get('maxsize', 'unknown'),
                    "ttl_seconds": info.get('ttl_seconds', 'unknown')
                }
            else:
                cache_states[f"cache_{index}"] = "Cache info not available"
        except Exception as e:
            cache_states[f"cache_{index}"] = f"Error getting cache info: {e}"
    
    return cache_states


def clear_request_caches():
    """Clear all caches for the current request"""
    if hasattr(_thread_local_storage, 'cache_registry'):
        registry = _thread_local_storage.cache_registry
        request_id = get_request_id()
        # if len(registry) != 0:
        #     request_id = get_request_id()  #getattr(_thread_local_storage, 'request_id', 'unknown')
            
        #     total_cached_items = sum(len(cache) for cache in registry)
            
        #     for cache in registry:
        #         cache.clear()
            
        #     logger.debug(
        #         f"Cleared {len(registry)} caches with {total_cached_items} total items "
        #         f"for request {request_id}"
        #     )
        # else:
        #     logger.debug(f"Nothing to clear !")
        # Get stats before clearing
        total_hits = 0
        total_misses = 0
        total_caches = len(registry)
        
        for cache in registry:
            try:
                if hasattr(cache, 'cache_info'):
                    info = cache.cache_info()
                    total_hits += info['lru_info'].hits
                    total_misses += info['lru_info'].misses
                
                if hasattr(cache, 'cache_clear'):
                    cache.cache_clear()
            except Exception as e:
                logger.warning(f"Error clearing cache: {e}")
        
        # Log performance summary
        total_requests = total_hits + total_misses
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        logger.info(
            f"Request {request_id} cache summary: "
            f"{total_caches} caches, {total_hits} hits, {total_misses} misses, "
            f"{hit_rate:.1f}% hit rate"
        )
            
        # Clear the registry
        _thread_local_storage.cache_registry = []
        _thread_local_storage.request_id = 'unknown'


def generate_custom_hashkey(*args, **kwargs):
    """Your working hash key generator - keeping it exactly as is"""
    kwargs = {
        k: (
            str(v)
            if isinstance(
                v,
                (
                    list,
                    Timestamp,
                    DatetimeIndex,
                    Index,
                    ndarray,
                    DataArray,
                ),
            )
            else v
        )
        for k, v in kwargs.items()
    }
    return hashkey(*args, **kwargs)


def custom_cached(func):
    """
    Backwards compatible per-request thread-safe LRU cache with TTL expiration.
    Usage is exactly the same as your existing decorator.
    TTL is internally configurable via 'PVGIS_CACHE_TTL_SECONDS' env variable (default 300s).
    """
    ttl = DEFAULT_TTL_SECONDS
    ttl_hash_gen = _ttl_hash_gen(ttl)
    
    def get_or_create_cache():
        cache_attr = f"_cache_{func.__name__}_{id(func)}"
        
        if not hasattr(_thread_local_storage, cache_attr):
            # LRUCache as backing cache store
            cache_memory = LRUCache(maxsize=CACHE_MAXSIZE)
            setattr(_thread_local_storage, cache_attr, cache_memory)
            # Register cache for per-request cleanup
            registry = getattr(_thread_local_storage, 'cache_registry', None)
            if registry is None:
                registry = []
                setattr(_thread_local_storage, 'cache_registry', registry)
            if cache_memory not in registry:
                registry.append(cache_memory)
            
            request_id = getattr(_thread_local_storage, 'request_id', 'unknown')
            logger.debug(f"Created cache for {func.__name__} in request {request_id}, TTL={ttl}s, maxsize={CACHE_MAXSIZE}")
        
        return getattr(_thread_local_storage, cache_attr)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_memory = get_or_create_cache()
        
        # Compute TTL hash to invalidate cache every ttl seconds
        ttl_hash = next(ttl_hash_gen)
        
        # Generate composite key: (ttl_hash, your original key)
        # Use your existing generate_custom_hashkey to maintain compatible key hashing
        from pvgisprototype.core.caching import generate_custom_hashkey  # adjust import as needed
        key_inner = generate_custom_hashkey(*args, **kwargs)
        key = (ttl_hash, key_inner)
        
        if key in cache_memory:
            request_id = getattr(_thread_local_storage, 'request_id', 'unknown')
            logger.debug(f"Cache HIT for {func.__name__} in request {request_id} (ttl_hash={ttl_hash})")
            return cache_memory[key]
        
        # Cache miss: call function and store result
        result = func(*args, **kwargs)
        cache_memory[key] = result
        
        request_id = getattr(_thread_local_storage, 'request_id', 'unknown')
        logger.debug(f"Cache MISS for {func.__name__} in request {request_id} (ttl_hash={ttl_hash})")
        
        return result
    
    return wrapper

from functools import wraps

from cachetools import cached, LRUCache
from cachetools.keys import hashkey

from pvgisprototype.log import logger
from pvgisprototype.constants import CACHE_MAXSIZE
from pvgisprototype.core.hashing import generate_hash

PVGIS_INTERNAL_CACHE_REGISTRY = []  # a global cache memory registry !


def register_cache(cache, registry=PVGIS_INTERNAL_CACHE_REGISTRY):
    """
    Register a cache memory in the global cache registry.
    """
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
        if len(cache):
            cache_states[f"cache_{index}"] = list(cache.items())
        else:
            cache_states[f"cache_{index}"] = "Cache is empty"

    return cache_states


def clear_cache_registry(registry=PVGIS_INTERNAL_CACHE_REGISTRY):
    """
    Clear all registered caches.
    """
    for cache in registry:
        cache.clear()
        logger.debug(
            "Cache registry cleared.",
            alt="[bold yellow]Cache registry cleared.[/bold yellow]",
        )


def make_object_hashable(object):
    """
    Convert unhashable objects to hashable representations.
    Uses generate_hash() for complex objects that can't be hashed directly.
    """
    try:
        # Try to hash the object directly first
        hash(object)
        logger.debug(f"Object {object} is hashable.")
        return object
    except TypeError:
        # If it's unhashable, use our custom generate_hash function
        logger.debug(f"Object {object} is unhashable.")
        return generate_hash(object)


def generate_custom_hashkey(*args, **kwargs):
    """
    Generate a custom hash key for the given arguments and keyword arguments.

    Returns
    -------
    hashkey: The hash key for the given arguments and keyword arguments.
    """
    args_hashed = tuple(make_object_hashable(argument) for argument in args)

    kwargs_hashed = {key: make_object_hashable(value) for key, value in kwargs.items()}

    return hashkey(*args_hashed, **kwargs_hashed)


def custom_cached(func):
    """
    Cache the results of the decorated function using a Least Frequently Used
    (LFU) cache and a custom hash key generator.

    This decorator applies LFU caching with a maximum size of 100 items, where
    the least frequently accessed items are evicted first once the cache
    reaches its maximum capacity. It also uses a custom key generation
    function, `generate_custom_hashkey`, to ensure consistent caching for calls
    with similar arguments.

    Parameters
    ----------
    func : callable
        The function whose results should be cached.

    Returns
    -------
    callable: A wrapper function that caches the results of `func` based on
    usage frequency and custom hash keys.

    Usage
    -----
    ```
    @custom_cached
    def expensive_computation(x, y):
        # Long-running computation here
        return x * y
    ```

    Notes
    -----
    - This decorator is useful for functions where some results are used more
      frequently than others, benefiting from the LFU eviction policy.
    - The custom key generator `generate_custom_hashkey` helps ensure that
      cache keys are generated consistently, which can be useful for handling
      complex or mutable arguments.

    """
    cache_memory = LRUCache(maxsize=CACHE_MAXSIZE)

    # Register cache immediately
    if cache_memory not in PVGIS_INTERNAL_CACHE_REGISTRY:
        register_cache(cache_memory)

    @wraps(func)
    @cached(cache=cache_memory, key=generate_custom_hashkey)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper

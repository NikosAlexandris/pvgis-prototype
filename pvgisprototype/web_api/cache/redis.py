from typing import Callable, Any, TypeVar


F = TypeVar('F', bound=Callable[..., Any])

# Configuration flag - can be set via environment variable or settings
USE_REDIS_CACHE = False  # Default to LRU cache

# Redis connection configuration
REDIS_CONFIG = {
    "endpoint": "127.0.0.1",
    "port": 6379,
    "db": 0,
    "ttl": 3600,  # 1 hour default
}


def redis_cached(namespace: str = "pvgis") -> Callable[[F], F]:
    """
    Redis cache decorator for synchronous functions in Web API context.
    
    This decorator caches synchronous function results in Redis, making them
    accessible across multiple workers and threads.
    
    Args:
        ttl: Time to live in seconds (default: 1 hour)
        namespace: Cache key namespace (default: "pvgis")
    
    Returns:
        Decorated async function that caches results in Redis
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key using your existing hash generator
            # custom_hash = generate_custom_hashkey(args, kwargs)
            custom_hash = generate_custom_hashkey(*args, **kwargs)
            cache_key = f"{namespace}:{func.__name__}:{custom_hash}"
            
            # Use aiocache.cached decorator with Redis backend
            @cached(
                cache=Cache.REDIS,
                key=cache_key,
                serializer=PickleSerializer(),
                **REDIS_CONFIG
            )
            async def cached_execution():
                # Execute synchronous function in thread pool to avoid blocking
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(
                    None, 
                    functools.partial(func, *args, **kwargs)
                )
            
            return await cached_execution()
        
        return async_wrapper
    return decorator

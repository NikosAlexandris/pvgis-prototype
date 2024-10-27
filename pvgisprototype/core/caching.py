from functools import wraps

from cachetools import cached, LFUCache
from cachetools.keys import hashkey
from pandas import Timestamp, DatetimeIndex, Index
from numpy import ndarray
from xarray import DataArray


def generate_custom_hashkey(*args, **kwargs):
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
    @wraps(func)
    @cached(cache=LFUCache(maxsize=100), key=generate_custom_hashkey)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper

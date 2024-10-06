from functools import wraps

from cachetools import cached, LFUCache
from cachetools.keys import hashkey
from pandas import Timestamp, DatetimeIndex, Index
from numpy import ndarray

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
                ),
            )
            else v
        )
        for k, v in kwargs.items()
    }
    return hashkey(*args, **kwargs)


def custom_cached(func):
    @wraps(func)
    @cached(cache=LFUCache(maxsize=100), key=generate_custom_hashkey) # NOTE Least Frequently Used eviction policy, useful when some results are used repeatedly
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper

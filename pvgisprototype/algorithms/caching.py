from pandas import DatetimeIndex
from cachetools.keys import hashkey


def custom_hashkey(*args, **kwargs):
    args = tuple(str(arg) if isinstance(arg, DatetimeIndex) else arg for arg in args)
    kwargs = {k: str(v) if isinstance(v, DatetimeIndex) else v for k, v in kwargs.items()}
    return hashkey(*args, **kwargs)

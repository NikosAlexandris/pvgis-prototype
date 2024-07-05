import zoneinfo
from functools import lru_cache

import numpy as np


@lru_cache(maxsize=None)
def get_timezones():
    return sorted(zoneinfo.available_timezones())


def replace_arrays_with_lists(data):
    if isinstance(data, dict):
        return {k: replace_arrays_with_lists(v) for k, v in data.items()}
    elif isinstance(data, tuple):
        return tuple(replace_arrays_with_lists(v) for v in data)
    elif isinstance(data, list):
        return [replace_arrays_with_lists(v) for v in data]
    elif isinstance(data, np.ndarray):
        return data.tolist()
    else:
        return data

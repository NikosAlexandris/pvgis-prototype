import numpy as np
import hashlib
import orjson


def ndarray_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def generate_hash(output):
    output_str = orjson.dumps(output, default=ndarray_to_list, sort_keys=True)
    hash_object = hashlib.sha256(output_str.encode())
    hash_hex = hash_object.hexdigest()

    return hash_hex

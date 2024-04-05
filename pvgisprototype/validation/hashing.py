import numpy as np
import hashlib
import json


def ndarray_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def generate_hash(output):
    output_str = json.dumps(output, default=ndarray_to_list, sort_keys=True)
    # instead of _dumping_ : do read the file  directly without loading in-memory first !!!
    hash_object = hashlib.sha256(output_str.encode())
    hash_hex = hash_object.hexdigest()

    return hash_hex

import hashlib
import json

import numpy as np


def ndarray_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def generate_hash(output):
    output_str = json.dumps(output, default=ndarray_to_list, sort_keys=True)
    # instead of _dumping_ : do read the file  directly without loading in-memory first !!!
    hash_object = hashlib.sha256(output_str.encode())
    hash_hex = hash_object.hexdigest()


def generate_hash(output, person="PVGIS"):
    hash = hashlib.blake2b(
        digest_size=32,
        # key=b'',
        # salt=b'',
        person=b"{person}",
        # fanout=1,
        # depth=1,
        # leaf_size=0,
        # node_offset=0,
        # node_depth=0,
        # inner_size=0,
        # last_node=False,
        usedforsecurity=False,
    )
    try:
        hash.update(output.tobytes())
    except AttributeError:
        pass
    return hash.hexdigest()

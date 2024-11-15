import hashlib

import numpy as np
import orjson

def ndarray_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


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
    
    # Convert the output to bytes based on its type
    if isinstance(output, np.ndarray):
        # For NumPy arrays, convert to bytes
        output_bytes = output.tobytes()
    elif isinstance(output, list):
        # For lists, first convert to a NumPy array and then to bytes
        output_bytes = np.array(output).tobytes()
    elif isinstance(output, dict):
        # For dictionaries, convert to a JSON string and then to bytes
        output_bytes = orjson.dumps(output).encode('utf-8')
    else:
        output_bytes = b''
    
    hash.update(output_bytes)
    
    return hash.hexdigest()
    

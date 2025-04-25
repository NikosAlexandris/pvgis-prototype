import hashlib
import numpy as np
import orjson


def ndarray_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def generate_hash(output, person=b"PVGIS"):
    hash_object = hashlib.blake2b(
        digest_size=32,
        # key=b'',
        # salt=b'',
        person=person,
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
    if hasattr(output, "__hash__") and callable(output.__hash__):
        # For custom objects, use their __hash__ method
        # Convert the hash to a string and then to bytes
        output_bytes = hash(output)
    elif isinstance(output, np.ndarray):
        # For NumPy arrays, convert to bytes
        output_bytes = output.tobytes()
    elif isinstance(output, list):
        # For lists, first convert to a NumPy array and then to bytes
        output_bytes = np.array(output).tobytes()
    elif isinstance(output, dict):
        output_bytes = orjson.dumps(
            output,
            default=lambda object: object.__dict__,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        )
    else:
        # Error for unsupported types
        raise TypeError(f"Unsupported type for hashing: {type(output)}!")

    hash_object.update(output_bytes)

    return hash_object.hexdigest()

import hashlib
import numpy as np
import orjson


def ndarray_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def generate_hash(data, person=b"PVGIS"):
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

    # Convert the data to bytes based on its type
    if hasattr(data, "__hash__") and callable(data.__hash__):
        # For custom objects, use their __hash__ method
        # Convert the hash to a string and then to bytes
        data_bytes = hash(data)
    elif isinstance(data, np.ndarray):
        # For NumPy arrays, convert to bytes
        data_bytes = data.tobytes()
    elif isinstance(data, list):
        # For lists, first convert to a NumPy array and then to bytes
        data_bytes = np.array(data).tobytes()
    elif isinstance(data, dict):
        # For dictionaries, convert to a JSON string and then to bytes
        data_bytes = orjson.dumps(
            data, 
            default=lambda object: object.__dict__, 
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        )
    else:
        # Error for unsupported types
        raise TypeError(f"Unsupported type for hashing: {type(data)}!")

    hash_object.update(data_bytes)

    return hash_object.hexdigest()

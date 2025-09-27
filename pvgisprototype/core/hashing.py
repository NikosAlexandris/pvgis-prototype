#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
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

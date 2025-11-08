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
from enum import Enum
import hashlib
import numpy as np
import orjson
from pandas import Timestamp, DatetimeIndex, Index
from xarray import DataArray, Dataset
from typing import Any


def ndarray_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def convert_numpy_to_json_serializable(obj: Any) -> Any:
    """
    Convert numpy arrays and other non-serializable objects to JSON-compatible types.
    """
    if isinstance(obj, Enum):
        return str(obj.name)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, set):
        return [convert_numpy_to_json_serializable(item) for item in obj]  # Convert set to list while recursively convert its items
    elif isinstance(obj, dict):
        return {k: convert_numpy_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_to_json_serializable(item) for item in obj]
    else:
        return obj


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
        output_bytes = str(hash(output)).encode("utf-8")
    elif isinstance(output, np.ndarray):
        # For NumPy arrays, convert to bytes
        output_bytes = output.tobytes()
    elif isinstance(output, list):
        # For lists, first convert to a NumPy array and then to bytes
        output_bytes = np.array(output).tobytes()
    elif isinstance(output, dict):
        # For dictionaries, convert to a JSON string and then to bytes
        output_bytes = orjson.dumps(
            output,
            default=lambda object: object.__dict__,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        )
    elif isinstance(output, (DatetimeIndex, Timestamp, Index)):
        output_bytes = str(output).encode("utf-8")
    elif isinstance(output, DataArray | Dataset):
        # For xarray objects, convert to JSON and then to bytes
        output_bytes = orjson.dumps(
            output.to_dict(),
            default=lambda object: object.__dict__,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        )
    else:
        # Error for unsupported types
        raise TypeError(f"Unsupported hashing output type: {type(output)}!")

    hash_object.update(output_bytes)

    return hash_object.hexdigest()

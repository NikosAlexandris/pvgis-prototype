import hashlib
import json


def serialize_for_hash(obj):
    """Serialize objects for cache key generation."""

    if isinstance(obj, dict):
        return {k: serialize_for_hash(v) for k, v in sorted(obj.items())}
    
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_hash(item) for item in obj]
    
    elif hasattr(obj, 'shape'):  # numpy arrays
        return f"array_shape_{obj.shape}_dtype_{obj.dtype}"
    
    # Handle PVGIS-native _series_ objects with .value attribute
    elif hasattr(obj, 'value'):
        val = obj.value
        # Check if value is array-like (has length) or scalar (float, int, etc.)
        if hasattr(val, '__len__'):
            return f"{obj.__class__.__name__}_{len(val)}"
        else:
            # Scalar value (float, int, etc.)
            return f"{obj.__class__.__name__}_{val}"
    
    elif str(type(obj)).startswith('<'):  # enum types
        return str(obj)
    
    else:
        return obj


def generate_compact_cache_key(*args, **kwargs):
    """
    Generate a compact, deterministic cache key using hashing.
    """
    # Create serializable representation
    cache_data = {
        'args': [serialize_for_hash(arg) for arg in args],
        'kwargs': {k: serialize_for_hash(v) for k, v in kwargs.items()}
    }
    
    # Create compact hash
    json_str = json.dumps(cache_data, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]  # 16 char hash

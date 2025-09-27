import hashlib
import json


def generate_compact_cache_key(*args, **kwargs):
    """
    Generate a compact, deterministic cache key using hashing.
    """
    def serialize_for_hash(obj):
        if isinstance(obj, dict):
            return {k: serialize_for_hash(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, (list, tuple)):
            return [serialize_for_hash(item) for item in obj]
        elif hasattr(obj, 'shape'):  # numpy arrays
            return f"array_shape_{obj.shape}_dtype_{obj.dtype}"
        elif hasattr(obj, 'value'):  # Your custom series objects
            return f"{obj.__class__.__name__}_{len(obj.value) if hasattr(obj, 'value') else 'no_value'}"
        elif str(type(obj)).startswith('<'):  # enum types
            return str(obj)
        else:
            return obj
    
    # Create serializable representation
    cache_data = {
        'args': [serialize_for_hash(arg) for arg in args],
        'kwargs': {k: serialize_for_hash(v) for k, v in kwargs.items()}
    }
    
    # Create compact hash
    json_str = json.dumps(cache_data, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]  # 16 char hash

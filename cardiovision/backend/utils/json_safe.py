import numpy as np


def to_json_safe(obj):
    """Convert numpy/scalar types to JSON-serializable Python natives."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {k: to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_json_safe(v) for v in obj]
    if isinstance(obj, (np.floating, np.integer, np.bool_)):
        return obj.item()
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, float):
        return float(obj)
    if isinstance(obj, (int, str, bool)):
        return obj
    return str(obj)

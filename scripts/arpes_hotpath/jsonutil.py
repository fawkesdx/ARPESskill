"""JSON values safe to print. Never expand ndarray payloads into chat."""

import numpy as np


def jsonable(value, *, max_str=200):
    if isinstance(value, dict):
        return {str(k): jsonable(v, max_str=max_str) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v, max_str=max_str) for v in value]
    if isinstance(value, bytes):
        text = value.decode("utf-8", "replace")
        return text if len(text) <= max_str else text[:max_str] + "…"
    if isinstance(value, str):
        return value if len(value) <= max_str else value[:max_str] + "…"
    if isinstance(value, np.generic):
        return jsonable(value.item(), max_str=max_str)
    if isinstance(value, np.ndarray):
        if value.shape == ():
            return jsonable(value.item(), max_str=max_str)
        return {"_ndarray_shape": list(value.shape), "_dtype": str(value.dtype)}
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        return None
    return value

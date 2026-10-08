"""HDF5 attrs and capped partial reads. Not an ARPES reduction backend."""

import json
from pathlib import Path

import h5py
import numpy as np

from arpes_hotpath.jsonutil import jsonable
from arpes_hotpath.policy import PolicyRefusal

MAX_ELEMENTS = 4096
MAX_NODES = 200


def hdf5_list(arguments):
    path = Path(arguments["path"])
    max_nodes = int(arguments.get("max_nodes") or MAX_NODES)
    nodes = []
    with h5py.File(path, "r") as handle:

        def visit(name, obj):
            if len(nodes) >= max_nodes:
                return
            if isinstance(obj, h5py.Dataset):
                nodes.append(
                    {
                        "path": name,
                        "kind": "dataset",
                        "shape": [int(n) for n in obj.shape],
                        "dtype": str(obj.dtype),
                    }
                )
            else:
                nodes.append({"path": name, "kind": "group"})

        visit("/", handle)
        handle.visititems(visit)
    return {"path": str(path), "n": len(nodes), "truncated": len(nodes) >= max_nodes, "nodes": nodes}


def _object(handle, object_path):
    if object_path in (None, "", "/"):
        return handle
    return handle[object_path]


def hdf5_attrs(arguments):
    path = Path(arguments["path"])
    object_path = arguments.get("object_path") or "/"
    with h5py.File(path, "r") as handle:
        obj = _object(handle, object_path)
        attrs = {str(key): jsonable(obj.attrs[key]) for key in obj.attrs}
    return {"path": str(path), "object_path": object_path, "attrs": attrs, "values_read": False}


def hdf5_partial(arguments):
    path = Path(arguments["path"])
    dataset = arguments["dataset"]
    start = list(arguments.get("start") or [])
    count = list(arguments.get("count") or [])
    if not count:
        raise PolicyRefusal("count is required; refusing a full-dataset read")
    if int(np.prod(count)) > MAX_ELEMENTS:
        raise PolicyRefusal(f"partial read capped at {MAX_ELEMENTS} elements")
    with h5py.File(path, "r") as handle:
        obj = handle[dataset]
        if len(start) != obj.ndim or len(count) != obj.ndim:
            raise PolicyRefusal("start and count must match dataset rank")
        slices = tuple(slice(int(s), int(s) + int(c)) for s, c in zip(start, count))
        values = np.asarray(obj[slices])
    return {
        "path": str(path),
        "dataset": dataset,
        "shape": list(values.shape),
        "values": jsonable(values.tolist()) if values.size else [],
        "capped": True,
    }


TOOL_SPECS = [
    {
        "name": "hdf5_list",
        "description": "Dataset and group names with shapes. No values.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "max_nodes": {"type": "integer"},
            },
            "required": ["path"],
        },
        "handler": hdf5_list,
    },
    {
        "name": "hdf5_attrs",
        "description": "Attributes on one HDF5 object. No dataset values.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "object_path": {"type": "string"},
            },
            "required": ["path"],
        },
        "handler": hdf5_attrs,
    },
    {
        "name": "hdf5_partial",
        "description": "Explicit hyperslab only, capped at 4096 elements.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "dataset": {"type": "string"},
                "start": {"type": "array", "items": {"type": "integer"}},
                "count": {"type": "array", "items": {"type": "integer"}},
            },
            "required": ["path", "dataset", "count"],
        },
        "handler": hdf5_partial,
    },
]

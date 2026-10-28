"""CLIO HDF5 side server: attrs and a capped slice. No reduction."""

import sys
from pathlib import Path

import h5py
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mcp_clio_hdf5"))

from arpes_hotpath.policy import PolicyRefusal
from tools import hdf5_attrs, hdf5_list, hdf5_partial


def test_attrs_and_partial_cap(tmp_path):
    path = tmp_path / "cube.h5"
    with h5py.File(path, "w") as handle:
        handle.attrs["sample"] = "demo"
        handle.create_dataset("spectrum", data=np.arange(100).reshape(10, 10))
    listed = hdf5_list({"path": str(path)})
    assert listed["nodes"][0]["kind"] == "group"
    datasets = [node for node in listed["nodes"] if node["kind"] == "dataset"]
    assert datasets[0]["shape"] == [10, 10]
    attrs = hdf5_attrs({"path": str(path), "object_path": "/"})
    assert attrs["attrs"]["sample"] == "demo"
    assert attrs["values_read"] is False
    partial = hdf5_partial(
        {"path": str(path), "dataset": "spectrum", "start": [0, 0], "count": [2, 2]}
    )
    assert partial["values"] == [[0, 1], [10, 11]]
    with pytest.raises(PolicyRefusal):
        hdf5_partial(
            {"path": str(path), "dataset": "spectrum", "start": [0, 0], "count": [64, 65]}
        )
    with pytest.raises(PolicyRefusal):
        hdf5_partial({"path": str(path), "dataset": "spectrum", "count": []})

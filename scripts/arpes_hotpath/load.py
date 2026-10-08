"""Load one spectrum for QC / overview / fit / k. No custom beamline parser."""

from pathlib import Path

import xarray as xr

from arpes_hotpath.policy import PolicyRefusal


def pick_dataarray(obj):
    if isinstance(obj, xr.DataArray):
        return obj, obj.name
    if isinstance(obj, xr.Dataset):
        candidates = []
        for name, da in obj.data_vars.items():
            folded = str(name).casefold()
            if "num_" in folded or folded.startswith("num"):
                continue
            candidates.append((str(name), da))
        if not candidates:
            raise PolicyRefusal("no intensity data variable after skipping counters")
        name, da = max(candidates, key=lambda item: int(item[1].size))
        da = da.copy()
        da.attrs["picked_variable"] = name
        return da, name
    raise PolicyRefusal(
        f"loader returned {type(obj).__name__}; no NxsScan↔xarray bridge in this script"
    )


def load_inspect_nc(path):
    path = Path(path)
    if path.suffix.lower() != ".nc":
        raise PolicyRefusal(
            "inspect-only full load in this script accepts .nc with coords already stored. "
            "HDF5/FITS cubes stay on a package loader or header peek — no axis names from layout."
        )
    ds = xr.open_dataset(path)
    da, name = pick_dataarray(ds.load())
    return da, name


def load_spectrum(path, *, backend, allow_inspect=False, location=None):
    """Return (DataArray, backend, picked_variable)."""
    path = Path(path)
    if not path.is_file():
        raise PolicyRefusal(f"file not found: {path}")
    if backend == "inspect-only":
        if not allow_inspect:
            raise PolicyRefusal(
                "inspect-only needs --allow-inspect after the user declines the package env"
            )
        da, name = load_inspect_nc(path)
        return da, "inspect-only", name
    if backend == "pyarpes":
        try:
            from arpes.io import load_data
        except ImportError as exc:
            raise PolicyRefusal(
                f"import arpes failed ({exc}). Ask for the Python 3.8 env. "
                "No silent xarray fallback."
            ) from exc
        kwargs = {}
        if location:
            kwargs["location"] = location
        loaded = load_data(str(path), **kwargs)
        da, name = pick_dataarray(loaded)
        return da, "pyarpes", name
    if backend == "arpes_viewer":
        try:
            from loader.registry import load as viewer_load
        except ImportError as exc:
            raise PolicyRefusal(
                f"import loader failed ({exc}). Ask for the ARPES-data-browser env. "
                "No silent fallback."
            ) from exc
        loaded = viewer_load(str(path))
        if not isinstance(loaded, (xr.DataArray, xr.Dataset)):
            raise PolicyRefusal(
                "arpes_viewer returned a non-xarray scan. Use viewer tools for that object. "
                "This script will not bridge NxsScan to xarray."
            )
        da, name = pick_dataarray(loaded)
        return da, "arpes_viewer", name
    raise PolicyRefusal(
        f"unknown backend {backend!r}; use pyarpes, arpes_viewer, or inspect-only"
    )

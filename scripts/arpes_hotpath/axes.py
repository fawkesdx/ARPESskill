"""Axis QC. Read coords and attrs. Do not rename or swap conventions."""

import numpy as np

ENERGY_NAMES = frozenset(
    {"ev", "binding", "kinetic", "energy", "binding_energy", "kinetic_energy"}
)
ANGLE_NAMES = frozenset(
    {
        "phi",
        "psi",
        "theta",
        "beta",
        "chi",
        "alpha",
        "pixel",
        "slit_defl",
        "slitdefl",
    }
)
SCAN_NAMES = frozenset({"psi", "theta", "beta", "chi", "alpha", "slit_defl", "slitdefl"})
DETECTOR_NAMES = frozenset({"phi", "pixel"})
MOMENTUM_NAMES = frozenset({"kx", "ky", "kz", "kp", "k"})
HV_NAMES = frozenset({"hv", "photon_energy", "mono_ev"})
SPATIAL_NAMES = frozenset({"x", "y"})

ENERGY_LABELS = frozenset({"Ek", "Eb", "E-EF", "ambiguous"})


def _fold(name):
    return str(name).casefold().replace(" ", "_")


def units_of(da, name):
    if name in getattr(da, "coords", {}):
        units = da.coords[name].attrs.get("units")
        if units not in (None, ""):
            return str(units)
    direct = da.attrs.get(f"{name}_units")
    if direct not in (None, ""):
        return str(direct)
    return ""


def _degrees(units):
    folded = units.casefold().replace(" ", "")
    return "deg" in folded or "degree" in folded or "°" in units


def _inv_angstrom(units):
    folded = units.casefold().replace(" ", "")
    tokens = ("angstrom", "ång", "å", "a^-1", "a−1", "a-1", "1/å", "1/a", "inv_ang")
    return any(token in folded for token in tokens)


def find_dim(da, names):
    for dim in da.dims:
        if _fold(dim) in names:
            return dim
    return None


def find_dims(da, names):
    return [dim for dim in da.dims if _fold(dim) in names]


def coord_range(da, name):
    if name not in da.coords:
        return None
    values = np.asarray(da.coords[name].values, dtype=float)
    if values.size == 0 or np.all(~np.isfinite(values)):
        return None
    finite = values[np.isfinite(values)]
    return float(np.min(finite)), float(np.max(finite))


def classify_energy(da, energy_dim):
    """Clue-based label. Attr wins. Range alone never promotes Ek."""
    if energy_dim is None:
        return {
            "dim": None,
            "label": "ambiguous",
            "claimed": False,
            "source": "no_energy_dim",
            "clues": [],
            "range_eV": None,
        }
    span = coord_range(da, energy_dim)
    clues = []
    attr = da.attrs.get("energy_convention")
    if isinstance(attr, str) and attr in ENERGY_LABELS:
        return {
            "dim": energy_dim,
            "label": attr,
            "claimed": attr != "ambiguous",
            "source": "attr:energy_convention",
            "clues": ["attr"],
            "range_eV": list(span) if span else None,
        }
    folded = _fold(energy_dim)
    units = units_of(da, energy_dim).casefold()
    if "kinetic" in folded or "kinetic" in units:
        label, source = "Ek", "name_or_units"
    elif "binding" in folded or "binding" in units:
        label, source = "Eb", "name_or_units"
    else:
        label, source = "ambiguous", "insufficient_clues"
        if span is not None:
            lo, hi = span
            if lo < 0 <= hi:
                label, source = "E-EF", "range_clue"
                clues.append("0_in_range_and_negative_values")
            elif lo > 1 and hi > 10:
                clues.append("range_much_greater_than_0_not_sufficient")
    return {
        "dim": energy_dim,
        "label": label,
        "claimed": label != "ambiguous",
        "source": source,
        "clues": clues,
        "range_eV": list(span) if span else None,
    }


def angle_as_k_flags(da):
    """Momentum-looking names are not Å⁻¹ without package provenance."""
    provenance = da.attrs.get("kspace_provenance")
    provenance_ok = isinstance(provenance, str) and provenance.strip() != ""
    flags = []
    for dim in da.dims:
        if _fold(dim) not in MOMENTUM_NAMES:
            continue
        units = units_of(da, dim)
        degree_units = _degrees(units)
        inverse = _inv_angstrom(units)
        if provenance_ok and inverse and not degree_units:
            continue
        reason = (
            "dim name looks like momentum; degrees in units"
            if degree_units
            else "dim name looks like momentum; no convert_to_kspace provenance"
        )
        flags.append(
            {
                "dim": dim,
                "units": units or None,
                "angle_as_k": True,
                "treat_as": "not_momentum",
                "reason": reason,
            }
        )
    return flags, (provenance if provenance_ok else None)


def axes_report(da, *, source_path, backend, picked_variable=None):
    energy_dim = find_dim(da, ENERGY_NAMES)
    energy = classify_energy(da, energy_dim)
    flags, provenance = angle_as_k_flags(da)
    coords = {}
    for name in da.dims:
        span = coord_range(da, name)
        coords[name] = {
            "size": int(da.sizes[name]),
            "min": None if span is None else span[0],
            "max": None if span is None else span[1],
            "units": units_of(da, name) or None,
        }
    mid = None
    if energy_dim is not None and da.sizes.get(energy_dim, 0) > 0:
        sl = da.isel({energy_dim: int(da.sizes[energy_dim]) // 2})
        values = np.asarray(sl.values, dtype=float)
        finite = values[np.isfinite(values)]
        if finite.size:
            mid = {
                "dim": energy_dim,
                "index": int(da.sizes[energy_dim]) // 2,
                "min": float(np.min(finite)),
                "max": float(np.max(finite)),
                "mean": float(np.mean(finite)),
            }
    attr_keys = list(da.attrs)[:8]
    return {
        "backend": backend,
        "path": None if source_path is None else str(source_path),
        "picked_variable": picked_variable or da.attrs.get("picked_variable"),
        "shape": [int(da.sizes[d]) for d in da.dims],
        "dims": list(da.dims),
        "coords": coords,
        "energy": energy,
        "angle_as_k": flags,
        "report_momentum": False if flags or not provenance else True,
        "kspace_provenance": provenance,
        "mid_summary": mid,
        "attrs_sample": {k: da.attrs[k] for k in attr_keys},
        "empty_daq": bool(np.all(np.asarray(da.values) == 0)),
    }
